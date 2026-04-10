import { onMessage } from '../shared/messaging';

// Follow a user on their profile page
async function followUser(): Promise<boolean> {
  try {
    // Find the Follow button (not "Following", "Requested", or "Edit profile")
    const buttons = Array.from(document.querySelectorAll('button'));
    const followBtn = buttons.find(btn => {
      const text = btn.textContent?.trim();
      return text === 'Follow' && !btn.closest('[aria-label="Following"]');
    });

    if (!followBtn) {
      console.log('[Konversly] Follow button not found or already following');
      return false;
    }

    followBtn.click();
    await delay(800, 1500);
    return true;
  } catch (e) {
    console.error('[Konversly] Follow failed:', e);
    return false;
  }
}

// Like the most recent post on a profile page
async function likeRecentPost(): Promise<boolean> {
  try {
    // Find post grid links on the profile page
    const postLinks = document.querySelectorAll('article a[href*="/p/"], main a[href*="/p/"]');
    if (postLinks.length === 0) {
      console.log('[Konversly] No posts found to like');
      return false;
    }

    // Click the first (most recent) post
    (postLinks[0] as HTMLElement).click();
    await delay(1000, 2000);

    // Find the like button (heart icon) in the post modal
    const likeBtn = document.querySelector(
      'svg[aria-label="Like"][role="img"]'
    )?.closest('button') ||
    document.querySelector(
      'span[class*="like"] button, section button:first-child'
    );

    if (!likeBtn) {
      console.log('[Konversly] Like button not found');
      closeModal();
      return false;
    }

    // Check if already liked (filled heart)
    const alreadyLiked = likeBtn.querySelector('svg[aria-label="Unlike"]');
    if (alreadyLiked) {
      console.log('[Konversly] Post already liked');
      closeModal();
      return true;
    }

    (likeBtn as HTMLElement).click();
    await delay(500, 1000);

    // Close the post modal
    closeModal();
    return true;
  } catch (e) {
    console.error('[Konversly] Like post failed:', e);
    closeModal();
    return false;
  }
}

// Like the user's story if available
async function likeStory(): Promise<boolean> {
  try {
    // Story ring is typically on the profile pic with a colorful gradient border
    // or a canvas element wrapping the avatar
    const avatar = document.querySelector(
      'header canvas, header span[role="link"] img, header a[href*="/stories/"] img'
    )?.closest('[role="button"], a') as HTMLElement | null;

    if (!avatar) {
      console.log('[Konversly] No story ring found');
      return false;
    }

    // Check for story indicator (gradient ring)
    const hasStory = avatar.closest('canvas') ||
      avatar.closest('[style*="gradient"]') ||
      document.querySelector('header a[href*="/stories/"]');

    if (!hasStory) {
      console.log('[Konversly] No active story detected');
      return false;
    }

    avatar.click();
    await delay(1500, 2500);

    // Find the like button in story viewer
    const storyLikeBtn = document.querySelector(
      'svg[aria-label="Like"]'
    )?.closest('button') as HTMLElement | null;

    if (!storyLikeBtn) {
      console.log('[Konversly] Story like button not found');
      closeStoryViewer();
      return false;
    }

    storyLikeBtn.click();
    await delay(500, 1000);

    closeStoryViewer();
    return true;
  } catch (e) {
    console.error('[Konversly] Like story failed:', e);
    closeStoryViewer();
    return false;
  }
}

function closeModal(): void {
  // Close post modal via close button or Escape
  const closeBtn = document.querySelector(
    'svg[aria-label="Close"]'
  )?.closest('button') as HTMLElement | null;
  if (closeBtn) {
    closeBtn.click();
  } else {
    document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape', bubbles: true }));
  }
}

function closeStoryViewer(): void {
  // Close story viewer via close button or Escape
  const closeBtn = document.querySelector(
    'button[aria-label="Close"]'
  ) as HTMLElement | null;
  if (closeBtn) {
    closeBtn.click();
  } else {
    document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape', bubbles: true }));
  }
}

function delay(minMs: number, maxMs: number): Promise<void> {
  const ms = minMs + Math.random() * (maxMs - minMs);
  return new Promise(resolve => setTimeout(resolve, ms));
}

// Listen for warmup messages from the service worker
onMessage(async (msg, _sender, sendResponse) => {
  if (msg.type === 'FOLLOW_USER') {
    const success = await followUser();
    sendResponse({ type: 'FOLLOW_RESULT', username: msg.username, success });
    return true;
  }

  if (msg.type === 'LIKE_POST') {
    const success = await likeRecentPost();
    sendResponse({ type: 'LIKE_RESULT', username: msg.username, success });
    return true;
  }

  if (msg.type === 'LIKE_STORY') {
    const success = await likeStory();
    sendResponse({ type: 'STORY_RESULT', username: msg.username, success });
    return true;
  }
});
