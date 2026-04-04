import { Lead } from '../shared/types';
import { onMessage } from '../shared/messaging';

function extractProfileData(): Lead {
  const lead: Lead = {
    instagram_handle: '',
    display_name: '',
    bio: '',
    follower_count: 0,
    following_count: 0,
    post_count: 0,
    profile_pic_url: '',
    account_type: 'unknown',
    is_private: false,
    recent_captions: [],
  };

  // Extract handle from URL
  const pathMatch = window.location.pathname.match(/^\/([a-zA-Z0-9._]+)\/?$/);
  if (pathMatch) lead.instagram_handle = pathMatch[1];

  // Extract display name from header
  const headerSection = document.querySelector('header section');
  if (headerSection) {
    // Display name is usually in a span within the header but outside the stats
    const nameEl = headerSection.querySelector('span[style*="font-weight"]') ||
                   headerSection.querySelector('h2')?.nextElementSibling;
    if (nameEl) lead.display_name = nameEl.textContent?.trim() || '';
  }

  // Extract bio
  const bioEl = document.querySelector('header section > div > span') ||
                document.querySelector('[class*="bio"]') ||
                document.querySelector('header span:not([class*="count"])');
  // Bio is tricky — look for the div after the name/stats section
  const headerDivs = document.querySelectorAll('header section > div');
  headerDivs.forEach(div => {
    const text = div.textContent?.trim() || '';
    if (text.length > 20 && text.length < 500 && !text.includes('followers') && !text.includes('following')) {
      lead.bio = text;
    }
  });

  // Extract stats (posts, followers, following)
  const statLinks = document.querySelectorAll('header section ul li');
  statLinks.forEach(li => {
    const text = li.textContent?.trim().toLowerCase() || '';
    const numMatch = text.replace(/,/g, '').match(/(\d+\.?\d*[kmb]?)\s*(posts?|followers?|following)/);
    if (numMatch) {
      const num = parseStatNumber(numMatch[1]);
      if (text.includes('post')) lead.post_count = num;
      else if (text.includes('follower') && !text.includes('following')) lead.follower_count = num;
      else if (text.includes('following')) lead.following_count = num;
    }
  });

  // Also try the span-based stat format
  const statSpans = document.querySelectorAll('header section span[title], header section span[class*="count"]');
  statSpans.forEach(span => {
    const title = span.getAttribute('title')?.replace(/,/g, '');
    const parent = span.closest('a') || span.closest('li') || span.parentElement;
    const context = parent?.textContent?.toLowerCase() || '';
    if (title) {
      const num = parseInt(title);
      if (!isNaN(num)) {
        if (context.includes('follower') && !context.includes('following')) lead.follower_count = num;
        else if (context.includes('following')) lead.following_count = num;
        else if (context.includes('post')) lead.post_count = num;
      }
    }
  });

  // Profile pic
  const profileImg = document.querySelector('header img[alt*="profile" i]') ||
                     document.querySelector('header img');
  if (profileImg) lead.profile_pic_url = (profileImg as HTMLImageElement).src;

  // Private account detection
  const privateText = document.body.textContent || '';
  lead.is_private = privateText.includes('This account is private') || privateText.includes('This Account is Private');

  // Account type detection
  const categoryEl = document.querySelector('header [class*="category"]') ||
                     document.querySelector('header a[href*="category"]');
  if (categoryEl) {
    const cat = categoryEl.textContent?.toLowerCase() || '';
    if (cat) lead.account_type = 'business';
  }
  // Creator accounts often have a "Creator" or "Digital creator" badge
  const badges = document.querySelectorAll('header span, header div');
  badges.forEach(el => {
    const t = el.textContent?.toLowerCase() || '';
    if (t.includes('creator') || t.includes('artist') || t.includes('musician')) {
      lead.account_type = 'creator';
    }
  });

  // Recent captions (first 3 posts)
  const articles = document.querySelectorAll('article img[alt]');
  articles.forEach((img, i) => {
    if (i < 3) {
      const alt = img.getAttribute('alt') || '';
      if (alt.length > 10) lead.recent_captions.push(alt);
    }
  });

  return lead;
}

function parseStatNumber(str: string): number {
  const lower = str.toLowerCase();
  const num = parseFloat(lower);
  if (lower.endsWith('k')) return Math.round(num * 1000);
  if (lower.endsWith('m')) return Math.round(num * 1000000);
  if (lower.endsWith('b')) return Math.round(num * 1000000000);
  return Math.round(num);
}

onMessage((message, _sender, sendResponse) => {
  if (message.type === 'ENRICH_PROFILE') {
    const lead = extractProfileData();
    sendResponse({ type: 'PROFILE_RESULT', lead });
    return true;
  }
});
