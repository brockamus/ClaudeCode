import { Campaign, Lead, LeadWithMessage, CampaignFilters, MessageVariant } from '../shared/types';
import { getConnection, getActiveCampaign, setActiveCampaign, getLeadQueue, setLeadQueue, incrementDmsToday, getCampaignPhase, setCampaignPhase, getAccountHealth, recordAction, getCampaignQueue, removeFromCampaignQueue, addToCampaignQueue } from '../shared/storage';
import { sendToContentScript } from '../shared/messaging';
import { api } from '../shared/api';
import { canSendDM, getDelayMs, shouldTakeBreak, getBreakDurationMs } from './rate-limiter';
import { humanDelay } from '../lib/human-delay';
import { getNextSendDelay } from '../lib/pacing';

let isRunning = false;
let currentTabId: number | null = null;

// Resume incomplete campaigns on service worker startup
resumeCampaignIfNeeded();

async function resumeCampaignIfNeeded(): Promise<void> {
  const campaign = await getActiveCampaign();
  const progress = await getCampaignPhase();

  if (!campaign || !progress || !progress.phase) return;
  if (progress.phase === 'completed') return;

  console.log(`[Konversly] Resuming campaign "${campaign.name}" from phase: ${progress.phase}`);

  // For sending phase: we have a lead queue with pending items — just resume autopilot
  if (progress.phase === 'sending') {
    const queue = await getLeadQueue();
    const hasPending = queue.some(l => l.status === 'pending');
    if (!hasPending) {
      await setCampaignPhase({ phase: 'completed' });
      return;
    }

    isRunning = true;

    // Open a fresh Instagram tab for sending
    const tab = await chrome.tabs.create({
      url: 'https://www.instagram.com/',
      active: false,
    });
    currentTabId = tab.id || null;
    await humanDelay(3000, 5000);

    if (campaign.send_mode === 'autopilot') {
      await processAutopilot(campaign);
    }
    // In review mode, leads are already in queue — user approves via options page
    return;
  }

  // For earlier phases (scraping/enriching/generating), restart from the beginning
  // since we can't reliably resume DOM-dependent operations
  console.log(`[Konversly] Phase "${progress.phase}" cannot be resumed mid-way. Restart the campaign.`);
  await setCampaignPhase(null);
}

// Campaign scheduler: check every 5 minutes for due scheduled campaigns
chrome.alarms.create('check-scheduled-campaigns', { periodInMinutes: 5 });
chrome.alarms.onAlarm.addListener(async (alarm) => {
  if (alarm.name !== 'check-scheduled-campaigns') return;
  if (isRunning) return; // Don't start a new campaign while one is running

  const queue = await getCampaignQueue();
  const now = Date.now();

  for (const entry of queue) {
    if (new Date(entry.scheduled_at).getTime() <= now) {
      console.log(`[Konversly] Starting scheduled campaign: ${entry.campaign.name}`);
      await removeFromCampaignQueue(entry.campaign.id);
      startCampaign(entry.campaign);
      break; // Only start one at a time
    }
  }
});

// Listen for messages from popup/options/content scripts
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  switch (message.type) {
    case 'GET_STATUS':
      getActiveCampaign().then(campaign => {
        sendResponse({ isRunning, campaign });
      });
      return true;

    case 'START_CAMPAIGN':
      startCampaign(message.campaign).then(() => sendResponse({ ok: true }));
      return true;

    case 'PAUSE_CAMPAIGN':
      isRunning = false;
      sendResponse({ ok: true });
      return;

    case 'STOP_CAMPAIGN':
      isRunning = false;
      setActiveCampaign(null);
      setLeadQueue([]);
      setCampaignPhase(null);
      sendResponse({ ok: true });
      return;

    case 'APPROVE_LEAD':
      approveLead(message.handle).then(() => sendResponse({ ok: true }));
      return true;

    case 'SKIP_LEAD':
      skipLead(message.handle).then(() => sendResponse({ ok: true }));
      return true;

    case 'REGENERATE_DM':
      regenerateDM(message.handle).then(() => sendResponse({ ok: true }));
      return true;

    case 'SCHEDULE_CAMPAIGN':
      addToCampaignQueue({ campaign: message.campaign, scheduled_at: message.scheduled_at })
        .then(() => sendResponse({ ok: true }));
      return true;

    case 'GET_HEALTH':
      getAccountHealth().then(health => sendResponse(health));
      return true;
  }
});

