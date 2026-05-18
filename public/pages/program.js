import { Data } from '../lib/data.js';
import { loadState, toggleProgramCheckbox } from '../lib/store.js';

// REV14 — Konu metnindeki anahtar kelimelerden slug çıkarır
const TOPIC_HINTS = [
  ['divan', 'divan_edebiyati'],
  ['tanzimat', 'tanzimat'],
  ['servet', 'servet_i_funun_fecr_i_ati'],
  ['fecr-i ati', 'servet_i_funun_fecr_i_ati'],
  ['milli edeb', 'milli_edebiyat'],
  ['milli ed', 'milli_edebiyat'],
  ['cumhuriyet', 'cumhuriyet'],
  ['halk edeb', 'halk_edebiyati'],
  ['halk siir', 'halk_edebiyati'],
  ['asik', 'halk_edebiyati'],
  ['islamiyet', 'islamiyet_oncesi_gecis'],
  ['gecis', 'islamiyet_oncesi_gecis'],
  ['gokturk', 'islamiyet_oncesi_gecis'],
  ['orhun', 'islamiyet_oncesi_gecis'],
  ['tiyatro', 'geleneksel_tiyatro'],
  ['karagoz', 'geleneksel_tiyatro'],
  ['orta oyun', 'geleneksel_tiyatro'],
  ['meddah', 'geleneksel_tiyatro'],
  ['masal', 'masal_fabl_destan'],
  ['fabl', 'masal_fabl_destan'],
  ['destan', 'masal_fabl_destan'],
  ['halk hikay', 'masal_fabl_destan'],
  ['akim', 'edebi_akimlar'],
  ['siir bilgisi', 'siir_bilgisi'],
  ['nazim', 'siir_bilgisi'],
  ['kafiye', 'siir_bilgisi'],
  ['vezin', 'siir_bilgisi'],
  ['aruz', 'siir_bilgisi'],
  ['hece', 'siir_bilgisi'],
  ['nesir', 'nesir_bilgisi'],
  ['soz san', 'soz_sanatlari'],
];

function normalizeTr(s) {
  return (s || '').toLowerCase()
    .replace(/ş/g, 's').replace(/ç/g, 'c').replace(/ğ/g, 'g')
    .replace(/ı/g, 'i').replace(/ö/g, 'o').replace(/ü/g, 'u');
}

function konuToSlug(konuText) {
  if (!konuText) return null;
  const lower = normalizeTr(konuText);
  // "TEKRAR" veya "deneme" sözcükleri varsa link verme (özet/sınav günleri)
  if (lower.includes('tekrar') || lower.includes('deneme')) return null;
  for (const [key, slug] of TOPIC_HINTS) {
    const normKey = normalizeTr(key);
    if (lower.includes(normKey)) return slug;
  }
  return null;
}

export async function renderProgram() {
  const p = await Data.program();
  const state = loadState();
  const checks = state.program_checkbox || {};

  window.__pageSetup = () => {
    document.querySelectorAll('[data-check]').forEach(box => {
      box.addEventListener('change', () => {
        toggleProgramCheckbox(box.dataset.check);
        updateProgressBar();
      });
    });
    updateProgressBar();
  };

  function updateProgressBar() {
    const total = document.querySelectorAll('[data-check]').length;
    const done = document.querySelectorAll('[data-check]:checked').length;
    const pb = document.getElementById('progBar');
    const pl = document.getElementById('progLabel');
    if (pb && pl) {
      const pct = total > 0 ? Math.round((done/total)*100) : 0;
      pb.style.width = pct + '%';
      pl.textContent = `${done} / ${total} gün tamamlandı (%${pct})`;
    }
  }

  return `
    <header class="mb-6">
      <h1 class="text-3xl font-bold mb-1">📅 1 Aylık Program</h1>
      <p class="text-slate-600 dark:text-slate-400 text-sm">Her gün için: <strong>(R)</strong> Bu site rehberi · <strong>(M)</strong> MEBİ özet PDF · <strong>(S)</strong> Çıkmış sorular pratik.<br><span class="text-xs">💡 Konu kutusuna tıkla → o konuya git · Tik kutusu → tamamlandı</span></p>
    </header>

    <div class="mb-5 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg p-3">
      <div class="flex items-center justify-between text-sm mb-1">
        <span class="font-semibold">İlerleme</span>
        <span id="progLabel" class="text-slate-500"></span>
      </div>
      <div class="h-2 bg-slate-200 dark:bg-slate-800 rounded-full overflow-hidden">
        <div id="progBar" class="h-full bg-ok-500 transition-all" style="width:0%"></div>
      </div>
    </div>

    ${p.haftalar.map((hafta, hi) => `
      <section class="mb-6">
        <h2 class="text-xl font-bold mb-3 text-primary-700 dark:text-primary-100">
          Hafta ${hi+1}: ${hafta.baslik}
        </h2>
        <div class="space-y-2">
          ${hafta.gunler.map((g, gi) => {
            const key = `h${hi+1}_${g.gun.toLowerCase()}`;
            const checked = checks[key] ? 'checked' : '';
            const slug = konuToSlug(g.konu);
            const inner = `
              <div class="flex items-baseline gap-2 mb-1 flex-wrap">
                <span class="font-bold text-sm bg-primary-700 text-white px-2 py-0.5 rounded">${g.gun}</span>
                <span class="font-semibold text-sm">${g.konu}</span>
                ${slug ? `<span class="text-[10px] text-primary-700 dark:text-primary-100 font-bold opacity-80">→ konuya git</span>` : ''}
              </div>
              <div class="grid sm:grid-cols-3 gap-1 text-xs text-slate-600 dark:text-slate-400">
                <div><strong class="text-primary-700 dark:text-primary-100">R:</strong> ${g.rehber}</div>
                <div><strong class="text-primary-700 dark:text-primary-100">M:</strong> ${g.mebi}</div>
                <div><strong class="text-primary-700 dark:text-primary-100">S:</strong> ${g.sorular}</div>
              </div>
            `;
            return `
              <div class="flex items-start gap-2 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg p-2 has-[input:checked]:bg-ok-500/5 has-[input:checked]:border-ok-500/30">
                <label class="cursor-pointer p-1 -m-1 flex items-center" title="Tamamlandı işaretle">
                  <input type="checkbox" data-check="${key}" ${checked} class="w-5 h-5 cursor-pointer" />
                </label>
                ${slug ? `
                  <a href="#/konular/${slug}" class="flex-1 min-w-0 p-2 -m-2 rounded hover:bg-slate-50 dark:hover:bg-slate-800/50 transition">
                    ${inner}
                  </a>
                ` : `
                  <div class="flex-1 min-w-0 p-2 -m-2">
                    ${inner}
                  </div>
                `}
              </div>
            `;
          }).join('')}
        </div>
      </section>
    `).join('')}
  `;
}
