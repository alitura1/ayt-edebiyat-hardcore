import { Data, topicLabel, slugify } from '../lib/data.js';

export async function renderAuthorList() {
  const authors = await Data.authors();
  const recurring = authors.filter(a => a.soru_sayisi >= 2);
  const single = authors.filter(a => a.soru_sayisi === 1);

  window.__pageSetup = () => {
    const q = document.getElementById('authorSearch');
    const filter = document.getElementById('authorFilter');
    function run() {
      const term = q.value.toLowerCase().trim();
      const f = filter.value;
      document.querySelectorAll('[data-author-row]').forEach(row => {
        const name = row.dataset.authorRow.toLowerCase();
        const konu = row.dataset.konu;
        const grup = row.dataset.grup;
        let show = true;
        if (term && !name.includes(term)) show = false;
        if (f && f !== 'hepsi' && grup !== f) show = false;
        row.style.display = show ? '' : 'none';
      });
    }
    q?.addEventListener('input', run);
    filter?.addEventListener('change', run);
  };

  return `
    <header class="mb-6">
      <h1 class="text-3xl font-bold mb-1">👤 Yazar Veritabanı</h1>
      <p class="text-slate-600 dark:text-slate-400 text-sm">
        ${authors.length} yazar / 192 soru — ${recurring.length} tekrar, ${single.length} tek sefer.
      </p>
    </header>
    <div class="flex gap-2 mb-4 flex-wrap">
      <input id="authorSearch" type="search" placeholder="Yazar ara: Fuzuli, Yakup Kadri..."
             class="flex-1 min-w-[200px] px-3 py-2 rounded-md border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900" />
      <select id="authorFilter" class="px-3 py-2 rounded-md border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900">
        <option value="hepsi">Hepsi</option>
        <option value="A">Tablo A — Tekrar edenler (2+)</option>
        <option value="B">Tablo B — Tek sefer</option>
      </select>
    </div>
    <div class="overflow-x-auto bg-white dark:bg-slate-900 rounded-lg border border-slate-200 dark:border-slate-700">
      <table class="w-full text-sm">
        <thead class="bg-primary-700 text-white">
          <tr>
            <th class="text-left px-3 py-2">Yazar</th>
            <th class="text-center px-2 py-2">Soru</th>
            <th class="text-left px-2 py-2">Yıllar</th>
            <th class="text-left px-2 py-2">Konu</th>
            <th class="text-center px-2 py-2">MEBİ</th>
            <th class="text-left px-2 py-2">Bilinmesi Gereken Diğer Eserleri</th>
          </tr>
        </thead>
        <tbody>
          ${authors.map(a => `
            <tr data-author-row="${a.name}" data-konu="${a.konular[0] || ''}" data-grup="${a.soru_sayisi >= 2 ? 'A' : 'B'}"
                class="border-t border-slate-200 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-800/50">
              <td class="px-3 py-2 font-semibold">
                <a href="#/yazarlar/${slugify(a.name)}" class="text-primary-700 dark:text-primary-100 hover:underline">${a.name}</a>
              </td>
              <td class="text-center px-2 py-2 ${a.soru_sayisi >= 5 ? 'font-bold text-accent-500' : ''}">${a.soru_sayisi}</td>
              <td class="px-2 py-2 text-slate-600 dark:text-slate-400">${a.yillar.join(', ')}</td>
              <td class="px-2 py-2 text-xs text-slate-500">${a.konular.map(topicLabel).join(', ')}</td>
              <td class="text-center px-2 py-2 text-xs text-slate-500">${a.mebi_sayfa || '—'}</td>
              <td class="px-2 py-2 text-xs text-slate-600 dark:text-slate-400">${a.diger_eserler || '—'}</td>
            </tr>
          `).join('')}
        </tbody>
      </table>
    </div>
  `;
}

export async function renderAuthorDetail(slug) {
  const authors = await Data.authors();
  const a = authors.find(x => slugify(x.name) === slug);
  if (!a) return `<p>Yazar bulunamadı.</p><a href="#/yazarlar" class="text-primary-700 underline">← Yazar listesine dön</a>`;
  return `
    <nav class="text-sm mb-3 text-slate-500"><a href="#/yazarlar" class="hover:underline">← Yazar listesi</a></nav>
    <header class="mb-6">
      <h1 class="text-3xl font-bold text-primary-700 dark:text-primary-100">${a.name}</h1>
      <p class="text-sm text-slate-500 mt-1">
        ${a.soru_sayisi} soruda geçti · ${a.yillar.join(', ')}
      </p>
    </header>
    <div class="grid md:grid-cols-2 gap-4 mb-6">
      <div class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg p-4">
        <h3 class="font-bold mb-2">Konu / Dönem</h3>
        <p class="text-sm">${a.konular.map(topicLabel).join(', ')}</p>
        ${a.mebi_sayfa ? `<div class="mebi-box mt-3"><strong>📘 MEBİ Konu Özeti</strong> → ayt-tde.pdf sayfa <strong>${a.mebi_sayfa}</strong></div>` : ''}
      </div>
      <div class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg p-4">
        <h3 class="font-bold mb-2">Bilinmesi Gereken Diğer Eserleri (2026 aday)</h3>
        <p class="text-sm text-slate-600 dark:text-slate-400">${a.diger_eserler || '—'}</p>
      </div>
    </div>
    ${a.occurrences && a.occurrences.length ? `
      <div class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg p-4">
        <h3 class="font-bold mb-3">Çıkmış Soru Geçmişi</h3>
        <ul class="space-y-1 text-sm">
          ${a.occurrences.map(o => `
            <li class="flex items-center gap-2 border-b border-slate-100 dark:border-slate-800 pb-1">
              <span class="bg-primary-50 dark:bg-primary-900/50 text-primary-700 dark:text-primary-100 text-xs font-bold px-2 py-0.5 rounded">${o.year}</span>
              <span>Soru ${o.qno}</span>
              <span class="text-slate-500 text-xs">· ${topicLabel(o.topic)}</span>
            </li>
          `).join('')}
        </ul>
      </div>
    ` : ''}
  `;
}