async function startCampaign(campaign: Campaign): Promise<void> {
  isRunning = true;
  await setActiveCampaign(campaign);

  // Step 1: Navigate to target account's followers page
  const tab = await chrome.tabs.create({
    url: `https://www.instagram.com/${campaign.target_account}/followers/`,
    active: true,
  });
  currentTabId = tab.id || null;

  // Wait for page to load
  await humanDelay(3000, 5000);

  if (!currentTabId || !isRunning) return;

  // Step 2: Scrape followers
  await setCampaignPhase({ phase: 'scraping' });
  await api.updateCampaign(campaign.id, { status: 'scraping' });

  const maxLeads = 500;
  const scrapeResult = await sendToContentScript(currentTabId, {
    type: 'START_SCRAPING',
    target_account: campaign.target_account,
    max_leads: maxLeads,
  }) as { leads: Lead[] } | undefined;

  const rawLeads = scrapeResult?.leads || [];
  await api.updateCampaign(campaign.id, { leads_scraped: rawLeads.length });

  // Step 3: Enrich each profile
  const enrichedLeads: Lead[] = [];
  for (const lead of rawLeads) {
    if (!isRunning) break;

    // Navigate to profile
    await chrome.tabs.update(currentTabId, {
      url: `https://www.instagram.com/${lead.instagram_handle}/`,
    });
    await humanDelay(3000, 8000);

    if (!currentTabId) break;

    const result = await sendToContentScript(currentTabId, {
      type: 'ENRICH_PROFILE',
      username: lead.instagram_handle,
    }) as { lead: Lead } | undefined;

    if (result?.lead) {
      enrichedLeads.push(result.lead);
    }
  }

  // Step 4: Filter leads
  const filteredLeads = filterLeads(enrichedLeads, campaign.filters);

  // Step 4b: Dedup — remove leads we've already contacted
  const conn = await getConnection();
  if (!conn) return;

  let dedupedLeads = filteredLeads;
  try {
    const { handles: contactedHandles } = await api.getContactedHandles(conn.account_id);
    const contactedSet = new Set(contactedHandles.map(h => h.toLowerCase()));
    dedupedLeads = filteredLeads.filter(l => !contactedSet.has(l.instagram_handle.toLowerCase()));
    const dupsRemoved = filteredLeads.length - dedupedLeads.length;
    if (dupsRemoved > 0) {
      console.log(`[Konversly] Dedup: removed ${dupsRemoved} previously contacted leads`);
    }
  } catch (err) {
    console.error('[Konversly] Dedup check failed, proceeding without dedup', err);
  }

  await api.updateCampaign(campaign.id, { leads_filtered: dedupedLeads.length });
  await setCampaignPhase({ phase: 'generating' });

  // Step 5: Generate DMs for each lead

  const leadQueue: LeadWithMessage[] = [];
  for (const lead of dedupedLeads) {
    if (!isRunning) break;

    try {
      // Select variant or use campaign prompt
      const variant = selectVariant(campaign.variants);
      const promptInstruction = variant?.prompt_instruction || campaign.prompt_instruction;

      const result = await api.generateDM(
        conn.account_id,
        campaign.id,
        lead,
        promptInstruction
      );

      leadQueue.push({
        ...lead,
        generated_message: result.message,
        variant_name: variant?.name,
        status: 'pending',
        campaign_id: campaign.id,
      });
    } catch (err) {
      console.error('Failed to generate DM for', lead.instagram_handle, err);
    }
  }

  await setLeadQueue(leadQueue);
  await setCampaignPhase({ phase: 'sending' });
  await api.updateCampaign(campaign.id, { status: 'running' });

  // Step 6: Process send queue
  if (campaign.send_mode === 'autopilot') {
    // In autopilot, auto-approve after threshold
    await processAutopilot(campaign);
  }
  // In review mode, leads stay in queue for user to approve via options page
}

