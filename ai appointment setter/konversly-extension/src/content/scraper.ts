import { Lead } from '../shared/types';
import { onMessage } from '../shared/messaging';

// Scrapes usernames from the followers dialog on instagram.com/{handle}/followers/
function scrapeFollowerList(maxLeads: number): Promise<string[]> {
  return new Promise((resolve) => {
    const usernames: Set<string> = new Set();
    const dialog = document.querySelector('[role="dialog"]');

    if (!dialog) {
      resolve([]);
      return;
    }

    const scrollContainer = dialog.querySelector('[style*="overflow"]') || dialog;
    let lastCount = 0;
    let staleRounds = 0;

    const interval = setInterval(() => {
      // Extract usernames from follower list links
      const links = dialog.querySelectorAll('a[href^="/"]');
      links.forEach(link => {
        const href = link.getAttribute('href');
        if (href && href.match(/^\/[a-zA-Z0-9._]+\/?$/) && !href.includes('/p/') && !href.includes('/explore/')) {
          const username = href.replace(/\//g, '');
          if (username && username.length > 0 && username !== 'explore' && username !== 'accounts') {
            usernames.add(username);
          }
        }
      });

      // Check if we have enough
      if (usernames.size >= maxLeads) {
        clearInterval(interval);
        resolve(Array.from(usernames).slice(0, maxLeads));
        return;
      }

      // Check if we're stuck (no new usernames after scroll)
      if (usernames.size === lastCount) {
        staleRounds++;
        if (staleRounds >= 5) {
          clearInterval(interval);
          resolve(Array.from(usernames));
          return;
        }
      } else {
        staleRounds = 0;
        lastCount = usernames.size;
      }

      // Scroll down
      scrollContainer.scrollTop = scrollContainer.scrollHeight;
    }, 1500);

    // Safety timeout after 5 minutes
    setTimeout(() => {
      clearInterval(interval);
      resolve(Array.from(usernames));
    }, 5 * 60 * 1000);
  });
}

// Listen for scrape commands from the service worker
onMessage((message, _sender, sendResponse) => {
  if (message.type === 'START_SCRAPING') {
    scrapeFollowerList(message.max_leads).then(usernames => {
      const leads: Lead[] = usernames.map(u => ({
        instagram_handle: u,
        display_name: '',
        bio: '',
        follower_count: 0,
        following_count: 0,
        post_count: 0,
        profile_pic_url: '',
        account_type: 'unknown' as const,
        is_private: false,
        recent_captions: [],
      }));
      sendResponse({ type: 'SCRAPE_RESULT', leads });
    });
    return true; // async response
  }
});
