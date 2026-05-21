import { Data, getDataSubject } from '../lib/data.js';

export async function renderPredictions() {
  const p = await Data.predictions();
  const isTarih = getDataSubject() === 'tarih';
  return `
    <header class="mb-6">
      <h1 class="text-3xl font-bold mb-1">🔮 2026 ${isTarih ? 'AYT Tarih ' : ''}Tahminleri</h1>
      <p class="text-slate-600 dark:text-slate-400 text-sm">8 yıllık trend + periyodik desen + boşluk haritası. Mutlak değil, olasılık temelli.</p>
    </header>

    <section class="mb-8">
      <h2 class="text-xl font-bold mb-3">Konu Bazlı Tahmin</h2>
      <div class="overflow-x-auto bg-white dark:bg-slate-900 rounded-lg border border-slate-200 dark:border-slate-700">
        <table class="w-full text-sm">
          <thead class="bg-primary-700 text-white">
            <tr>
              <th class="text-left px-3 py-2">Konu</th>
              <th class="text-center px-2 py-2">8 Yıl</th>
              <th class="text-center px-2 py-2">2026 Tahmin</th>
              <th class="text-left px-2 py-2">Güvence</th>
            </tr>
          </thead>
          <tbody>
            ${p.konular.map(k => `
              <tr class="border-t border-slate-200 dark:border-slate-800">
                <td class="px-3 py-2 font-semibold">${k.ad}</td>
                <td class="text-center px-2 py-2 text-slate-500 text-xs">${k.frekans_8yil}</td>
                <td class="text-center px-2 py-2 font-bold">${k.tahmin}</td>
                <td class="px-2 py-2 text-xs ${guvenColor(k.guven)}">${k.guven}</td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>
    </section>

    <section class="mb-8 grid md:grid-cols-3 gap-4">
      <div class="bg-ok-500/10 border-2 border-ok-500/30 rounded-lg p-4">
        <h3 class="font-bold mb-2 text-ok-500">🟢 Çok Yüksek (2026'da güçlü)</h3>
        <ul class="text-sm space-y-1">
          ${p.yazarlar_cok_yuksek.map(y => `<li>• <strong>${y.ad}</strong> — ${y.not_}</li>`).join('')}
        </ul>
      </div>
      <div class="bg-warn-500/10 border-2 border-warn-500/30 rounded-lg p-4">
        <h3 class="font-bold mb-2 text-warn-500">🟡 Orta olasılık</h3>
        <ul class="text-sm space-y-1">
          ${p.yazarlar_orta.map(y => `<li>• ${y}</li>`).join('')}
        </ul>
      </div>
      <div class="bg-accent-500/10 border-2 border-accent-500/30 rounded-lg p-4">
        <h3 class="font-bold mb-2 text-accent-500">🔴 BOŞLUK ADAYI (özetinde var, sorulmadı)</h3>
        <ul class="text-sm space-y-1">
          ${p.bosluk_adaylari.map(b => `<li>• <strong>${b.ad}</strong> — ${b.not_}</li>`).join('')}
        </ul>
      </div>
    </section>

    ${p.periyodik_desen ? `
    <section class="mb-8">
      <h2 class="text-xl font-bold mb-3">Periyodik Desen Analizi (2-3 yıllık döngüler)</h2>
      <p class="text-sm text-slate-500 mb-3">ÖSYM bazı konuları periyodik olarak boş bırakıp tekrar getiriyor. Bu desenler 2026 tahminlerinin temelidir.</p>
      <div class="overflow-x-auto bg-white dark:bg-slate-900 rounded-lg border border-slate-200 dark:border-slate-700">
        <table class="w-full text-sm">
          <thead class="bg-primary-700 text-white">
            <tr>
              <th class="text-left px-3 py-2">Konu</th>
              <th class="text-left px-2 py-2">Periyot</th>
              <th class="text-center px-2 py-2">Son Geldiği</th>
              <th class="text-left px-2 py-2">2026 Tahmin</th>
            </tr>
          </thead>
          <tbody>
            ${p.periyodik_desen.map(d => `
              <tr class="border-t border-slate-200 dark:border-slate-800">
                <td class="px-3 py-2 font-semibold">${d.konu}</td>
                <td class="px-2 py-2 text-xs">${d.periyot}</td>
                <td class="text-center px-2 py-2 text-xs text-slate-500">${d.son_geldigi}</td>
                <td class="px-2 py-2 text-xs ${guvenColor(d.tahmin)}">${d.tahmin}</td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>
    </section>` : ''}

    ${p.yazar_son_yil_haritasi ? `
    <section class="mb-8">
      <h2 class="text-xl font-bold mb-3">Yazar — Son Geldiği Yıl Haritası</h2>
      <p class="text-sm text-slate-500 mb-3">Uzun süre çıkmamış favori yazarlar 2026 için yüksek aday. Az önce çıkmış olanlar düşük olası.</p>
      <div class="overflow-x-auto bg-white dark:bg-slate-900 rounded-lg border border-slate-200 dark:border-slate-700">
        <table class="w-full text-sm">
          <thead class="bg-primary-700 text-white">
            <tr>
              <th class="text-left px-3 py-2">Yazar</th>
              <th class="text-center px-2 py-2">Son Geldiği</th>
              <th class="text-center px-2 py-2">Boş Yıl</th>
              <th class="text-left px-2 py-2">2026 Öncelik</th>
            </tr>
          </thead>
          <tbody>
            ${p.yazar_son_yil_haritasi.map(y => `
              <tr class="border-t border-slate-200 dark:border-slate-800">
                <td class="px-3 py-2 font-semibold">${y.yazar}</td>
                <td class="text-center px-2 py-2 text-slate-500">${y.son_geldigi}</td>
                <td class="text-center px-2 py-2 font-bold ${y.bos_yil >= 3 ? 'text-accent-500' : y.bos_yil >= 1 ? 'text-warn-500' : 'text-slate-500'}">${y.bos_yil} yıl</td>
                <td class="px-2 py-2 text-xs ${guvenColor(y.oncelik)}">${y.oncelik}</td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>
    </section>` : ''}

    ${p.bosluk_haritasi ? `
    <section>
      <h2 class="text-xl font-bold mb-3">Alt Başlık Boşluk Haritası</h2>
      <p class="text-sm text-slate-500 mb-3">Konuya çalışırken bu alt başlıklara özellikle bak — 8 yılda hiç sorulmamış ama MEBİ özetinde var.</p>
      <div class="overflow-x-auto bg-white dark:bg-slate-900 rounded-lg border border-slate-200 dark:border-slate-700">
        <table class="w-full text-sm">
          <thead class="bg-primary-700 text-white">
            <tr>
              <th class="text-left px-3 py-2">Konu</th>
              <th class="text-left px-2 py-2">Sorulmamış Alt Başlıklar</th>
              <th class="text-center px-2 py-2">Tahmin Gücü</th>
            </tr>
          </thead>
          <tbody>
            ${p.bosluk_haritasi.map(b => `
              <tr class="border-t border-slate-200 dark:border-slate-800">
                <td class="px-3 py-2 font-semibold">${b.konu}</td>
                <td class="px-2 py-2 text-sm">${b.alt_basliklar}</td>
                <td class="text-center px-2 py-2 text-xs ${guvenColor(b.guc)}">${b.guc}</td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>
    </section>` : ''}
  `;
}

function guvenColor(g) {
  if (!g) return '';
  if (g.includes('KESİN') || g.includes('ÇOK YÜKSEK')) return 'text-ok-500 font-bold';
  if (g.includes('YÜKSEK')) return 'text-ok-500';
  if (g.includes('ORTA')) return 'text-warn-500';
  return 'text-slate-500';
}
