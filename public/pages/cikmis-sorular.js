// REV22 — Çıkmış Sorular listesi: ham ÖSYM sorularını görüntüleme
// Subject-aware: Edebiyat (qno/soru/secenekler şeması) + Tarih (num/body şeması)
// Manuel cevap anahtarı girişi destekli (localStorage)

import { Data, getDataSubject } from '../lib/data.js';
import { loadState, saveState } from '../lib/store.js';

function escapeHtml(s) {
  return String(s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}

function normalizeQuestion(raw, subject) {
  // İki şemayı tek formata indir
  if (subject === 'tarih') {
    return {
      no: raw.num,
      year: raw.year,
      bodyText: raw.body || '',
      konu: raw.konu || '',
      konuLabel: raw.konuLabel || raw.konu || '—',
      secenekler: null,  // body içinde gömülü
    };
  }
  // Edebiyat
  return {
    no: raw.qno,
    year: raw.year,
    bodyText: raw.soru || '',
    konu: raw.topic || '',
    konuLabel: raw.topic_label || raw.topic || '—',
    secenekler: raw.secenekler || null,
  };
}

function getCevapKey(year, no) {
  return `${year}-${no}`;
}

function getSavedAnswers(state) {
  return state.cikmis_cevap || {};
}

function setSavedAnswer(year, no, cevap) {
  const s = loadState();
  s.cikmis_cevap = s.cikmis_cevap || {};
  s.cikmis_cevap[getCevapKey(year, no)] = cevap;
  saveState(s);
}

export async function renderCikmisSorular() {
  const subject = getDataSubject();
  const raw = await Data.cikmis();
  // İki olası şema: ya direkt array (Tarih), ya {meta, questions} (Edebiyat)
  const list = Array.isArray(raw) ? raw : (raw?.questions || []);
  const questions = list.map(q => normalizeQuestion(q, subject))
    .filter(q => q.no && q.year)
    .sort((a, b) => a.year - b.year || a.no - b.no);

  const state = loadState();
  const savedAnswers = getSavedAnswers(state);

  const yearCounts = {};
  questions.forEach(q => { yearCounts[q.year] = (yearCounts[q.year] || 0) + 1; });
  const years = Object.keys(yearCounts).sort();

  const isTarih = subject === 'tarih';
  const headerTitle = isTarih ? '📋 AYT Tarih Çıkmış Sorular' : '📋 AYT Edebiyat Çıkmış Sorular';
  const headerSub = `${questions.length} soru · 2018-2025 ÖSYM kaynağı · ${Object.values(savedAnswers).length} cevap manuel girildi`;

  window.__pageSetup = () => {
    const search = document.getElementById('csSearch');
    const yearF = document.getElementById('csYear');
    function run() {
      const term = (search.value || '').toLowerCase().trim();
      const yr = yearF.value;
      document.querySelectorAll('[data-cs-row]').forEach(r => {
        const txt = r.dataset.csRow.toLowerCase();
        const y = r.dataset.year;
        let show = true;
        if (term && !txt.includes(term)) show = false;
        if (yr && yr !== 'hepsi' && y !== yr) show = false;
        r.style.display = show ? '' : 'none';
      });
    }
    search?.addEventListener('input', run);
    yearF?.addEventListener('change', run);

    // Manuel cevap kaydetme
    document.querySelectorAll('[data-save-cevap]').forEach(sel => {
      sel.addEventListener('change', (e) => {
        const [year, no] = sel.dataset.saveCevap.split(':');
        const v = e.target.value;
        if (v) setSavedAnswer(parseInt(year, 10), parseInt(no, 10), v);
        // Görsel feedback
        sel.classList.add('ring-2', 'ring-ok-500');
        setTimeout(() => sel.classList.remove('ring-2', 'ring-ok-500'), 1000);
      });
    });
  };

  return `
    <header class="mb-6">
      <h1 class="text-3xl font-bold mb-1">${headerTitle}</h1>
      <p class="text-slate-600 dark:text-slate-400 text-sm">${headerSub}</p>
    </header>

    <div class="flex gap-2 mb-4 flex-wrap">
      <input id="csSearch" type="search" placeholder="Soru içinde ara: Atatürk, Kanuni..." class="flex-1 min-w-[200px] px-3 py-2 rounded-md border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900" />
      <select id="csYear" class="px-3 py-2 rounded-md border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900">
        <option value="hepsi">Tüm yıllar (${questions.length})</option>
        ${years.map(y => `<option value="${y}">${y} (${yearCounts[y]} soru)</option>`).join('')}
      </select>
    </div>

    <div class="space-y-3">
      ${questions.map(q => {
        const saved = savedAnswers[getCevapKey(q.year, q.no)] || '';
        const opts = ['A','B','C','D','E'];
        return `
          <div data-cs-row="${escapeHtml(q.bodyText.slice(0, 200))}" data-year="${q.year}"
               class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg p-4">
            <div class="flex items-center justify-between gap-2 mb-2 flex-wrap">
              <div class="flex items-center gap-2 text-xs">
                <span class="bg-${isTarih ? 'amber' : 'primary'}-700 text-white px-2 py-0.5 rounded-full font-bold">#${q.no}</span>
                <span class="bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 px-2 py-0.5 rounded-full font-semibold">${q.year}-AYT</span>
                ${q.konuLabel !== '—' ? `<span class="text-slate-500">· ${escapeHtml(q.konuLabel)}</span>` : ''}
              </div>
              <div class="flex items-center gap-1 text-xs">
                <span class="text-slate-500">Cevap:</span>
                <select data-save-cevap="${q.year}:${q.no}" class="px-2 py-1 rounded border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 text-xs">
                  <option value="">—</option>
                  ${opts.map(o => `<option value="${o}" ${saved === o ? 'selected' : ''}>${o}</option>`).join('')}
                </select>
              </div>
            </div>
            <div class="text-sm whitespace-pre-wrap leading-relaxed text-slate-800 dark:text-slate-200">${escapeHtml(q.bodyText)}</div>
            ${q.secenekler ? `
              <div class="mt-3 space-y-1 text-sm">
                ${q.secenekler.map(s => `
                  <div class="flex gap-2"><span class="font-bold text-${isTarih ? 'amber' : 'primary'}-700 dark:text-${isTarih ? 'amber' : 'primary'}-100">${s.id})</span><span>${escapeHtml(s.text)}</span></div>
                `).join('')}
              </div>
            ` : ''}
          </div>
        `;
      }).join('')}
    </div>

    ${questions.length === 0 ? `
      <div class="text-center py-12 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg">
        <p class="text-slate-500">Çıkmış soru verisi yüklenemedi.</p>
      </div>
    ` : ''}
  `;
}
