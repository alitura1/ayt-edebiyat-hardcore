// Ana uygulama: hash router + sayfa render orkestrasyonu
// REV20 — HİBRİT (Edebiyat + Tarih) subject-aware
import { renderHome } from './pages/home.js';
import { renderTopicList, renderTopicDetail } from './pages/topics.js';
import { renderAuthorList, renderAuthorDetail } from './pages/authors.js';
import { renderPredictions } from './pages/predictions.js';
import { renderPattern } from './pages/pattern.js';
import { renderProgram } from './pages/program.js';
import { renderGlossary } from './pages/glossary.js';
import { renderTerms } from './pages/terms.js';
import { renderQuizSetup, renderQuizSession, renderQuizResult } from './pages/quiz.js';
import { renderCardList, renderCardNew } from './pages/cards.js';
import { renderStats } from './pages/stats.js';
import { renderSettings } from './pages/settings.js';
import { renderAtis } from './pages/atis.js';
import { renderCollection } from './pages/collection.js';
import { renderWorkList, renderWorkDetail } from './pages/works.js';
import { renderGroupList, renderGroupDetail } from './pages/groups.js';
import { renderLogin, renderRegister, renderProfile } from './pages/auth.js';
import { renderSelectSubject, setupSelectSubject } from './pages/select-subject.js';
import { renderCikmisSorular } from './pages/cikmis-sorular.js';
import { renderSimulations } from './pages/simulations.js';
import { streakInfo, currentBadge } from './lib/streak.js';
import { initSync, scheduleSync, currentSyncUid, refreshSyncForSubject } from './lib/sync.js';
import { startNotifyScheduler } from './lib/notify.js';
import {
  loadSubjectPreference, getCurrentSubject, saveSubjectPreference,
  migrateOldData
} from './lib/store.js';
import { setDataSubject } from './lib/data.js';

const SUBJECT_META = {
  edebiyat: { title: 'AYT Edebiyat — Hardcore Hazırlık', slogan: 'Yazar avı, ezber atışı' },
  tarih:    { title: 'AYT Tarih — Hardcore Hazırlık',    slogan: 'Tarihçi olma, tarihi yendin sayılır' },
  fen:      { title: 'TYT Fen — Hardcore Hazırlık',      slogan: 'Fizik · Kimya · Biyoloji — 4 hafta uçuş' },
};

// ---- Tema ----
const themeKey = 'theme';  // REV20: subject-agnostic (eski edebiyat-theme geriye dönük okunur)
function applyTheme(t) {
  document.documentElement.classList.toggle('dark', t === 'dark');
}
function initTheme() {
  // Eski edebiyat-theme key'inden migration
  let saved = localStorage.getItem(themeKey) || localStorage.getItem('edebiyat-theme');
  if (saved && !localStorage.getItem(themeKey)) {
    localStorage.setItem(themeKey, saved);
  }
  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
  applyTheme(saved || (prefersDark ? 'dark' : 'light'));
  document.getElementById('darkToggle')?.addEventListener('click', () => {
    const cur = document.documentElement.classList.contains('dark') ? 'dark' : 'light';
    const next = cur === 'dark' ? 'light' : 'dark';
    localStorage.setItem(themeKey, next);
    applyTheme(next);
  });
}

// ---- REV20: Subject yönetimi ----
function applySubject(subject) {
  if (!subject) return;
  // <html data-subject="edebiyat|tarih"> set et
  document.documentElement.setAttribute('data-subject', subject);
  // data.js'i bilgilendir
  setDataSubject(subject);
  // Sayfa başlığı
  const meta = SUBJECT_META[subject];
  if (meta) {
    document.title = meta.title;
    const titleEl = document.getElementById('pageTitle');
    if (titleEl) titleEl.textContent = meta.title;
  }
}

