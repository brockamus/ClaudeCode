import { ConnectionConfig, Campaign, LeadWithMessage } from './types';

const KEYS = {
  CONNECTION: 'konversly_connection',
  ACTIVE_CAMPAIGN: 'konversly_active_campaign',
  LEAD_QUEUE: 'konversly_lead_queue',
  DMS_TODAY: 'konversly_dms_today',
  DMS_TODAY_DATE: 'konversly_dms_today_date',
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
