// JJA Cleaning Services: small progressive enhancements. The page works without JS.
(() => {
  const root = document.documentElement;
  root.classList.add('js');
  const PHONE = '+13163507493';
  const EMAIL = 'jjacleaning5@gmail.com';

  // Proposal ribbon: dismiss once per visitor.
  const bar = document.getElementById('proposal-bar');
  try { if (bar && localStorage.getItem('jja-proposal-hidden') === '1') bar.hidden = true; } catch {}
  document.querySelector('[data-dismiss-proposal]')?.addEventListener('click', () => {
    bar.hidden = true;
    try { localStorage.setItem('jja-proposal-hidden', '1'); } catch {}
  });

  // Before / after sliders: a native range input drives a CSS variable,
  // so keyboard and screen-reader support come for free.
  document.querySelectorAll('[data-ba]').forEach((el) => {
    const range = el.querySelector('input[type="range"]');
    const set = (v) => el.style.setProperty('--pos', `${v}%`);
    range.addEventListener('input', () => set(range.value));
    set(range.value);
  });

  // Header shadow + mobile action bar once the hero is scrolled past.
  const header = document.querySelector('.site-header');
  const actionBar = document.querySelector('.action-bar');
  const hero = document.querySelector('.hero');
  const quote = document.getElementById('quote');
  let heroGone = false;
  let quoteVisible = false;
  const syncBar = () => actionBar?.classList.toggle('is-visible', heroGone && !quoteVisible);
  if ('IntersectionObserver' in window) {
    new IntersectionObserver(([e]) => {
      heroGone = !e.isIntersecting;
      header.classList.toggle('is-scrolled', heroGone || window.scrollY > 8);
      syncBar();
    }, { rootMargin: '-120px 0px 0px 0px' }).observe(hero);
    new IntersectionObserver(([e]) => { quoteVisible = e.isIntersecting; syncBar(); }, { threshold: 0.15 }).observe(quote);
  }
  addEventListener('scroll', () => header.classList.toggle('is-scrolled', window.scrollY > 8), { passive: true });

  // Reveal on scroll.
  const reveals = document.querySelectorAll('.reveal');
  if ('IntersectionObserver' in window && !matchMedia('(prefers-reduced-motion: reduce)').matches) {
    const io = new IntersectionObserver((entries) => {
      entries.forEach((e) => { if (e.isIntersecting) { e.target.classList.add('is-in'); io.unobserve(e.target); } });
    }, { rootMargin: '0px 0px -8% 0px' });
    reveals.forEach((el) => io.observe(el));
  } else {
    reveals.forEach((el) => el.classList.add('is-in'));
  }

  // Gallery lightbox.
  const box = document.getElementById('lightbox');
  const boxImg = document.getElementById('lightbox-img');
  const boxCap = document.getElementById('lightbox-cap');
  document.querySelectorAll('[data-gallery] button').forEach((btn) => {
    btn.addEventListener('click', () => {
      if (typeof box.showModal !== 'function') { window.open(btn.dataset.full, '_blank'); return; }
      boxImg.src = btn.dataset.full;
      boxImg.alt = btn.querySelector('img')?.alt || '';
      boxCap.textContent = btn.dataset.caption || '';
      box.showModal();
    });
  });
  box.addEventListener('click', (e) => { if (e.target === box || e.target.hasAttribute('data-close')) box.close(); });

  // Service buttons pre-select the matching option in the quote form.
  const form = document.getElementById('quote-form');
  const select = form.querySelector('#f-service');
  document.querySelectorAll('[data-service]').forEach((a) => {
    a.addEventListener('click', () => { select.value = a.dataset.service; });
  });

  // Quote form: validate, then open a pre-written text or email.
  // No backend needed; in production this can post to a CRM instead.
  const status = document.getElementById('form-status');
  let channel = 'sms';
  form.querySelectorAll('button[type="submit"]').forEach((b) => b.addEventListener('click', () => { channel = b.dataset.channel; }));
  form.addEventListener('submit', (e) => {
    e.preventDefault();
    const name = form.elements.name;
    const phone = form.elements.phone;
    let firstBad = null;
    [[name, name.value.trim().length > 1], [phone, phone.value.replace(/\D/g, '').length >= 10]].forEach(([el, ok]) => {
      el.setAttribute('aria-invalid', ok ? 'false' : 'true');
      if (!ok && !firstBad) firstBad = el;
    });
    if (firstBad) { firstBad.focus(); return; }

    const lines = [
      `Hi JJA! I'd like a free quote.`,
      `Name: ${name.value.trim()}`,
      `Phone: ${phone.value.trim()}`,
      `Service: ${select.value}`,
      `How often: ${form.elements.freq.value}`,
    ];
    const msg = form.elements.message.value.trim();
    if (msg) lines.push(`Details: ${msg}`);
    const body = encodeURIComponent(lines.join('\n'));

    if (channel === 'email') {
      location.href = `mailto:${EMAIL}?subject=${encodeURIComponent('Free quote request: ' + select.value)}&body=${body}`;
    } else {
      location.href = `sms:${PHONE}?&body=${body}`;
    }
    status.hidden = false;
    status.textContent = channel === 'email'
      ? 'Your email is ready. Just hit send and we’ll reply shortly.'
      : 'Your text is ready. Just hit send. On a computer? Use “Send by email” or call 316-350-7493.';
  });
  form.querySelectorAll('input[required]').forEach((el) => el.addEventListener('input', () => el.setAttribute('aria-invalid', 'false')));

  document.querySelectorAll('[data-year]').forEach((el) => { el.textContent = new Date().getFullYear(); });
})();
