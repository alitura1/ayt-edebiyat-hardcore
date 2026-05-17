import { Data } from '../lib/data.js';
import { loadState, toggleProgramCheckbox } from '../lib/store.js';

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
      <p class="text-slate-600 dark:text-slate-400 text-sm">Her gün için: <strong>(R)</strong> Bu site rehberi · <strong>(M)</strong> MEBİ özet PDF · <strong>(S)</strong> Çıkmış sorular pratik.</p>
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
            return `
              <label class="flex items-start gap-3 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg p-3 has-[:checked]:bg-ok-500/5 has-[:checked]:border-ok-500/30 cursor-pointer">
                <input type="checkbox" data-check="${key}" ${checked} class="mt-1 w-5 h-5" />
                <div class="flex-1 min-w-0">
                  <div class="flex items-baseline gap-2 mb-1">
                    <span class="font-bold text-sm bg-primary-700 text-white px-2 py-0.5 rounded">${g.gun}</span>
                    <span class="font-semibold text-sm">${g.konu}</span>
                  </div>
                  <div class="grid sm:grid-cols-3 gap-1 text-xs text-slate-600 dark:text-slate-400">
                    <div><strong class="text-primary-700 dark:text-primary-100">R:</strong> ${g.rehber}</div>
                    <div><strong class="text-primary-700 dark:text-primary-100">M:</strong> ${g.mebi}</div>
                    <div><strong class="text-primary-700 dark:text-primary-100">S:</strong> ${g.sorular}</div>
                  </div>
                </div>
              </label>
            `;
          }).join('')}
        </div>
      </section>
    `).join('')}
  `;
}
