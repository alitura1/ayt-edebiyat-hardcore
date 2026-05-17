import { Data, TOPIC_LABELS, topicLabel } from '../lib/data.js';
import { loadState, updateProgress, setSessionState, getSessionState } from '../lib/store.js';

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

export async function renderQuizSetup() {
  const q = getQuery();
  const presetKonu = q.konu || 'hepsi';

  const cards = await Data.cards();
  const state = loadState();
  const allCards = [...cards, ...state.custom_kartlar];
  const totalCount = allCards.length;
  const errorCount = state.hata_defteri.length;

  // Konu sayıları
  const counts = {};
  for (const c of allCards) counts[c.konu] = (counts[c.konu] || 0) + 1;

  return `
    <header class="mb-6">
      <h1 class="text-3xl font-bold mb-1">🎯 Quiz Ayarları</h1>
      <p class="text-slate-600 dark:text-slate-400 text-sm">ÖSYM tarzı 4-5 şıklı test. Toplam <strong>${totalCount} kart</strong> havuzda.</p>
    </header>

    <form id="quizSetup" class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg p-5 space-y-4 max-w-xl">
      <div>
        <label class="block text-sm font-semibold mb-1">Konu</label>
        <select name="konu" class="w-full px-3 py-2 rounded-md border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900">
          <option value="hepsi" ${presetKonu==='hepsi'?'selected':''}>🔀 Hepsi karışık (${totalCount})</option>
          ${errorCount > 0 ? `<option value="hata">⚠️ Sadece hata defteri (${errorCount})</option>` : ''}
          ${Object.entries(TOPIC_LABELS).map(([code, label]) => `
            <option value="${code}" ${presetKonu===code?'selected':''} ${!counts[code]?'disabled':''}>
              ${label} (${counts[code] || 0})
            </option>
          `).join('')}
        </select>
      </div>

      <div>
        <label class="block text-sm font-semibold mb-1">Zorluk</label>
        <select name="zorluk" class="w-full px-3 py-2 rounded-md border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900">
          <option value="hepsi">Hepsi</option>
          <option value="kolay">Kolay</option>
          <option value="orta">Orta</option>
          <option value="zor">Zor</option>
        </select>
      </div>

      <div>
        <label class="block text-sm font-semibold mb-1">Soru sayısı</label>
        <div class="grid grid-cols-4 gap-2">
          ${[10, 20, 30, 0].map(n => `
            <label class="flex items-center justify-center gap-2 border-2 border-slate-300 dark:border-slate-700 rounded-md py-2 cursor-pointer hover:border-primary-500 has-[:checked]:border-accent-500 has-[:checked]:bg-accent-500/10">
              <input type="radio" name="sayi" value="${n}" ${n === 10 ? 'checked' : ''} class="sr-only" />
              <span class="font-semibold">${n === 0 ? 'Hepsi' : n}</span>
            </label>
          `).join('')}
        </div>
      </div>

      <button type="submit" class="w-full bg-accent-500 hover:bg-accent-700 text-white font-bold py-3 rounded-md transition">
        🎯 Quiz'i başlat
      </button>
    </form>

    <script>
      document.getElementById('quizSetup').addEventListener('submit', (e) => {
        e.preventDefault();
        const data = new FormData(e.target);
        const params = new URLSearchParams({
          konu: data.get('konu'),
          zorluk: data.get('zorluk'),
          sayi: data.get('sayi'),
        });
        location.hash = '#/quiz?' + params.toString();
      });
    </script>
  `;
}

