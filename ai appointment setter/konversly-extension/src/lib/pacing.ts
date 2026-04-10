import { Campaign } from '../shared/types';
import { getDmsToday, getDailyTarget, setDailyTarget } from '../shared/storage';

/**
 * Pacing algorithm: spreads DMs evenly across working hours.
 * Calculates the delay until the next DM should be sent based on
 * how far through the work day we are vs how many DMs we've sent.
 */
export async function getNextSendDelay(campaign: Campaign): Promise<number> {
  const now = new Date();
  const currentHour = now.getHours() + now.getMinutes() / 60;
  const { working_hours_start: start, working_hours_end: end } = campaign;

  // Outside working hours — return ms until working hours begin
  if (!isWithinWorkingHours(currentHour, start, end)) {
    return msUntilWorkingHours(now, start);
  }

  const dmsSentToday = await getDmsToday();
  const dailyTarget = await getOrSetDailyTarget(campaign);

  // Already hit today's target
  if (dmsSentToday >= dailyTarget) {
    return -1; // Signal: done for today
  }

  // Calculate progress through work day (0.0 to 1.0)
  const windowHours = end > start ? end - start : (24 - start + end);
  const hoursElapsed = currentHour >= start
    ? currentHour - start
    : (24 - start + currentHour);
  const dayProgress = Math.min(1, hoursElapsed / windowHours);

  // Expected sends by now
  const expectedByNow = Math.floor(dailyTarget * dayProgress);
  const remaining = dailyTarget - dmsSentToday;
  const hoursLeft = windowHours - hoursElapsed;

  if (hoursLeft <= 0 || remaining <= 0) {
    return -1;
  }

  // Base interval: spread remaining DMs across remaining hours
  const baseIntervalMs = (hoursLeft * 60 * 60 * 1000) / remaining;

  // Adjust pace: if behind schedule, send sooner; if ahead, wait longer
  const pace = dmsSentToday < expectedByNow ? 0.6 : 1.4;

  // Add randomness (+-30%) to avoid mechanical patterns
  const jitter = 0.7 + Math.random() * 0.6;

  const delay = baseIntervalMs * pace * jitter;

  // Clamp: at least 30s, at most 20 minutes
  return Math.max(30_000, Math.min(delay, 20 * 60_000));
}

function isWithinWorkingHours(currentHour: number, start: number, end: number): boolean {
  if (start < end) {
    return currentHour >= start && currentHour < end;
  }
  // Wraps midnight (e.g., 22-6)
  return currentHour >= start || currentHour < end;
}

function msUntilWorkingHours(now: Date, startHour: number): number {
  const next = new Date(now);
  next.setHours(startHour, 0, 0, 0);
  if (next <= now) {
    next.setDate(next.getDate() + 1);
  }
  return next.getTime() - now.getTime();
}

async function getOrSetDailyTarget(campaign: Campaign): Promise<number> {
  const existing = await getDailyTarget();
  const today = new Date().toDateString();

  if (existing && existing.date === today) {
    return existing.target;
  }

  // Randomize today's target between min and max
  const { daily_limit_min: min, daily_limit_max: max } = campaign;
  const target = Math.floor(min + Math.random() * (max - min + 1));
  await setDailyTarget({ date: today, target });
  return target;
}
