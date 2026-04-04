import { Campaign, Lead, LeadWithMessage, CampaignFilters } from '../shared/types';
import { getConnection, getActiveCampaign, setActiveCampaign, getLeadQueue, setLeadQueue, incrementDmsToday } from '../shared/storage';
import { sendToContentScript } from '../shared/messaging';
import { api } from '../shared/api';
import { canSendDM, getDelayMs, shouldTakeBreak, getBreakDurationMs } from './rate-limiter';
import { humanDelay } from '../lib/human-delay';

let isRunning = false;
let currentTabId: number | null = null;

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
      sendResponse({ ok: true });
      return;

    case 'APPROVE_LEAD':
      approveLead(message.index).then(() => sendResponse({ ok: true }));
      return true;

    case 'SKIP_LEAD':
      skipLead(message.index).then(() => sendResponse({ ok: true }));
      return true;

    case 'REGENERATE_DM':
      regenerateDM(message.index).then(() => sendResponse({ ok: true }));
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
  await api.updateCampaign(campaign.id, { leads_filtered: filteredLeads.length });

  // Step 5: Generate DMs for each lead
  const conn = await getConnection();
  if (!conn) return;

  const leadQueue: LeadWithMessage[] = [];
  for (const lead of filteredLeads) {
    if (!isRunning) break;

    try {
      const result = await api.generateDM(
        conn.account_id,
        campaign.id,
        lead,
        campaign.prompt_instruction
      );

      leadQueue.push({
        ...lead,
        generated_message: result.message,
        status: 'pending',
        campaign_id: campaign.id,
      });
    } catch (err) {
      console.error('Failed to generate DM for', lead.instagram_handle, err);
    }
  }

  await setLeadQueue(leadQueue);
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

    // Check rate limits
    const rateCheck = await canSendDM(campaign.rate_limits);
    if (!rateCheck.allowed) {
      if (rateCheck.reason === 'daily_limit') break;
      if (rateCheck.reason === 'quiet_hours') {
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

    // Send the DM
    await sendLeadDM(lead, pendingIndex, campaign);
    dmsSinceBreak++;

    // Delay before next DM
    const delay = getDelayMs(campaign.rate_limits);
    await new Promise(r => setTimeout(r, delay));
  }
}

async function sendLeadDM(lead: LeadWithMessage, index: number, campaign: Campaign): Promise<void> {
  if (!currentTabId) return;

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

  const queue = await getLeadQueue();
  if (result?.success) {
    queue[index].status = 'sent';
    await incrementDmsToday();

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
        });
      } catch (err) {
        console.error('Failed to sync contact', err);
      }
    }
  } else {
    queue[index].status = 'failed';
  }

  await setLeadQueue(queue);
}

async function approveLead(index: number): Promise<void> {
  const queue = await getLeadQueue();
  const campaign = await getActiveCampaign();
  if (!queue[index] || !campaign) return;

  await sendLeadDM(queue[index], index, campaign);

  // Update approved count
  campaign.dms_approved++;
  await setActiveCampaign(campaign);
  await api.updateCampaign(campaign.id, { dms_approved: campaign.dms_approved, dms_sent: campaign.dms_sent + 1 });
}

async function skipLead(index: number): Promise<void> {
  const queue = await getLeadQueue();
  if (queue[index]) {
    queue[index].status = 'skipped';
    await setLeadQueue(queue);
  }
}

async function regenerateDM(index: number): Promise<void> {
  const queue = await getLeadQueue();
  const campaign = await getActiveCampaign();
  const conn = await getConnection();
  if (!queue[index] || !campaign || !conn) return;

  try {
    const result = await api.generateDM(conn.account_id, campaign.id, queue[index], campaign.prompt_instruction);
    queue[index].generated_message = result.message;
    await setLeadQueue(queue);
  } catch (err) {
    console.error('Failed to regenerate DM', err);
  }
}
