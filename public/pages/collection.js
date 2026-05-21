// REV5 — Koleksiyonum: yazar/kişi mastery seviyesi gridi
import { Data, periodTheme, topicLabel, slugify, getDataSubject } from '../lib/data.js';
import { loadState } from '../lib/store.js';
import { authorMastery, LEVELS, masterySummary } from '../lib/mastery.js';

export async function renderCollection() {
  const authors = await Data.authors();
  const cards = await Data.cards();
  const state = loadState();
  const allCards = [...cards, ...state.custom_kartlar];
  const isTarih = getDataSubject() === 'tarih';

  const summary = masterySummary(authors, allCards, state);
  const pct = Math.round((summary.counts.ogrendin / summary.total) * 100);

  // Yazarları mastery + soru sayısına göre sırala (öğrenildi en üste, soru çok olan üste)
  const ranked = authors.map(a => {
    const lvl = summary.byAuthor[slugify(a.name)];
    return { ...a, mastery: lvl };
  }).sort((a, b) => {
    if (a.mastery !== b.mastery) return LEVELS[b.mastery].rank - LEVELS[a.mastery].rank;
    return b.soru_sayisi - a.soru_sayisi;
  });

  window.__pageSetup = () => {
    const lvlF = document.getElementById('lvlFilter');
    const donF = document.getElementById('donemFilter');
    const srch = document.getElementById('collSearch');

    function run() {
      const lf = lvlF.value;
      const df = donF.value;
      const term = srch.value.toLowerCase().trim();
      document.querySelectorAll('[data-author-card]').forEach(el => {
        const lvl = el.dataset.mastery;
        const donem = el.dataset.donem;
        const name = el.dataset.authorCard.toLowerCase();
        let show = true;
        if (lf && lf !== 'hepsi' && lvl !== lf) show = false;
        if (df && df !== 'hepsi' && donem !== df) show = false;
        if (term && !name.includes(term)) show = false;
        el.style.display = show ? '' : 'none';
      });
    }
    lvlF?.addEventListener('change', run);
    donF?.addEventListener('change', run);
    srch?.addEventListener('input', run);
  };

  // Unique dönem listesi (filtreye)
  const donems = [...new Set(authors.map(a => a.donem || a.konular[0]).filter(Boolean))];

  return `
    <header class="mb-6">
      <h1 class="text-3xl font-bold mb-1">🎴 Koleksiyonum</h1>
      <p class="text-slate-600 dark:text-slate-400 text-sm">
        ${summary.total} yazarın kaç tanesini tanıyorsun? Sürekli karşına çıka çıka ezberlemeden ezberlersin.
      </p>
    </header>

    <!-- Özet kart -->
    <div class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-2xl p-5 mb-5">
      <div class="grid grid-cols-3 gap-3 mb-4">
        <div class="text-center p-3 rounded-lg bg-slate-100 dark:bg-slate-800">
          <div class="text-2xl">${LEVELS.tanisilmadi.emoji}</div>
          <div class="text-xl font-bold">${summary.counts.tanisilmadi}</div>
          <div class="text-xs text-slate-500">Tanışmadın</div>
        </div>
        <div class="text-center p-3 rounded-lg bg-warn-500/10">
          <div class="text-2xl">${LEVELS.tanidin.emoji}</div>
          <div class="text-xl font-bold text-warn-500">${summary.counts.tanidin}</div>
          <div class="text-xs text-slate-500">Tanıdın</div>
        </div>
        <div class="text-center p-3 rounded-lg bg-ok-500/10">
          <div class="text-2xl">${LEVELS.ogrendin.emoji}</div>
          <div class="text-xl font-bold text-ok-500">${summary.counts.ogrendin}</div>
          <div class="text-xs text-slate-500">Öğrendin</div>
        </div>
      </div>
      <div class="text-xs text-slate-500 mb-1">Öğrendin ilerlemesi: ${summary.counts.ogrendin}/${summary.total} (%${pct})</div>
      <div class="h-2 bg-slate-200 dark:bg-slate-800 rounded-full overflow-hidden">
        <div class="h-full bg-ok-500 transition-all" style="width:${pct}%"></div>
      </div>
    </div>

    <!-- Filtreler -->
    <div class="flex gap-2 mb-4 flex-wrap">
      <input id="collSearch" type="search" placeholder="Ara: Fuzuli, Halit Ziya..."
             class="flex-1 min-w-[180px] px-3 py-2 rounded-md border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900" />
      <select id="lvlFilter" class="px-3 py-2 rounded-md border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900">
        <option value="hepsi">Tüm seviyeler</option>
        <option value="tanisilmadi">${LEVELS.tanisilmadi.emoji} Tanışmadın</option>
        <option value="tanidin">${LEVELS.tanidin.emoji} Tanıdın</option>
        <option value="ogrendin">${LEVELS.ogrendin.emoji} Öğrendin</option>
      </select>
      <select id="donemFilter" class="px-3 py-2 rounded-md border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900">
        <option value="hepsi">Tüm dönemler</option>
        ${donems.map(d => `<option value="${d}">${periodTheme(d).label}</option>`).join('')}
      </select>
    </div>

    <!-- Grid -->
    <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
      ${ranked.map(a => {
        const th = periodTheme(a.donem || a.konular[0]);
        const lvl = LEVELS[a.mastery];
        return `
          <a href="#/yazarlar/${slugify(a.name)}"
             data-author-card="${a.name}" data-mastery="${a.mastery}" data-donem="${a.donem || a.konular[0]}"
             class="block rounded-xl border-2 border-slate-200 dark:border-slate-700 ${th.bg} p-3 hover:shadow-md transition ${lvl.cls}">
            <div class="flex items-center justify-between mb-1">
              <span class="text-lg">${lvl.emoji}</span>
              <span class="text-[10px] uppercase tracking-wider ${th.text} font-bold">${a.soru_sayisi} soru</span>
            </div>
            <div class="font-semibold ${th.text} text-sm leading-tight mb-1 line-clamp-2 min-h-[2.5rem]">${a.name}</div>
            <div class="text-[10px] ${th.text} opacity-80 line-clamp-1">${th.label} · ${a.pozisyon || ''}</div>
          </a>
        `;
      }).join('')}
    </div>
  `;
}
