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
    // REV25 yeni şema: body + options[] + correct + donem_slug
    return {
      no: raw.num,
      year: raw.year,
      bodyText: raw.body || '',
      konu: raw.donem_slug || raw.konu || '',
      konuLabel: raw.konuLabel || raw.donem_slug || '—',
      secenekler: Array.isArray(raw.options) && raw.options.length > 0 ? raw.options : null,
      correctRaw: raw.correct || null,
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
    // REV18c — derin analiz alanları
    dogru_cevap: raw.dogru_cevap || null,
    soru_tipi_analizi: raw.soru_tipi_analizi || null,
    neden_dogru: raw.neden_dogru || null,
    celdirici_analizi: raw.celdirici_analizi || null,
    osym_mantigi: raw.osym_mantigi || null,
    dersini_ogren: raw.dersini_ogren || null,
    analiz_var: raw.analiz_var || false,
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
  // REV18c — derin analizli soru sayısı
  const analizliCount = questions.filter(q => q.analiz_var).length;
  const headerSub = `${questions.length} soru · 2018-2025 ÖSYM kaynağı · ${Object.values(savedAnswers).length} cevap girildi`
    + (analizliCount > 0 ? ` · <span class="text-ok-500 font-bold">${analizliCount} soruda derin analiz</span>` : '');

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
                  <div class="flex gap-2 ${q.dogru_cevap === s.id ? 'bg-ok-500/15 px-2 -mx-2 py-1 rounded' : ''}"><span class="font-bold text-${isTarih ? 'amber' : 'primary'}-700 dark:text-${isTarih ? 'amber' : 'primary'}-100">${s.id})</span><span>${escapeHtml(s.text)}</span>${q.dogru_cevap === s.id ? '<span class="ml-auto text-ok-500 text-xs font-bold">✓ DOĞRU</span>' : ''}</div>
                `).join('')}
              </div>
            ` : ''}
            ${q.analiz_var ? `
              <details class="mt-3 border-t border-slate-200 dark:border-slate-700 pt-3">
                <summary class="cursor-pointer text-sm font-bold text-primary-700 dark:text-primary-100 hover:text-accent-500">📚 ÖSYM Mantığı + Derin Analizi Aç</summary>
                <div class="mt-3 space-y-3 text-sm">
                  ${q.soru_tipi_analizi ? `
                    <div class="bg-primary-500/5 border-l-4 border-primary-500 p-3 rounded-r">
                      <strong class="text-primary-700 dark:text-primary-100">🎯 Soru Tipi Analizi</strong>
                      <p class="mt-1 text-slate-700 dark:text-slate-300">${escapeHtml(q.soru_tipi_analizi)}</p>
                    </div>
                  ` : ''}
                  ${q.neden_dogru ? `
                    <div class="bg-ok-500/10 border-l-4 border-ok-500 p-3 rounded-r">
                      <strong class="text-ok-700 dark:text-ok-300">✓ Neden ${q.dogru_cevap || ''} Doğru</strong>
                      <p class="mt-1 text-slate-700 dark:text-slate-300">${escapeHtml(q.neden_dogru)}</p>
                    </div>
                  ` : ''}
                  ${q.celdirici_analizi && Object.keys(q.celdirici_analizi).length ? `
                    <div class="bg-warn-500/10 border-l-4 border-warn-500 p-3 rounded-r">
                      <strong class="text-warn-700 dark:text-warn-300">🔍 Çeldirici Analizi</strong>
                      <div class="mt-2 space-y-1">
                        ${Object.entries(q.celdirici_analizi).map(([k,v]) => `
                          <div class="text-xs"><strong class="text-warn-600 dark:text-warn-400">${k})</strong> <span class="text-slate-700 dark:text-slate-300">${escapeHtml(v)}</span></div>
                        `).join('')}
                      </div>
                    </div>
                  ` : ''}
                  ${q.osym_mantigi ? `
                    <div class="bg-accent-500/10 border-l-4 border-accent-500 p-3 rounded-r">
                      <strong class="text-accent-700 dark:text-accent-300">🧠 ÖSYM'nin Mantığı</strong>
                      <p class="mt-1 text-slate-700 dark:text-slate-300">${escapeHtml(q.osym_mantigi)}</p>
                    </div>
                  ` : ''}
                  ${q.dersini_ogren ? `
                    <div class="bg-slate-100 dark:bg-slate-800 border-l-4 border-slate-400 p-3 rounded-r">
                      <strong class="text-slate-700 dark:text-slate-300">📝 Dersini Öğren</strong>
                      <p class="mt-1 text-slate-700 dark:text-slate-300 italic">${escapeHtml(q.dersini_ogren)}</p>
                    </div>
                  ` : ''}
                </div>
              </details>
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
