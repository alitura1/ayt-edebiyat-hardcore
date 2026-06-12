// REV6 M5 — Edebi gruplar / hanedanlar: liste + detay
import { Data, periodTheme, slugify, getDataSubject } from '../lib/data.js';
import { loadState } from '../lib/store.js';
import { authorMastery, LEVELS } from '../lib/mastery.js';

export async function renderGroupList() {
  const groups = await Data.groups();
  const isTarih = getDataSubject() === 'tarih';
  const headerTitle = isTarih ? '🏛️ Hanedanlar & Gruplar' : '👥 Edebi Gruplar';
  const headerSub = isTarih
    ? `${groups.length} grup · Osmanlı Hanedanı, Selçuklu Sultanları, Anadolu Beylikleri, Kuvayımilliye Kahramanları, İttihat-Terakki ve İlk Türk Devletleri.`
    : `${groups.length} grup · Beş Hececiler, Garip, İkinci Yeni, Servet-i Fünun ve daha fazlası. ÖSYM tuzaklarının çözüldüğü yer.`;

  return `
    <header class="mb-5">
      <h1 class="text-3xl font-bold mb-1">${headerTitle}</h1>
      <p class="text-slate-600 dark:text-slate-400 text-sm">${headerSub}</p>
    </header>

    <div class="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
      ${groups.map(g => {
        const th = periodTheme(g.donem);
        return `
          <a href="#/grup/${g.slug}" class="block rounded-2xl border-2 border-slate-200 dark:border-slate-700 ${th.bg} p-5 hover:shadow-md transition">
            <div class="flex items-center gap-2 mb-2">
              <span class="text-xs font-bold ${th.text} uppercase tracking-wider">${th.label}</span>
              <span class="text-xs ${th.text} opacity-70">· ${g.kurulus}</span>
            </div>
            <h3 class="text-lg font-bold ${th.text} mb-2">${g.ad}</h3>
            <div class="text-xs ${th.text} opacity-90 mb-2 line-clamp-3">${g.manifesto}</div>
            <div class="text-xs ${th.text} opacity-70">${g.uyeler.length} üye</div>
          </a>
        `;
      }).join('')}
    </div>
  `;
}

export async function renderGroupDetail(slug) {
  const groups = await Data.groups();
  const authors = await Data.authors();
  const cards = await Data.cards();
  const state = loadState();
  const allCards = [...cards, ...state.custom_kartlar];

  const g = groups.find(x => x.slug === slug);
  if (!g) return `<p>Grup bulunamadı.</p><a href="#/gruplar" class="text-primary-700 underline">← Gruplar listesine dön</a>`;

  const th = periodTheme(g.donem);

  // Üyelerin profillerini eşleştir
  const uyeProfiller = g.uyeler.map(name => {
    const a = authors.find(x => x.name === name);
    if (!a) return { name, slug: null, mevcut: false };
    return {
      name,
      slug: slugify(name),
      mevcut: true,
      anekdot: a.anekdot,
      pozisyon: a.pozisyon,
      donem: a.donem,
      soru_sayisi: a.soru_sayisi,
      mastery: authorMastery(a.name, allCards, state),
    };
  });

  return `
    <nav class="text-sm mb-3 text-slate-500"><a href="#/gruplar" class="hover:underline">← Gruplar</a></nav>

    <!-- HEADER -->
    <div class="rounded-2xl overflow-hidden ${th.bg} border-2 border-slate-200 dark:border-slate-700 mb-5">
      <div class="p-6">
        <div class="flex items-center gap-2 mb-2">
          <span class="text-xs font-bold uppercase tracking-wider ${th.text} opacity-80">${th.label} · ${g.kurulus}</span>
        </div>
        <h1 class="text-3xl md:text-4xl font-bold ${th.text} mb-3">${g.ad}</h1>
        <p class="text-sm ${th.text} leading-relaxed">${g.manifesto}</p>
      </div>
    </div>

    <!-- REV21 — GRUP HAFIZA KODLAMASI (üyelik ipucu) -->
    ${g.grup_kodlama ? `
      <div class="mb-5 rounded-xl p-4 bg-gradient-to-br from-purple-500/10 via-fuchsia-500/10 to-violet-500/10 border-2 border-purple-400/40 dark:border-purple-400/30">
        <div class="text-xs font-bold uppercase tracking-wider text-purple-700 dark:text-purple-300 mb-1.5">🧠 Hafıza Kodlaması (üyeler)</div>
        <p class="text-sm leading-relaxed text-slate-800 dark:text-slate-100">${g.grup_kodlama}</p>
      </div>
    ` : ''}

    <!-- ÜYELER -->
    <div class="mb-5">
      <h2 class="text-lg font-bold mb-3">👥 Üyeler (${uyeProfiller.length})</h2>
      <div class="grid sm:grid-cols-2 gap-3">
        ${uyeProfiller.map(u => {
          const uTh = u.donem ? periodTheme(u.donem) : th;
          const lvl = u.mevcut ? LEVELS[u.mastery] : null;
          return u.mevcut ? `
            <a href="#/yazarlar/${u.slug}" class="block rounded-xl border-2 border-slate-200 dark:border-slate-700 ${uTh.bg} p-3 hover:shadow-md transition">
              <div class="flex items-center justify-between mb-1">
                <span class="font-bold ${uTh.text}">${u.name}</span>
                <span title="${lvl.label}">${lvl.emoji}</span>
              </div>
              <div class="text-[10px] ${uTh.text} opacity-80 mb-1">${u.pozisyon || '—'} · ${u.soru_sayisi} soru</div>
              ${u.anekdot ? `<div class="text-xs ${uTh.text} opacity-90 line-clamp-2 italic">"${u.anekdot}"</div>` : ''}
            </a>
          ` : `
            <div class="block rounded-xl border-2 border-dashed border-slate-300 dark:border-slate-700 p-3 opacity-60">
              <div class="font-bold text-slate-500">${u.name}</div>
              <div class="text-[10px] text-slate-400">(veritabanında profil yok)</div>
            </div>
          `;
        }).join('')}
      </div>
    </div>

    <!-- ORTAK ÖZELLİKLER -->
    <div class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg p-4 mb-4">
      <h3 class="font-bold mb-3 text-sm">📋 Ortak Özellikleri</h3>
      <ul class="space-y-1.5 text-sm">
        ${g.ortak_ozellikler.map(o => `<li class="flex gap-2"><span class="text-primary-700 dark:text-primary-100">▸</span><span>${o}</span></li>`).join('')}
      </ul>
    </div>

    <!-- MARKA ESERLER -->
    ${g.marka_eserler && g.marka_eserler.length ? `
      <div class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg p-4 mb-4">
        <h3 class="font-bold mb-3 text-sm">📚 Marka Eserler</h3>
        <ul class="space-y-1 text-sm">
          ${g.marka_eserler.map(e => `<li class="flex gap-2"><span class="text-accent-500">📖</span><span>${e}</span></li>`).join('')}
        </ul>
      </div>
    ` : ''}

    <!-- KLASİK TUZAK -->
    ${g.klasik_tuzak ? `
      <div class="tuzak-box mb-4">
        <strong>⚠ KLASİK ÖSYM TUZAĞI</strong>
        <div class="mt-1 text-sm">${g.klasik_tuzak}</div>
      </div>
    ` : ''}
  `;
}