function filterLeads(leads: Lead[], filters: CampaignFilters): Lead[] {
  return leads.filter(lead => {
    if (lead.is_private) return false;
    if (lead.follower_count < filters.follower_min) return false;
    if (lead.follower_count > filters.follower_max) return false;

    if (filters.bio_keywords_include.length > 0) {
      const bioLower = lead.bio.toLowerCase();
      const hasKeyword = filters.bio_keywords_include.some(kw => bioLower.includes(kw.toLowerCase()));
      if (!hasKeyword) return false;
    }

    if (filters.bio_keywords_exclude.length > 0) {
      const bioLower = lead.bio.toLowerCase();
      const hasExcluded = filters.bio_keywords_exclude.some(kw => bioLower.includes(kw.toLowerCase()));
      if (hasExcluded) return false;
    }

    if (filters.account_types.length > 0 && lead.account_type !== 'unknown') {
      if (!filters.account_types.includes(lead.account_type)) return false;
    }

    return true;
  });
}

async function processAutopilot(campaign: Campaign): Promise<void> {
  let dmsSinceBreak = 0;

  while (isRunning) {
    const queue = await getLeadQueue();
    const pendingIndex = queue.findIndex(l => l.status === 'pending');
    if (pendingIndex === -1) break; // All done

    const lead = queue[pendingIndex];

    // Check rate limits (with working hours + daily target awareness)
    const rateCheck = await canSendDM(campaign.rate_limits, campaign);
    if (!rateCheck.allowed) {
      if (rateCheck.reason === 'daily_limit') break;
      if (rateCheck.reason === 'quiet_hours' || rateCheck.reason === 'outside_working_hours') {
        await humanDelay(60000, 120000); // Wait 1-2 min and recheck
        continue;
      }
    }

    // Check if we need a break
    if (shouldTakeBreak(dmsSinceBreak, campaign.rate_limits)) {
      const breakMs = getBreakDurationMs(campaign.rate_limits);
      await new Promise(r => setTimeout(r, breakMs));
      dmsSinceBreak = 0;
    }

    // If under autopilot threshold, skip (user must approve manually)
    if (campaign.dms_approved < campaign.autopilot_threshold) {
      await humanDelay(5000, 10000);
      continue;
    }

    // Send the DM (with warmup if enabled)
    await sendLeadDM(lead, campaign);
    dmsSinceBreak++;

    // Use pacing algorithm if enabled, otherwise fall back to fixed delay
    if (campaign.pacing_enabled) {
      const pacingDelay = await getNextSendDelay(campaign);
      if (pacingDelay === -1) break; // Daily target reached
      await new Promise(r => setTimeout(r, pacingDelay));
    } else {
      const delay = getDelayMs(campaign.rate_limits);
      await new Promise(r => setTimeout(r, delay));
    }
  }
}

