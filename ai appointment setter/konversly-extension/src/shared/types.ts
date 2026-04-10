export interface Lead {
  instagram_handle: string;
  display_name: string;
  bio: string;
  follower_count: number;
  following_count: number;
  post_count: number;
  profile_pic_url: string;
  account_type: 'business' | 'creator' | 'personal' | 'unknown';
  is_private: boolean;
  recent_captions: string[];
}

export interface CampaignFilters {
  follower_min: number;
  follower_max: number;
  bio_keywords_include: string[];
  bio_keywords_exclude: string[];
  account_types: string[];
}

export interface RateLimits {
  dms_per_day: number;
  delay_min: number;
  delay_max: number;
  session_break_after: number;
  session_break_min: number;
  session_break_max: number;
  quiet_hours_start: number;
  quiet_hours_end: number;
}

export interface MessageVariant {
  name: string;
  prompt_instruction: string;
  weight: number;
}

export interface Campaign {
  id: string;
  account_id: string;
  name: string;
  target_account: string;
  filters: CampaignFilters;
  prompt_instruction: string;
  send_mode: 'review' | 'autopilot';
  autopilot_threshold: number;
  rate_limits: RateLimits;
  // Message variants
  variants: MessageVariant[];
  // Working hours + pacing
  working_hours_start: number;
  working_hours_end: number;
  pacing_enabled: boolean;
  // Daily limits (randomized between min/max each day)
  daily_limit_min: number;
  daily_limit_max: number;
  // Engagement warmup
  warmup_follow: boolean;
  warmup_like_post: boolean;
  warmup_like_story: boolean;
  // Scheduling
  scheduled_at?: string;
  // Stats
  status: 'draft' | 'scheduled' | 'scraping' | 'running' | 'paused' | 'completed';
  leads_scraped: number;
  leads_filtered: number;
  dms_sent: number;
  dms_approved: number;
  replies_received: number;
}

export interface LeadWithMessage extends Lead {
  generated_message: string;
  variant_name?: string;
  status: 'pending' | 'approved' | 'sent' | 'skipped' | 'failed';
  campaign_id: string;
}

export interface ConnectionConfig {
  api_url: string;
  api_key: string;
  account_id: string;
  ghl_location_id: string;
}

export type MessageType =
  | { type: 'START_SCRAPING'; target_account: string; max_leads: number }
  | { type: 'SCRAPE_RESULT'; leads: Lead[] }
  | { type: 'ENRICH_PROFILE'; username: string }
  | { type: 'PROFILE_RESULT'; lead: Lead }
  | { type: 'SEND_DM'; username: string; message: string }
  | { type: 'DM_SENT'; username: string; success: boolean }
  | { type: 'CAMPAIGN_STATUS'; status: string; progress: number; total: number }
  | { type: 'STOP_CAMPAIGN' }
  | { type: 'PAUSE_CAMPAIGN' }
  | { type: 'GET_STATUS' }
  | { type: 'START_CAMPAIGN'; campaign: Campaign }
  | { type: 'APPROVE_LEAD'; handle: string }
  | { type: 'SKIP_LEAD'; handle: string }
  | { type: 'REGENERATE_DM'; handle: string }
  | { type: 'FOLLOW_USER'; username: string }
  | { type: 'FOLLOW_RESULT'; username: string; success: boolean }
  | { type: 'LIKE_POST'; username: string }
  | { type: 'LIKE_RESULT'; username: string; success: boolean }
  | { type: 'LIKE_STORY'; username: string }
  | { type: 'STORY_RESULT'; username: string; success: boolean }
  | { type: 'SCHEDULE_CAMPAIGN'; campaign: Campaign; scheduled_at: string }
  | { type: 'GET_HEALTH' };