export async function renderQuizSession() {
  const q = getQuery();
  const cards = await Data.cards();
  const state = loadState();
  const all = [...cards, ...state.custom_kartlar];

  // Filtreleme
  let pool = all;
  if (q.konu === 'hata') {
    pool = all.filter(c => state.hata_defteri.includes(c.id));
  } else if (q.konu && q.konu !== 'hepsi') {
    pool = all.filter(c => c.konu === q.konu);
  }
  if (q.zorluk && q.zorluk !== 'hepsi') {
    pool = pool.filter(c => (c.zorluk || 'orta') === q.zorluk);
  }

  if (pool.length === 0) {
    return `
      <div class="text-center py-12">
        <p class="text-slate-500 mb-3">Bu filtreyle eşleşen kart yok.</p>
        <a href="#/quiz/setup" class="text-primary-700 underline">← Filtreyi değiştir</a>
      </div>
    `;
  }

  // Hata defterindekilere 2x ağırlık
  const weighted = [];
  for (const c of pool) {
    weighted.push(c);
    if (state.hata_defteri.includes(c.id)) weighted.push(c);
  }

  let n = parseInt(q.sayi || '10', 10);
  if (n === 0) n = pool.length;
  const session = shuffle(weighted).slice(0, n);
  // duplicate eliminasyon
  const seen = new Set();
  const unique = [];
  for (const c of session) {
    if (!seen.has(c.id)) { seen.add(c.id); unique.push(c); }
  }
  // Eğer 2x ağırlıktan dolayı azaldıysa pool'dan tamamla
  if (unique.length < n) {
    for (const c of shuffle(pool)) {
      if (unique.length >= n) break;
      if (!seen.has(c.id)) { seen.add(c.id); unique.push(c); }
    }
  }

  setSessionState('session', {
    cards: unique,
    answers: [],
    startedAt: Date.now(),
    filter: q,
  });

  return renderQuizCard(0);
}

function renderQuizCard(idx) {
  const s = getSessionState('session');
  if (!s) return `<p>Oturum yok.</p>`;
  const card = s.cards[idx];
  if (!card) return renderFinish();

  const opts = shuffle(card.secenekler.map(o => ({...o})));

  window.__pageSetup = () => {
    const buttons = document.querySelectorAll('[data-opt]');
    let answered = false;
    buttons.forEach(btn => {
      btn.addEventListener('click', () => {
        if (answered) return;
        answered = true;
        const chosen = btn.dataset.opt;
        const isCorrect = chosen === card.dogru;
        buttons.forEach(b => {
          b.disabled = true;
          if (b.dataset.opt === card.dogru) b.classList.add('correct');
          if (b.dataset.opt === chosen && !isCorrect) b.classList.add('wrong');
        });
        updateProgress(card.id, isCorrect);
        const sess = getSessionState('session');
        sess.answers.push({ id: card.id, chosen, isCorrect });
        setSessionState('session', sess);
        document.getElementById('feedback').classList.remove('hidden');
        document.getElementById('next').classList.remove('hidden');
      });
    });
    document.getElementById('next')?.addEventListener('click', () => {
      const nextIdx = idx + 1;
      if (nextIdx >= s.cards.length) {
        location.hash = '#/quiz/sonuc';
      } else {
        document.getElementById('app').innerHTML = `<div class="fade-in">${renderQuizCard(nextIdx)}</div>`;
        if (window.__pageSetup) { try { window.__pageSetup(); } catch(e){} }
        window.scrollTo({ top: 0 });
      }
    });
  };

  const progress = `${idx + 1} / ${s.cards.length}`;
  const pct = Math.round((idx / s.cards.length) * 100);

  return `
    <div class="max-w-3xl mx-auto">
      <div class="flex items-center justify-between text-sm mb-1">
        <span class="text-slate-500">${progress}</span>
        <span class="text-slate-500">${topicLabel(card.konu)}</span>
      </div>
      <div class="h-1.5 bg-slate-200 dark:bg-slate-800 rounded-full mb-5 overflow-hidden">
        <div class="h-full bg-accent-500 transition-all" style="width: ${pct}%"></div>
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
        ${card.mebi_sayfa ? `<div class="mebi-box"><strong>📘 Derinleştirme</strong> → MEBİ Konu Özet PDF sayfa <strong>${card.mebi_sayfa}</strong></div>` : ''}
      </div>

      <div class="flex justify-end">
        <button id="next" class="hidden bg-primary-700 hover:bg-primary-900 text-white font-bold py-2 px-4 rounded-md">Sonraki →</button>
      </div>
    </div>
  `;
}

function renderFinish() {
  location.hash = '#/quiz/sonuc';
  return '';
}