async function sendLeadDM(lead: LeadWithMessage, campaign: Campaign): Promise<void> {
  if (!currentTabId) return;

  // Engagement warmup: navigate to profile first for follow/like actions
  if (campaign.warmup_follow || campaign.warmup_like_post || campaign.warmup_like_story) {
    await chrome.tabs.update(currentTabId, {
      url: `https://www.instagram.com/${lead.instagram_handle}/`,
    });
    await humanDelay(2000, 4000);

    if (campaign.warmup_follow && currentTabId) {
      await sendToContentScript(currentTabId, { type: 'FOLLOW_USER', username: lead.instagram_handle });
      await humanDelay(2000, 5000);
    }

    if (campaign.warmup_like_post && currentTabId) {
      await sendToContentScript(currentTabId, { type: 'LIKE_POST', username: lead.instagram_handle });
      await humanDelay(2000, 5000);
    }

    if (campaign.warmup_like_story && currentTabId) {
      await sendToContentScript(currentTabId, { type: 'LIKE_STORY', username: lead.instagram_handle });
      await humanDelay(3000, 8000);
    }
  }

  // Navigate to DM page for this user
  await chrome.tabs.update(currentTabId, {
    url: `https://www.instagram.com/direct/new/`,
  });
  await humanDelay(2000, 4000);

  // TODO: Need to search for user in the "new message" dialog
  // For now, navigate to their profile and use the Message button
  await chrome.tabs.update(currentTabId, {
    url: `https://www.instagram.com/${lead.instagram_handle}/`,
  });
  await humanDelay(2000, 4000);

  if (!currentTabId) return;

  const result = await sendToContentScript(currentTabId, {
    type: 'SEND_DM',
    username: lead.instagram_handle,
    message: lead.generated_message,
  }) as { success: boolean } | undefined;

  // Update queue by handle (safe against index shifts from concurrent mutations)
  const queue = await getLeadQueue();
  const queueIdx = queue.findIndex(l => l.instagram_handle === lead.instagram_handle);
  if (queueIdx === -1) return;

  if (result?.success) {
    queue[queueIdx].status = 'sent';
    await incrementDmsToday();
    await recordAction(true);

    // Sync to Konversly
    const conn = await getConnection();
    if (conn) {
      try {
        await api.syncContact({
          account_id: conn.account_id,
          ghl_location_id: conn.ghl_location_id,
          campaign_id: campaign.id,
          instagram_handle: lead.instagram_handle,
          contact_name: lead.display_name || lead.instagram_handle,
          instagram_bio: lead.bio,
          instagram_followers: lead.follower_count,
          profile_photo_url: lead.profile_pic_url,
          channel_type: 'instagram',
          first_dm_content: lead.generated_message,
          variant_name: lead.variant_name || null,
        });
      } catch (err) {
        console.error('Failed to sync contact', err);
      }
    }
  } else {
    queue[queueIdx].status = 'failed';
    await recordAction(false);

    // Auto-pause if too many consecutive failures (likely action blocked)
    const health = await getAccountHealth();
    if (health.consecutive_failures >= 3) {
      console.warn(`[Konversly] ${health.consecutive_failures} consecutive failures — auto-pausing campaign (possible action block)`);
      isRunning = false;
    }
  }

  await setLeadQueue(queue);
}

async function approveLead(handle: string): Promise<void> {
  const queue = await getLeadQueue();
  const lead = queue.find(l => l.instagram_handle === handle);
  const campaign = await getActiveCampaign();
  if (!lead || !campaign) return;

  await sendLeadDM(lead, campaign);

  // Re-read campaign to get fresh counts, then increment
  const freshCampaign = await getActiveCampaign();
  if (freshCampaign) {
    freshCampaign.dms_approved++;
    freshCampaign.dms_sent++;
    await setActiveCampaign(freshCampaign);
    await api.updateCampaign(freshCampaign.id, { dms_approved: freshCampaign.dms_approved, dms_sent: freshCampaign.dms_sent });
  }
}

async function skipLead(handle: string): Promise<void> {
  const queue = await getLeadQueue();
  const idx = queue.findIndex(l => l.instagram_handle === handle);
  if (idx !== -1) {
    queue[idx].status = 'skipped';
    await setLeadQueue(queue);
  }
}

async function regenerateDM(handle: string): Promise<void> {
  const queue = await getLeadQueue();
  const idx = queue.findIndex(l => l.instagram_handle === handle);
  const campaign = await getActiveCampaign();
  const conn = await getConnection();
  if (idx === -1 || !campaign || !conn) return;

  try {
    const variant = selectVariant(campaign.variants);
    const promptInstruction = variant?.prompt_instruction || campaign.prompt_instruction;
    const result = await api.generateDM(conn.account_id, campaign.id, queue[idx], promptInstruction);
    queue[idx].generated_message = result.message;
    queue[idx].variant_name = variant?.name;
    await setLeadQueue(queue);
  } catch (err) {
    console.error('Failed to regenerate DM', err);
  }
}

// Weighted random variant selection
function selectVariant(variants: MessageVariant[]): MessageVariant | null {
  if (!variants || variants.length === 0) return null;

  const totalWeight = variants.reduce((sum, v) => sum + v.weight, 0);
  if (totalWeight <= 0) return variants[0];

  let roll = Math.random() * totalWeight;
  for (const variant of variants) {
    roll -= variant.weight;
    if (roll <= 0) return variant;
  }
  return variants[variants.length - 1];
}
