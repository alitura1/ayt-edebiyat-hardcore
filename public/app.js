// Ana uygulama: hash router + sayfa render orkestrasyonu
import { renderHome } from './pages/home.js';
import { renderTopicList, renderTopicDetail } from './pages/topics.js';
import { renderAuthorList, renderAuthorDetail } from './pages/authors.js';
import { renderPredictions } from './pages/predictions.js';
import { renderProgram } from './pages/program.js';
import { renderGlossary } from './pages/glossary.js';
import { renderQuizSetup, renderQuizSession, renderQuizResult } from './pages/quiz.js';
import { renderCardList, renderCardNew } from './pages/cards.js';
import { renderStats } from './pages/stats.js';
import { renderSettings } from './pages/settings.js';
import { renderAtis } from './pages/atis.js';
import { renderCollection } from './pages/collection.js';
import { streakInfo, currentBadge } from './lib/streak.js';

// ---- Tema ----
const themeKey = 'edebiyat-theme';
function applyTheme(t) {
  document.documentElement.classList.toggle('dark', t === 'dark');
}
function initTheme() {
  const saved = localStorage.getItem(themeKey);
  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
  applyTheme(saved || (prefersDark ? 'dark' : 'light'));
  document.getElementById('darkToggle')?.addEventListener('click', () => {
    const cur = document.documentElement.classList.contains('dark') ? 'dark' : 'light';
    const next = cur === 'dark' ? 'light' : 'dark';
    localStorage.setItem(themeKey, next);
    applyTheme(next);
  });
}

// ---- Router ----
const app = document.getElementById('app');

function notFound() {
  return `
    <div class="text-center py-16">
      <h1 class="text-4xl font-bold mb-2">404</h1>
      <p class="text-slate-500 mb-4">Sayfa bulunamadı.</p>
      <a href="#/" class="text-primary-700 dark:text-primary-100 underline">Ana sayfaya dön</a>
    </div>
  `;
}

async function render() {
  const rawHash = location.hash.slice(1) || '/';
  const hash = rawHash.split('?')[0]; // query string'i ayır
  const parts = hash.split('/').filter(Boolean); // ["quiz","setup"] vs.

  let html = '';
  try {
    if (parts.length === 0) {
      html = await renderHome();
    } else if (parts[0] === 'konular' && !parts[1]) {
      html = await renderTopicList();
    } else if (parts[0] === 'konular' && parts[1]) {
      html = await renderTopicDetail(parts[1]);
    } else if (parts[0] === 'yazarlar' && !parts[1]) {
      html = await renderAuthorList();
    } else if (parts[0] === 'yazarlar' && parts[1]) {
      html = await renderAuthorDetail(parts[1]);
    } else if (parts[0] === 'tahminler') {
      html = await renderPredictions();
    } else if (parts[0] === 'program') {
      html = await renderProgram();
    } else if (parts[0] === 'sozluk') {
      html = await renderGlossary();
    } else if (parts[0] === 'quiz' && parts[1] === 'setup') {
      html = await renderQuizSetup();
    } else if (parts[0] === 'quiz' && parts[1] === 'sonuc') {
      html = await renderQuizResult();
    } else if (parts[0] === 'quiz') {
      html = await renderQuizSession();
    } else if (parts[0] === 'kartlar' && parts[1] === 'yeni') {
      html = await renderCardNew();
    } else if (parts[0] === 'kartlar' && parts[1] && parts[1] !== 'yeni') {
      html = await renderCardNew(parts[1]); // edit mode
    } else if (parts[0] === 'kartlar') {
      html = await renderCardList();
    } else if (parts[0] === 'istatistik') {
      html = await renderStats();
    } else if (parts[0] === 'ayarlar') {
      html = await renderSettings();
    } else if (parts[0] === 'atis') {
      html = await renderAtis();
    } else if (parts[0] === 'koleksiyon') {
      html = await renderCollection();
    } else {
      html = notFound();
    }
  } catch (e) {
    console.error(e);
    html = `
      <div class="text-center py-16">
        <h1 class="text-3xl font-bold text-accent-500 mb-2">Hata</h1>
        <p class="text-slate-500 mb-2">${e?.message || 'Bilinmeyen hata'}</p>
        <pre class="text-xs text-left bg-slate-100 dark:bg-slate-800 p-3 rounded overflow-auto max-w-2xl mx-auto">${(e?.stack || '').replace(/</g,'&lt;')}</pre>
      </div>
    `;
  }

  app.innerHTML = `<div class="fade-in">${html}</div>`;
  window.scrollTo({ top: 0, behavior: 'instant' });

  // REV5 — global streak rozeti güncelle
  updateStreakBadge();

  // Bazı sayfaların post-render setup callback'i olabilir
  if (window.__pageSetup) {
    try { window.__pageSetup(); } catch (e) { console.error(e); }
    window.__pageSetup = null;
  }
}

function updateStreakBadge() {
  const el = document.getElementById('streakBadge');
  if (!el) return;
  const info = streakInfo();
  if (!info.current || info.current === 0) {
    el.classList.add('hidden');
    el.classList.remove('flex');
    return;
  }
  const badge = currentBadge(info.current);
  const emoji = badge?.emoji || '🔥';
  el.innerHTML = `<span>${emoji}</span><span>${info.current}</span>`;
  el.classList.remove('hidden');
  el.classList.add('flex');
  el.title = `${info.current} günlük seri (en uzun: ${info.longest}) — ${info.status === 'at_risk' ? 'Bugün soru çöz, kaybetme!' : info.status === 'active_today' ? 'Bugün aktif ✓' : ''}`;
  el.href = '#/atis';
}

window.addEventListener('hashchange', render);
window.addEventListener('DOMContentLoaded', () => {
  initTheme();
  render();
});
