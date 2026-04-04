import { RateLimits } from '../shared/types';
import { getDmsToday } from '../shared/storage';
import { isQuietHours } from '../lib/human-delay';

export async function canSendDM(limits: RateLimits): Promise<{ allowed: boolean; reason?: string }> {
  // Check quiet hours
  if (isQuietHours(limits.quiet_hours_start, limits.quiet_hours_end)) {
    return { allowed: false, reason: 'quiet_hours' };
  }

  // Check daily limit
  const today = await getDmsToday();
  if (today >= limits.dms_per_day) {
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
