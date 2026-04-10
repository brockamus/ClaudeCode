import { ConnectionConfig, Campaign, LeadWithMessage } from './types';

const KEYS = {
  CONNECTION: 'konversly_connection',
  ACTIVE_CAMPAIGN: 'konversly_active_campaign',
  LEAD_QUEUE: 'konversly_lead_queue',
  DMS_TODAY: 'konversly_dms_today',
  DMS_TODAY_DATE: 'konversly_dms_today_date',
  DAILY_TARGET: 'konversly_daily_target',
  CAMPAIGN_PHASE: 'konversly_campaign_phase',
  ACCOUNT_HEALTH: 'konversly_account_health',
  CAMPAIGN_QUEUE: 'konversly_campaign_queue',
} as const;

export async function getConnection(): Promise<ConnectionConfig | null> {
  const result = await chrome.storage.local.get(KEYS.CONNECTION);
  return result[KEYS.CONNECTION] || null;
}

export async function setConnection(config: ConnectionConfig): Promise<void> {
  await chrome.storage.local.set({ [KEYS.CONNECTION]: config });
}

export async function getActiveCampaign(): Promise<Campaign | null> {
  const result = await chrome.storage.local.get(KEYS.ACTIVE_CAMPAIGN);
  return result[KEYS.ACTIVE_CAMPAIGN] || null;
}

export async function setActiveCampaign(campaign: Campaign | null): Promise<void> {
  await chrome.storage.local.set({ [KEYS.ACTIVE_CAMPAIGN]: campaign });
}

export async function getLeadQueue(): Promise<LeadWithMessage[]> {
  const result = await chrome.storage.local.get(KEYS.LEAD_QUEUE);
  return result[KEYS.LEAD_QUEUE] || [];
}

export async function setLeadQueue(leads: LeadWithMessage[]): Promise<void> {
  await chrome.storage.local.set({ [KEYS.LEAD_QUEUE]: leads });
}

export async function getDmsToday(): Promise<number> {
  const result = await chrome.storage.local.get([KEYS.DMS_TODAY, KEYS.DMS_TODAY_DATE]);
  const today = new Date().toDateString();
  if (result[KEYS.DMS_TODAY_DATE] !== today) {
    await chrome.storage.local.set({ [KEYS.DMS_TODAY]: 0, [KEYS.DMS_TODAY_DATE]: today });
    return 0;
  }
  return result[KEYS.DMS_TODAY] || 0;
}

export async function incrementDmsToday(): Promise<number> {
  const current = await getDmsToday();
  const newCount = current + 1;
  await chrome.storage.local.set({ [KEYS.DMS_TODAY]: newCount, [KEYS.DMS_TODAY_DATE]: new Date().toDateString() });
  return newCount;
}

export interface DailyTarget {
  date: string;
  target: number;
}

export async function getDailyTarget(): Promise<DailyTarget | null> {
  const result = await chrome.storage.local.get(KEYS.DAILY_TARGET);
  return result[KEYS.DAILY_TARGET] || null;
}

export async function setDailyTarget(target: DailyTarget): Promise<void> {
  await chrome.storage.local.set({ [KEYS.DAILY_TARGET]: target });
}

// Campaign phase tracking for resume after restart
export type CampaignPhase = 'scraping' | 'enriching' | 'filtering' | 'generating' | 'sending' | 'completed' | null;

export interface CampaignProgress {
  phase: CampaignPhase;
  enrichedLeads?: string; // JSON serialized — chrome.storage has size limits per key
  filteredLeads?: string;
}

export async function getCampaignPhase(): Promise<CampaignProgress | null> {
  const result = await chrome.storage.local.get(KEYS.CAMPAIGN_PHASE);
  return result[KEYS.CAMPAIGN_PHASE] || null;
}

export async function setCampaignPhase(progress: CampaignProgress | null): Promise<void> {
  await chrome.storage.local.set({ [KEYS.CAMPAIGN_PHASE]: progress });
}

// Account health monitoring
export interface AccountHealth {
  consecutive_failures: number;
  total_successes_today: number;
  total_failures_today: number;
  last_failure_at: string | null;
  status: 'healthy' | 'warning' | 'blocked';
  date: string;
}

const DEFAULT_HEALTH: AccountHealth = {
  consecutive_failures: 0,
  total_successes_today: 0,
  total_failures_today: 0,
  last_failure_at: null,
  status: 'healthy',
  date: new Date().toDateString(),
};

export async function getAccountHealth(): Promise<AccountHealth> {
  const result = await chrome.storage.local.get(KEYS.ACCOUNT_HEALTH);
  const health = result[KEYS.ACCOUNT_HEALTH] as AccountHealth | undefined;
  const today = new Date().toDateString();

  // Reset daily counters
  if (!health || health.date !== today) {
    const fresh = { ...DEFAULT_HEALTH, date: today };
    await chrome.storage.local.set({ [KEYS.ACCOUNT_HEALTH]: fresh });
    return fresh;
  }
  return health;
}

export async function recordAction(success: boolean): Promise<AccountHealth> {
  const health = await getAccountHealth();

  if (success) {
    health.consecutive_failures = 0;
    health.total_successes_today++;
    health.status = 'healthy';
  } else {
    health.consecutive_failures++;
    health.total_failures_today++;
    health.last_failure_at = new Date().toISOString();
    health.status = health.consecutive_failures >= 5 ? 'blocked' : health.consecutive_failures >= 3 ? 'warning' : 'healthy';
  }

  await chrome.storage.local.set({ [KEYS.ACCOUNT_HEALTH]: health });
  return health;
}

// Campaign queue for scheduling
export interface ScheduledCampaign {
  campaign: Campaign;
  scheduled_at: string; // ISO date string
}

export async function getCampaignQueue(): Promise<ScheduledCampaign[]> {
  const result = await chrome.storage.local.get(KEYS.CAMPAIGN_QUEUE);
  return result[KEYS.CAMPAIGN_QUEUE] || [];
}

export async function setCampaignQueue(queue: ScheduledCampaign[]): Promise<void> {
  await chrome.storage.local.set({ [KEYS.CAMPAIGN_QUEUE]: queue });
}

export async function addToCampaignQueue(entry: ScheduledCampaign): Promise<void> {
  const queue = await getCampaignQueue();
  queue.push(entry);
  queue.sort((a, b) => new Date(a.scheduled_at).getTime() - new Date(b.scheduled_at).getTime());
  await setCampaignQueue(queue);
}

export async function removeFromCampaignQueue(campaignId: string): Promise<void> {
  const queue = await getCampaignQueue();
  await setCampaignQueue(queue.filter(e => e.campaign.id !== campaignId));
}
