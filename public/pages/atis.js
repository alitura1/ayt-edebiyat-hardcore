// REV5 — Hızlı Atış: random pop quiz, sonsuz mod
import { Data, topicLabel, altKonuToAuthorSlug } from '../lib/data.js';
import { loadState, saveState, updateProgress, recordSrs, dueCardIds } from '../lib/store.js';
import { tickStreak } from '../lib/streak.js';

function shuffle(arr) {
  const a = [...arr];
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

function getQuery() {
  const h = location.hash;
  const i = h.indexOf('?');
  const params = {};
  if (i >= 0) {
    const usp = new URLSearchParams(h.slice(i + 1));
    for (const [k, v] of usp) params[k] = v;
  }
  return params;
}

// %70 due havuzundan + hata defterindekiler 2× ağırlık
function pickNext(pool, state) {
  if (!pool.length) return null;
  const dueSet = new Set(dueCardIds());
  const due = pool.filter(c => dueSet.has(c.id));
  const useDue = due.length > 0 && Math.random() < 0.70;
  const source = useDue ? due : pool;
  const weighted = [];
  for (const c of source) {
    weighted.push(c);
    if (state.hata_defteri.includes(c.id)) weighted.push(c); // 2x ağırlık
  }
  return weighted[Math.floor(Math.random() * weighted.length)];
}

let _runState = { count: 0, lastCardId: null };

function renderShot(card, state, bestRun) {
  const opts = shuffle(card.secenekler.map(o => ({...o})));
  window.__pageSetup = setupShot.bind(null, card.id);

  return `
    <div class="max-w-3xl mx-auto">
      <div class="flex items-center justify-between mb-3">
        <h1 class="text-xl font-bold">⚡ Hızlı Atış</h1>
        <div class="flex gap-3 text-sm items-center">
          <span class="bg-accent-500/20 text-accent-500 px-3 py-1 rounded-full font-bold">Run: <span id="runCount">${_runState.count}</span> 🔥</span>
          <span class="text-slate-500">Best: <strong id="bestRun">${bestRun}</strong></span>
        </div>
      </div>

      <div id="atisCard">
        <div class="flex items-center justify-between text-sm mb-2">
          <span class="text-slate-500">${topicLabel(card.konu)}</span>
          <span class="text-xs text-slate-500">${card.tip || ''}</span>
        </div>

        <div class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg p-5 mb-4">
          <p class="text-base md:text-lg leading-relaxed">${card.soru}</p>
        </div>

        <div class="grid gap-2 mb-4">
          ${opts.map(o => `
            <button class="opt" data-opt="${o.id}">
              <span class="opt-letter">${o.id}</span>
              <span class="flex-1">${o.text}</span>
            </button>
          `).join('')}
        </div>

        <div id="feedback" class="hidden space-y-2 mb-4">
          <div class="ezber-box">
            <strong>✓ Doğru cevap: ${card.dogru}</strong><br>
            ${card.aciklama || ''}
          </div>
          ${card.tuzak ? `<div class="tuzak-box"><strong>⚠ TUZAK</strong><br>${card.tuzak}</div>` : ''}
          ${card.mebi_sayfa ? `<div class="mebi-box"><strong>📘 Derinleştirme</strong> → MEBİ s.<strong>${card.mebi_sayfa}</strong></div>` : ''}
        </div>
      </div>

      <div class="flex justify-between items-center mt-3">
        <a href="#/" class="text-sm text-slate-500 hover:underline">← Bırak</a>
        <button id="nextShot" class="hidden bg-accent-500 hover:bg-accent-700 text-white font-bold py-2 px-6 rounded-md">Sonraki 🎯</button>
      </div>
    </div>
  `;
}

function setupShot(currentCardId) {
  const buttons = document.querySelectorAll('[data-opt]');
  let answered = false;
  buttons.forEach(btn => {
    btn.addEventListener('click', () => {
      if (answered) return;
      answered = true;
      const chosen = btn.dataset.opt;
      // Doğru cevabı bulmak için DOM'dan alamayız, ama card'ı handler argümanından alıyoruz
      // Bunun yerine sayfayı tekrar render ediyoruz — basitlik için DOM lookup
      const correct = window.__atisCorrect;
      const isCorrect = chosen === correct;
      buttons.forEach(b => {
        b.disabled = true;
        if (b.dataset.opt === correct) b.classList.add('correct');
        if (b.dataset.opt === chosen && !isCorrect) b.classList.add('wrong');
      });
      updateProgress(currentCardId, isCorrect);
      recordSrs(currentCardId, isCorrect);
      const streakRes = tickStreak();

      // Run sayacı
      if (isCorrect) {
        _runState.count++;
      } else {
        _runState.count = 0;
      }
      const runEl = document.getElementById('runCount');
      if (runEl) runEl.textContent = _runState.count;

      // Best run güncelle
      const st = loadState();
      if (!st.atis) st.atis = { best_run: 0 };
      if (_runState.count > (st.atis.best_run || 0)) {
        st.atis.best_run = _runState.count;
        saveState(st);
        const bestEl = document.getElementById('bestRun');
        if (bestEl) bestEl.textContent = st.atis.best_run;
      }

      document.getElementById('feedback').classList.remove('hidden');
      document.getElementById('nextShot').classList.remove('hidden');

      // Streak toast
      if (streakRes.bumped) {
        const toast = document.createElement('div');
        toast.className = 'fixed bottom-4 left-1/2 -translate-x-1/2 z-50 bg-accent-500 text-white px-4 py-2 rounded-lg shadow-lg text-sm font-bold';
        toast.textContent = `🔥 Streak ${streakRes.current} gün!`;
        document.body.appendChild(toast);
        setTimeout(() => toast.remove(), 2500);
      }
    });
  });
  document.getElementById('nextShot')?.addEventListener('click', advanceShot);
}

async function advanceShot() {
  const cards = await Data.cards();
  const state = loadState();
  const q = getQuery();
  let pool = [...cards, ...state.custom_kartlar];
  if (q.yazar) pool = pool.filter(c => altKonuToAuthorSlug(c.alt_konu) === q.yazar);
  if (q.konu && q.konu !== 'hepsi') pool = pool.filter(c => c.konu === q.konu);

  // Aynı kartı arka arkaya gösterme
  let nextCard = pickNext(pool, state);
  let safety = 0;
  while (nextCard && nextCard.id === _runState.lastCardId && pool.length > 1 && safety < 8) {
    nextCard = pickNext(pool, state);
    safety++;
  }
  if (!nextCard) {
    document.getElementById('app').innerHTML = `<div class="fade-in"><p class="text-center py-12 text-slate-500">Bu filtreyle eşleşen kart yok.</p></div>`;
    return;
  }
  _runState.lastCardId = nextCard.id;
  window.__atisCorrect = nextCard.dogru;
  const html = renderShot(nextCard, state, state.atis?.best_run || 0);
  document.getElementById('app').innerHTML = `<div class="fade-in">${html}</div>`;
  if (window.__pageSetup) { try { window.__pageSetup(); } catch(e){console.error(e);} }
  window.scrollTo({ top: 0 });
}

export async function renderAtis() {
  const cards = await Data.cards();
  const state = loadState();
  const q = getQuery();

  // Run state sıfırla (yeni oturum)
  _runState = { count: 0, lastCardId: null };

  let pool = [...cards, ...state.custom_kartlar];
  if (q.yazar) pool = pool.filter(c => altKonuToAuthorSlug(c.alt_konu) === q.yazar);
  if (q.konu && q.konu !== 'hepsi') pool = pool.filter(c => c.konu === q.konu);

  if (pool.length === 0) {
    return `
      <div class="text-center py-12">
        <p class="text-slate-500 mb-3">Bu filtreyle eşleşen kart yok.</p>
        <a href="#/" class="text-primary-700 underline">← Ana sayfa</a>
      </div>
    `;
  }

  const first = pickNext(pool, state);
  _runState.lastCardId = first.id;
  window.__atisCorrect = first.dogru;
  return renderShot(first, state, state.atis?.best_run || 0);
}
