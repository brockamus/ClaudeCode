import { getConnection } from './storage';
import { Lead } from './types';

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const conn = await getConnection();
  if (!conn) throw new Error('Not connected to Konversly');

  const res = await fetch(`${conn.api_url}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  });

  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.error || `Request failed: ${res.status}`);
  }

  return res.json();
}

export const api = {
  testConnection: () => request<{ status: string }>('/health'),

  generateDM: (accountId: string, campaignId: string, lead: Lead, promptInstruction: string) =>
    request<{ message: string; tokens_used: number }>('/outbound/generate-dm', {
      method: 'POST',
      body: JSON.stringify({ account_id: accountId, campaign_id: campaignId, lead, prompt_instruction: promptInstruction }),
    }),

  syncContact: (data: {
    account_id: string;
    ghl_location_id: string;
    campaign_id: string;
    instagram_handle: string;
    contact_name: string;
    instagram_bio: string;
    instagram_followers: number;
    profile_photo_url: string;
    channel_type: string;
    first_dm_content: string;
  }) => request<{ status: string; contact_id: string }>('/outbound/contacts', {
    method: 'POST',
    body: JSON.stringify(data),
  }),

  getCampaigns: (accountId: string) =>
    request<{ campaigns: unknown[] }>(`/outbound/campaigns/${accountId}`),

  createCampaign: (data: Record<string, unknown>) =>
    request<Record<string, unknown>>('/outbound/campaigns', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  updateCampaign: (id: string, data: Record<string, unknown>) =>
    request<Record<string, unknown>>(`/outbound/campaigns/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),
};
