import { RateLimits, Campaign } from '../shared/types';
import { getDmsToday, getDailyTarget } from '../shared/storage';
import { isQuietHours } from '../lib/human-delay';

export async function canSendDM(limits: RateLimits, campaign?: Campaign): Promise<{ allowed: boolean; reason?: string }> {
  // Check working hours (if campaign has them) or fall back to quiet hours
  if (campaign && campaign.working_hours_start !== undefined && campaign.working_hours_end !== undefined) {
    const hour = new Date().getHours();
    const start = campaign.working_hours_start;
    const end = campaign.working_hours_end;
    const withinHours = start < end
      ? hour >= start && hour < end
      : hour >= start || hour < end;
    if (!withinHours) {
      return { allowed: false, reason: 'outside_working_hours' };
    }
  } else if (isQuietHours(limits.quiet_hours_start, limits.quiet_hours_end)) {
    return { allowed: false, reason: 'quiet_hours' };
  }

  // Check daily limit — use randomized daily target if available, else fixed limit
  const today = await getDmsToday();
  if (campaign && campaign.daily_limit_max) {
    const dailyTarget = await getDailyTarget();
    const todayStr = new Date().toDateString();
    const limit = (dailyTarget && dailyTarget.date === todayStr) ? dailyTarget.target : campaign.daily_limit_max;
    if (today >= limit) {
      return { allowed: false, reason: 'daily_limit' };
    }
  } else if (today >= limits.dms_per_day) {
    return { allowed: false, reason: 'daily_limit' };
  }

  return { allowed: true };
}

export function getDelayMs(limits: RateLimits): number {
  return limits.delay_min * 1000 + Math.random() * (limits.delay_max - limits.delay_min) * 1000;
}

export function shouldTakeBreak(dmsSinceBreak: number, limits: RateLimits): boolean {
  return dmsSinceBreak >= limits.session_break_after;
}

export function getBreakDurationMs(limits: RateLimits): number {
  return (limits.session_break_min + Math.random() * (limits.session_break_max - limits.session_break_min)) * 1000;
}
