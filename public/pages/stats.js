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

  // Doğruluk trendi (son 30 cevap zaman sırasıyla)
  const allAnswers = Object.entries(state.progress)
    .map(([id, p]) => ({ id, son: p.son, dogruluk: p.cozuldu > 0 ? p.dogru/p.cozuldu : 0 }))
    .filter(a => a.son > 0)
    .sort((a,b) => a.son - b.son)
    .slice(-30);

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

      <div class="grid md:grid-cols-2 gap-4 mb-4">
        <div class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg p-4">
          <h3 class="font-bold mb-3">🎯 Konu Bazlı Doğruluk (Donut)</h3>
          ${donutChart(konuRows)}
        </div>
        <div class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg p-4">
          <h3 class="font-bold mb-3">📈 Son ${allAnswers.length} Kartta Doğruluk Trendi</h3>
          ${lineChart(allAnswers)}
        </div>
      </div>

      ${konuRows.length > 0 ? `
        <div class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg p-4 mb-4">
          <h3 class="font-bold mb-3">Konu Bazlı Performans (zayıftan güçlüye) — Bar Grafik</h3>
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

// Donut chart (konu bazlı doğruluk)
function donutChart(rows) {
  if (rows.length === 0) return '<p class="text-slate-500 text-sm">Veri yok</p>';
  const cx = 100, cy = 100, r = 70, sw = 18;
  const totalCozuldu = rows.reduce((s,r)=>s+r.cozuldu, 0);
  if (totalCozuldu === 0) return '<p class="text-slate-500 text-sm">Veri yok</p>';

  let currAngle = -Math.PI/2;  // 12 saat yönü başla
  const slices = [];
  const colors = ['#1F3A5F', '#C41E3A', '#2E7D32', '#FFC107', '#3A5F8F', '#5b87c0', '#9b1830', '#fbbf24', '#34d399', '#a78bfa', '#fb923c', '#06b6d4', '#ec4899'];
  rows.forEach((row, i) => {
    const portion = row.cozuldu / totalCozuldu;
    const angle = portion * Math.PI * 2;
    const endAngle = currAngle + angle;
    const x1 = cx + r * Math.cos(currAngle), y1 = cy + r * Math.sin(currAngle);
    const x2 = cx + r * Math.cos(endAngle), y2 = cy + r * Math.sin(endAngle);
    const large = angle > Math.PI ? 1 : 0;
    const color = colors[i % colors.length];
    slices.push(`<path d="M ${x1.toFixed(2)} ${y1.toFixed(2)} A ${r} ${r} 0 ${large} 1 ${x2.toFixed(2)} ${y2.toFixed(2)}" stroke="${color}" stroke-width="${sw}" fill="none" opacity="${0.5 + (row.pct/100)*0.5}"></path>`);
    currAngle = endAngle;
  });

  const legend = rows.slice(0, 6).map((r, i) => `
    <div class="flex items-center gap-2 text-xs">
      <span class="inline-block w-3 h-3 rounded" style="background:${colors[i % colors.length]};opacity:${0.5 + (r.pct/100)*0.5}"></span>
      <span class="truncate">${topicLabel(r.k)}</span>
      <span class="text-slate-500 ml-auto">${r.pct}%</span>
    </div>
  `).join('');

  return `
    <div class="flex items-center gap-3">
      <svg viewBox="0 0 200 200" width="200" height="200">
        ${slices.join('')}
        <text x="100" y="95" text-anchor="middle" font-size="22" font-weight="bold" fill="currentColor">%${Math.round(totalCozuldu>0 ? rows.reduce((s,r)=>s+r.dogru,0)/totalCozuldu*100 : 0)}</text>
        <text x="100" y="115" text-anchor="middle" font-size="11" fill="#6c757d">doğruluk</text>
      </svg>
      <div class="flex-1 space-y-1 min-w-0">${legend}</div>
    </div>
  `;
}

// Line chart (son N kart doğruluk trendi)
function lineChart(answers) {
  if (answers.length === 0) return '<p class="text-slate-500 text-sm">Veri yok</p>';
  const W = 360, H = 140, P = 25;
  const dataPoints = answers.map((a, i) => ({ x: P + (i / Math.max(1, answers.length - 1)) * (W - 2 * P), y: H - P - a.dogruluk * (H - 2 * P) }));
  const path = dataPoints.map((p, i) => (i === 0 ? 'M' : 'L') + ` ${p.x.toFixed(1)} ${p.y.toFixed(1)}`).join(' ');
  const avgPct = Math.round(answers.reduce((s,a)=>s+a.dogruluk,0) / answers.length * 100);

  return `
    <svg viewBox="0 0 ${W} ${H}" width="100%" height="${H}">
      <!-- grid -->
      <line x1="${P}" y1="${P}" x2="${P}" y2="${H-P}" stroke="currentColor" stroke-width="0.5" opacity="0.3"/>
      <line x1="${P}" y1="${H-P}" x2="${W-P}" y2="${H-P}" stroke="currentColor" stroke-width="0.5" opacity="0.3"/>
      <text x="${P-2}" y="${P+4}" font-size="9" text-anchor="end" fill="#6c757d">100%</text>
      <text x="${P-2}" y="${H-P+4}" font-size="9" text-anchor="end" fill="#6c757d">0%</text>
      <text x="${W-P}" y="${H-P+15}" font-size="9" text-anchor="end" fill="#6c757d">son</text>
      <text x="${P}" y="${H-P+15}" font-size="9" text-anchor="start" fill="#6c757d">eski</text>
      <!-- avg line -->
      <line x1="${P}" y1="${H-P - (avgPct/100)*(H-2*P)}" x2="${W-P}" y2="${H-P - (avgPct/100)*(H-2*P)}" stroke="#2E7D32" stroke-dasharray="4 4" stroke-width="1" opacity="0.5"/>
      <text x="${W-P-2}" y="${H-P - (avgPct/100)*(H-2*P)-3}" font-size="9" text-anchor="end" fill="#2E7D32">ort %${avgPct}</text>
      <!-- line -->
      <path d="${path}" stroke="#C41E3A" stroke-width="2" fill="none"/>
      <!-- points -->
      ${dataPoints.map(p => `<circle cx="${p.x.toFixed(1)}" cy="${p.y.toFixed(1)}" r="2.5" fill="#C41E3A"/>`).join('')}
    </svg>
  `;
}
