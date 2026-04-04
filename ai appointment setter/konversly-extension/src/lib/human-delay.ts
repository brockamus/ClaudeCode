// Gaussian random using Box-Muller transform
function gaussianRandom(mean: number, stdDev: number): number {
  const u1 = Math.random();
  const u2 = Math.random();
  const z = Math.sqrt(-2 * Math.log(u1)) * Math.cos(2 * Math.PI * u2);
  return mean + z * stdDev;
}

export function humanDelay(minMs: number, maxMs: number): Promise<void> {
  const mean = (minMs + maxMs) / 2;
  const stdDev = (maxMs - minMs) / 4;
  let delay = gaussianRandom(mean, stdDev);
  delay = Math.max(minMs, Math.min(maxMs * 1.2, delay));

  // 10% chance of an extra-long pause (simulating distraction)
  if (Math.random() < 0.1) {
    delay *= 2 + Math.random();
  }

  return new Promise(resolve => setTimeout(resolve, delay));
}

export function isQuietHours(startHour: number, endHour: number): boolean {
  const hour = new Date().getHours();
  if (startHour < endHour) {
    return hour >= startHour && hour < endHour;
  }
  // Wraps around midnight (e.g., 23-7)
  return hour >= startHour || hour < endHour;
}
