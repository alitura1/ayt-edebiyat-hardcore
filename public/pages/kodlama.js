// REV21 — Yazar Hafıza Kodlama (görsel/işitsel mnemonic) sözlük + kodlamadan quiz
import { Data, slugify, periodTheme } from '../lib/data.js';

function esc(s) {
  return String(s || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

const PRIO_ORDER = ['ÇOK YÜKSEK', 'YÜKSEK', 'ORTA', 'DÜŞÜK', 'İHMAL'];
const PRIO_META = {
  'ÇOK YÜKSEK': { emoji: '🔴', cls: 'text-accent-700 dark:text-accent-200' },
  'YÜKSEK':     { emoji: '🟠', cls: 'text-warn-700 dark:text-warn-200' },
  'ORTA':       { emoji: '🟡', cls: 'text-primary-700 dark:text-primary-100' },
  'DÜŞÜK':      { emoji: '🟢', cls: 'text-slate-600 dark:text-slate-300' },
  'İHMAL':      { emoji: '⚪', cls: 'text-slate-500' },
};

export async function renderKodlama() {
  const authors = (await Data.authors()) || [];
  const coded = authors.filter(a => a.kodlama && a.kodlama.sahne);

  // Öncelik kovasına göre grupla (en önemliden aza), her kova soru_sayisi azalan
  const byPrio = {};
  for (const a of coded) {
    const p = PRIO_ORDER.includes(a.priority_2026) ? a.priority_2026 : 'DÜŞÜK';
    (byPrio[p] = byPrio[p] || []).push(a);
  }
  for (const p of Object.keys(byPrio)) {
    byPrio[p].sort((x, y) => (y.soru_sayisi || 0) - (x.soru_sayisi || 0));
  }
  const donemSet = [...new Set(coded.map(a => a.donem).filter(Boolean))];

  window.__pageSetup = () => {
    const q = document.getElementById('kodSearch');
    const pf = document.getElementById('kodPrio');
    const apply = () => {
      const term = (q && q.value || '').toLowerCase().trim();
      const pfv = (pf && pf.value) || 'hepsi';
      document.querySelectorAll('[data-kod-row]').forEach(r => {
        const hay = r.dataset.kodRow.toLowerCase();
        const show = (!term || hay.includes(term)) && (pfv === 'hepsi' || r.dataset.prio === pfv);
        r.style.display = show ? '' : 'none';
      });
      document.querySelectorAll('[data-prio-block]').forEach(b => {
        const vis = b.querySelectorAll('[data-kod-row]:not([style*="display: none"])').length;
        b.style.display = vis ? '' : 'none';
      });
    };
    if (q) q.addEventListener('input', apply);
    if (pf) pf.addEventListener('change', apply);
  };

  if (!coded.length) {
    return `<div class="text-center py-12 text-slate-500">Henüz hafıza kodlaması eklenmemiş.</div>`;
  }

  return `
    <header class="mb-5">
      <h1 class="text-3xl font-bold mb-1">🧠 Hafıza Kodlama</h1>
      <p class="text-slate-600 dark:text-slate-400 text-sm">
        Yazarı sesçil bir kanca + canlı bir sahneyle kodla, eserlerini ezberlemeden tut.
        <strong>${coded.length} yazar</strong> · en önemliden aza sıralı. Sahneyi oku, çözümü kapalı tut, kendini sına.
      </p>
    </header>

    <div class="flex flex-wrap gap-2 mb-3 items-center">
      <input id="kodSearch" type="search" placeholder="Yazar / ipucu ara: atılgan, çöl, saat..."
        class="flex-1 min-w-[200px] px-3 py-2 rounded-md border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900" />
      <select id="kodPrio" class="px-3 py-2 rounded-md border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 text-sm">
        <option value="hepsi">Tüm öncelikler</option>
        ${PRIO_ORDER.filter(p => byPrio[p]).map(p => `<option value="${p}">${PRIO_META[p].emoji} ${p}</option>`).join('')}
      </select>
      <a href="#/quiz?kodlama=hepsi&sayi=20" class="px-4 py-2 rounded-md bg-accent-500 text-white font-bold text-sm hover:bg-accent-700">
        🎯 Tüm kodlamalardan quiz
      </a>
    </div>
    ${donemSet.length > 1 ? `
      <div class="flex flex-wrap gap-1.5 mb-5 text-xs">
        ${donemSet.map(d => {
          const th = periodTheme(d);
          return `<a href="#/quiz?kodlama=${encodeURIComponent(d)}&sayi=12" class="px-2.5 py-1 rounded-full ${th.bg} ${th.text} font-semibold hover:opacity-80">🎯 ${th.label}</a>`;
        }).join('')}
      </div>` : ''}

    ${PRIO_ORDER.filter(p => byPrio[p]).map(p => {
      const meta = PRIO_META[p];
      return `
        <section data-prio-block class="mb-6">
          <h2 class="text-sm font-bold mb-3 ${meta.cls} uppercase tracking-wider">
            ${meta.emoji} ${p} <span class="text-slate-400 font-normal normal-case">· ${byPrio[p].length} yazar</span>
          </h2>
          <div class="grid sm:grid-cols-2 gap-3">
            ${byPrio[p].map(a => {
              const k = a.kodlama;
              const slug = slugify(a.name);
              return `
                <div data-kod-row="${esc(a.name)} ${esc(k.ad_cagrisimi || '')} ${esc(k.sahne || '')}" data-prio="${p}"
                     class="rounded-xl p-3.5 bg-gradient-to-br from-purple-500/10 via-fuchsia-500/10 to-violet-500/10 border-2 border-purple-400/40 dark:border-purple-400/30">
                  <div class="flex items-center gap-2 mb-1.5">
                    <span class="text-xl">${k.emoji || '🧠'}</span>
                    <a href="#/yazarlar/${slug}" class="font-bold text-purple-800 dark:text-purple-200 hover:underline">${esc(a.name)}</a>
                    <span class="ml-auto text-[10px] text-slate-400">${a.soru_sayisi || 0} soru</span>
                  </div>
                  ${k.ad_cagrisimi ? `<div class="text-[11px] font-mono text-purple-700 dark:text-purple-300 mb-1.5">${esc(k.ad_cagrisimi)}</div>` : ''}
                  <p class="text-sm leading-relaxed text-slate-800 dark:text-slate-100 mb-1.5">🎬 ${esc(k.sahne)}</p>
                  ${k.cozum ? `
                    <details>
                      <summary class="text-xs font-bold text-purple-700 dark:text-purple-300 cursor-pointer">🔑 Çözümü göster</summary>
                      <p class="mt-1 text-xs text-slate-600 dark:text-slate-300 leading-relaxed">${esc(k.cozum)}</p>
                    </details>` : ''}
                </div>`;
            }).join('')}
          </div>
        </section>`;
    }).join('')}
  `;
}