function updateSubjectToggle() {
  const toggle = document.getElementById('subjectToggle');
  if (!toggle) return;
  const current = getCurrentSubject();
  if (!current) {
    toggle.classList.add('hidden');
    return;
  }
  toggle.classList.remove('hidden');
  toggle.innerHTML = `
    <button data-sub="edebiyat" class="px-2.5 py-1 rounded-full text-xs font-bold transition ${current==='edebiyat' ? 'bg-primary-600 text-white' : 'text-slate-500 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800'}">📚 Edebiyat</button>
    <button data-sub="tarih" class="px-2.5 py-1 rounded-full text-xs font-bold transition ${current==='tarih' ? 'bg-amber-600 text-white' : 'text-slate-500 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800'}">⏳ Tarih</button>
    <button data-sub="fen" class="px-2.5 py-1 rounded-full text-xs font-bold transition ${current==='fen' ? 'bg-emerald-600 text-white' : 'text-slate-500 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800'}">⚗ Fen</button>
  `;
  toggle.querySelectorAll('button[data-sub]').forEach(btn => {
    btn.addEventListener('click', async () => {
      const newSub = btn.dataset.sub;
      if (newSub === current) return;
      saveSubjectPreference(newSub);
      applySubject(newSub);
      // Cloud sync için yeni subject'i de pull et
      try { await refreshSyncForSubject(newSub); } catch(e) { console.warn(e); }
      location.hash = '#/';
      // Cache'leri temizleyip yeniden render
      setTimeout(() => location.reload(), 50);
    });
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
  // REV15 — hem query (?) hem ikinci hash (#) ayır (anchor scroll için)
  const hash = rawHash.split('?')[0].split('#')[0];
  const parts = hash.split('/').filter(Boolean); // ["quiz","setup"] vs.

  // REV20 — Subject Gate: subject seçilmemişse select-subject sayfasına yönlendir
  const subject = getCurrentSubject();
  const allowWithoutSubject = ['select-subject', 'giris', 'kayit'];
  if (!subject && parts[0] !== 'select-subject' && !allowWithoutSubject.includes(parts[0])) {
    location.hash = '#/select-subject';
    return;
  }

  let html = '';
  try {
    if (parts[0] === 'select-subject') {
      html = await renderSelectSubject();
      window.__pageSetup = setupSelectSubject;
    } else if (parts.length === 0) {
      html = await renderHome();
    } else if (parts[0] === 'konular' && !parts[1]) {
      html = await renderTopicList();
    } else if (parts[0] === 'konular' && parts[1]) {
      html = await renderTopicDetail(parts[1]);
    } else if (parts[0] === 'yazarlar' && !parts[1]) {
      html = await renderAuthorList();
    } else if (parts[0] === 'yazarlar' && parts[1]) {
      html = await renderAuthorDetail(parts[1]);
    } else if (parts[0] === 'cikmis-sorular') {
      html = await renderCikmisSorular();
    } else if (parts[0] === 'tahminler') {
      html = await renderPredictions();
    } else if (parts[0] === 'sistem' || parts[0] === 'pattern') {
      html = await renderPattern();
    } else if (parts[0] === 'program') {
      html = await renderProgram();
    } else if (parts[0] === 'sozluk') {
      html = await renderGlossary();
    } else if (parts[0] === 'terimler') {
      html = await renderTerms();
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
    } else if (parts[0] === 'simulasyonlar') {
      html = await renderSimulations();
    } else if (parts[0] === 'koleksiyon') {
      html = await renderCollection();
    } else if (parts[0] === 'eserler' && !parts[1]) {
      html = await renderWorkList();
    } else if (parts[0] === 'eserler' && parts[1]) {
      html = await renderWorkDetail(parts[1]);
    } else if (parts[0] === 'gruplar') {
      html = await renderGroupList();
    } else if (parts[0] === 'grup' && parts[1]) {
      html = await renderGroupDetail(parts[1]);
    } else if (parts[0] === 'giris') {
      html = await renderLogin();
    } else if (parts[0] === 'kayit') {
      html = await renderRegister();
    } else if (parts[0] === 'hesap') {
      html = await renderProfile();
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
  // REV6 — auth rozetini güncelle
  updateAuthBadge();
  // REV20 — subject toggle güncelle
  updateSubjectToggle();

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
window.addEventListener('DOMContentLoaded', async () => {
  initTheme();

  // REV20 — Subject yönetimi: migration + preference load + data subject
  const savedSubject = loadSubjectPreference();
  if (savedSubject) {
    applySubject(savedSubject);
  } else {
    // İlk açılışta migration tetiklenebilir (select-subject sayfasında da çalışır)
    // Eski edebiyat-state-v1 verisi varsa kullanıcıya korunduğunu garanti eder.
  }

  // REV6 — Cloud sync init (Firebase yüklenir, login varsa pull yapar)
  window.__syncHook = scheduleSync;
  initSync().catch(e => console.warn('sync init err', e));
  // REV8+9+11 — Google OAuth redirect'ten dönüş yakalama
  try {
    const fb = await import('./lib/firebase.js');
    const inst = await fb.getFirebase();
    const result = await inst.authMod.getRedirectResult(inst.auth);
    if (result?.user) {
      console.log('[auth] redirect login OK:', result.user.email);
      window.dispatchEvent(new CustomEvent('authchange', { detail: { user: result.user } }));
      // Header rozeti + sayfa render — gecikme ile sync init'i bekle
      setTimeout(() => render(), 250);
    }
  } catch(e) { console.warn('redirect result err', e); }
  startNotifyScheduler();
  // Auth state değişince re-render (header auth göstergesi)
  window.addEventListener('authchange', () => {
    updateAuthBadge();
  });
  render();
});

function updateAuthBadge() {
  const el = document.getElementById('authBadge');
  if (!el) return;
  const uid = currentSyncUid();
  if (uid) {
    el.innerHTML = '<span class="text-ok-500">☁️</span><span class="hidden md:inline ml-1">Hesabım</span>';
    el.href = '#/hesap';
    el.title = 'Cloud sync aktif';
  } else {
    el.innerHTML = '<span>🔐</span><span class="hidden md:inline ml-1">Giriş</span>';
    el.href = '#/giris';
    el.title = 'Cihazlar arası sync için giriş yap';
  }
}
