import { getConnection } from './storage';
import { Lead, Campaign } from './types';

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
    variant_name?: string | null;
  }) => request<{ status: string; contact_id: string }>('/outbound/contacts', {
    method: 'POST',
    body: JSON.stringify(data),
  }),

  getContactedHandles: (accountId: string) =>
    request<{ handles: string[] }>(`/outbound/contacted/${accountId}`),

  getReplies: (accountId: string) =>
    request<{ replied_handles: string[]; total_contacted: number; total_replies: number; reply_rate: string }>(`/outbound/replies/${accountId}`),

  getVariantStats: (campaignId: string) =>
    request<{ variant_stats: Array<{ variant_name: string; sent: number; replies: number; reply_rate: string }> }>(`/outbound/campaigns/${campaignId}/variant-stats`),

  getScheduledCampaigns: (accountId: string) =>
    request<{ campaigns: Campaign[] }>(`/outbound/scheduled/${accountId}`),

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
