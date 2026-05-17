import { Data, TOPIC_LABELS, topicLabel } from '../lib/data.js';
import { loadState } from '../lib/store.js';

export async function renderStats() {
  const cards = await Data.cards();
  const state = loadState();
  const all = [...cards, ...state.custom_kartlar];

  const totalSolved = Object.values(state.progress).reduce((a,p)=>a+p.cozuldu, 0);
  const totalCorrect = Object.values(state.progress).reduce((a,p)=>a+p.dogru, 0);
  const totalWrong = totalSolved - totalCorrect;
  const accuracy = totalSolved > 0 ? Math.round((totalCorrect/totalSolved)*100) : 0;
  const errorCount = state.hata_defteri.length;

  // Konu bazlı zayıflık
  const perKonu = {};
  for (const c of all) {
    const p = state.progress[c.id];
    if (!p) continue;
    if (!perKonu[c.konu]) perKonu[c.konu] = { cozuldu: 0, dogru: 0, yanlis: 0 };
    perKonu[c.konu].cozuldu += p.cozuldu;
    perKonu[c.konu].dogru += p.dogru;
    perKonu[c.konu].yanlis += p.yanlis;
  }
  const konuRows = Object.entries(perKonu)
    .map(([k, v]) => ({ k, ...v, pct: v.cozuldu > 0 ? Math.round((v.dogru/v.cozuldu)*100) : 0 }))
    .sort((a,b) => a.pct - b.pct);

  return `
    <header class="mb-6">
      <h1 class="text-3xl font-bold mb-1">📊 İstatistikler</h1>
    </header>

    ${totalSolved === 0 ? `
      <div class="text-center py-12 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg">
        <p class="text-slate-500 mb-3">Henüz hiç soru çözmedin.</p>
        <a href="#/quiz/setup" class="text-primary-700 underline">İlk quiz'ini başlat</a>
      </div>
    ` : `
      <div class="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
        <div class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg p-3 text-center">
          <div class="text-3xl font-bold">${totalSolved}</div>
          <div class="text-xs text-slate-500">Toplam Çözüm</div>
        </div>
        <div class="bg-ok-500/10 border-2 border-ok-500/30 rounded-lg p-3 text-center">
          <div class="text-3xl font-bold text-ok-500">%${accuracy}</div>
          <div class="text-xs text-slate-500">Doğruluk</div>
        </div>
        <div class="bg-accent-500/10 border-2 border-accent-500/30 rounded-lg p-3 text-center">
          <div class="text-3xl font-bold text-accent-500">${totalWrong}</div>
          <div class="text-xs text-slate-500">Yanlış</div>
        </div>
        <div class="bg-warn-500/10 border-2 border-warn-500/30 rounded-lg p-3 text-center">
          <div class="text-3xl font-bold text-warn-500">${errorCount}</div>
          <div class="text-xs text-slate-500">Hata defteri</div>
        </div>
      </div>

      ${konuRows.length > 0 ? `
        <div class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg p-4 mb-4">
          <h3 class="font-bold mb-3">Konu Bazlı Performans (zayıftan güçlüye)</h3>
          ${konuRows.map(r => `
            <div class="mb-2">
              <div class="flex items-center justify-between text-sm mb-1">
                <span class="font-medium">${topicLabel(r.k)}</span>
                <span class="text-slate-500 text-xs">${r.dogru}/${r.cozuldu} (%${r.pct})</span>
              </div>
              <div class="h-2 bg-slate-200 dark:bg-slate-800 rounded-full overflow-hidden">
                <div class="h-full ${r.pct>=70?'bg-ok-500':r.pct>=40?'bg-warn-500':'bg-accent-500'}" style="width:${r.pct}%"></div>
              </div>
            </div>
          `).join('')}
        </div>
      ` : ''}

      ${errorCount > 0 ? `
        <div class="text-center">
          <a href="#/quiz?konu=hata&sayi=${Math.min(errorCount, 30)}" class="inline-block bg-accent-500 hover:bg-accent-700 text-white font-bold py-2 px-5 rounded-md">
            ⚠️ Hata defterindeki ${errorCount} soruyu çöz
          </a>
        </div>
      ` : ''}
    `}
  `;
}