export async function renderQuizResult() {
  const s = getSessionState('session');
  if (!s) return `<p>Oturum bulunamadı. <a href="#/quiz/setup" class="text-primary-700 underline">Yeni quiz başlat</a></p>`;
  const total = s.answers.length;
  const correct = s.answers.filter(a => a.isCorrect).length;
  const wrong = total - correct;
  const net = Math.max(0, correct - wrong / 4);
  const wrongIds = s.answers.filter(a => !a.isCorrect).map(a => a.id);

  // Konu performansı
  const cardsById = Object.fromEntries(s.cards.map(c => [c.id, c]));
  const perKonu = {};
  for (const a of s.answers) {
    const k = cardsById[a.id]?.konu || 'bilinmiyor';
    if (!perKonu[k]) perKonu[k] = { dogru: 0, yanlis: 0 };
    if (a.isCorrect) perKonu[k].dogru++;
    else perKonu[k].yanlis++;
  }

  window.__pageSetup = () => {
    document.getElementById('redoWrongs')?.addEventListener('click', () => {
      const wrongCards = s.cards.filter(c => wrongIds.includes(c.id));
      setSessionState('session', {
        cards: wrongCards,
        answers: [],
        startedAt: Date.now(),
        filter: { konu: 'tekrar', sayi: wrongCards.length },
      });
      location.hash = '#/quiz';
      // hashchange listener tetiklenecek, ama session yenisi olduğu için
      // doğrudan render edilmesi gerek. Hash zaten "quiz" olduğu için
      // hashchange tetiklenmeyebilir → manuel render:
      setTimeout(() => location.reload(), 50);
    });
  };

  return `
    <div class="max-w-3xl mx-auto text-center">
      <h1 class="text-4xl font-bold mb-2">📊 Sonuç</h1>
      <div class="grid grid-cols-4 gap-3 my-6">
        <div class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg p-3">
          <div class="text-3xl font-bold">${total}</div>
          <div class="text-xs text-slate-500">Toplam</div>
        </div>
        <div class="bg-ok-500/10 border-2 border-ok-500/30 rounded-lg p-3">
          <div class="text-3xl font-bold text-ok-500">${correct}</div>
          <div class="text-xs text-slate-500">Doğru</div>
        </div>
        <div class="bg-accent-500/10 border-2 border-accent-500/30 rounded-lg p-3">
          <div class="text-3xl font-bold text-accent-500">${wrong}</div>
          <div class="text-xs text-slate-500">Yanlış</div>
        </div>
        <div class="bg-primary-50 dark:bg-primary-900/40 border-2 border-primary-500/30 rounded-lg p-3">
          <div class="text-3xl font-bold text-primary-700 dark:text-primary-100">${net.toFixed(2)}</div>
          <div class="text-xs text-slate-500">Net</div>
        </div>
      </div>

      ${Object.keys(perKonu).length > 1 ? `
      <div class="text-left bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg p-4 my-4">
        <h3 class="font-bold mb-2">Konu Bazlı Performans</h3>
        ${Object.entries(perKonu).map(([k, v]) => {
          const t = v.dogru + v.yanlis;
          const p = t > 0 ? Math.round((v.dogru/t)*100) : 0;
          return `
            <div class="mb-2">
              <div class="flex justify-between text-sm mb-1">
                <span>${topicLabel(k)}</span>
                <span class="text-slate-500">${v.dogru}/${t} (%${p})</span>
              </div>
              <div class="h-2 bg-slate-200 dark:bg-slate-800 rounded-full overflow-hidden">
                <div class="h-full ${p>=70?'bg-ok-500':p>=40?'bg-warn-500':'bg-accent-500'}" style="width:${p}%"></div>
              </div>
            </div>
          `;
        }).join('')}
      </div>
      ` : ''}

      <div class="flex flex-wrap gap-2 justify-center">
        <a href="#/quiz/setup" class="bg-primary-700 hover:bg-primary-900 text-white font-bold py-2 px-5 rounded-md">Yeni Quiz</a>
        ${wrong > 0 ? `<button id="redoWrongs" class="bg-accent-500 hover:bg-accent-700 text-white font-bold py-2 px-5 rounded-md">Yanlışları Tekrar Çöz</button>` : ''}
        <a href="#/" class="bg-slate-200 dark:bg-slate-800 hover:bg-slate-300 dark:hover:bg-slate-700 font-bold py-2 px-5 rounded-md">Ana sayfa</a>
      </div>
    </div>
  `;
}
