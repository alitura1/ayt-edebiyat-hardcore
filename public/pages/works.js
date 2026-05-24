// REV6 M4 — Eserler / Olaylar liste + detay
import { Data, periodTheme, slugify, getDataSubject } from '../lib/data.js';

export async function renderWorkList() {
  // TYT Fen'de eser/olay yok — empty state
  if (getDataSubject() === 'fen') {
    return `
      <section class="max-w-2xl mx-auto py-12 px-4 text-center">
        <div class="text-5xl mb-4">⚗</div>
        <h1 class="text-2xl font-bold mb-2">TYT Fen'de eser/olay listesi yok</h1>
        <p class="text-slate-600 dark:text-slate-400 mb-6">Fen Bilimleri sayısal-uygulamalı bir ders. Onun yerine simülasyonlar ve konu sayfalarına geçebilirsin.</p>
        <div class="flex flex-wrap gap-3 justify-center">
          <a href="#/konular" class="inline-block px-5 py-2.5 rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white font-semibold">📚 Konular</a>
          <a href="#/simulasyonlar" class="inline-block px-5 py-2.5 rounded-lg bg-blue-600 hover:bg-blue-700 text-white font-semibold">🔬 Simülasyonlar</a>
        </div>
      </section>
    `;
  }
  const isTarih = getDataSubject() === 'tarih';
  // Tarih moduyla events.json + treaties.json'u "works" şemasına çevir
  let works;
  if (isTarih) {
    const events = await Data.events();
    const treaties = await Data.treaties();
    const eventToWork = e => ({
      title: e.isim,
      slug: e.slug,
      yazar: e.taraflar || '—',
      yazarSlug: 'tarih',
      tur: e.tur === 'savas' ? 'Savaş' : 'Olay',
      donem: e.yil < 1300 ? 'turk_islam' : e.yil < 1453 ? 'osmanli_kurulus' : e.yil < 1595 ? 'osmanli_yukselis' : e.yil < 1792 ? 'osmanli_duraklama' : e.yil < 1922 ? 'osmanli_dagilma' : 'milli_mucadele',
      yil: e.yil,
      cikmis: false,
    });
    const treatyToWork = t => ({
      title: t.isim,
      slug: t.slug,
      yazar: t.taraflar,
      yazarSlug: 'tarih',
      tur: 'Antlaşma',
      donem: t.yil < 1595 ? 'osmanli_yukselis' : t.yil < 1792 ? 'osmanli_duraklama' : t.yil < 1922 ? 'osmanli_dagilma' : 'milli_mucadele',
      yil: t.yil,
      cikmis: false,
    });
    works = [...events.map(eventToWork), ...treaties.map(treatyToWork)].sort((a, b) => a.yil - b.yil);
  } else {
    works = await Data.works();
  }

  window.__pageSetup = () => {
    const srch = document.getElementById('wSearch');
    const turF = document.getElementById('wTurFilter');
    const donF = document.getElementById('wDonemFilter');
    const cikF = document.getElementById('wCikmisFilter');
    function run() {
      const term = srch.value.toLowerCase().trim();
      const tf = turF.value;
      const df = donF.value;
      const cf = cikF.value;
      document.querySelectorAll('[data-work-row]').forEach(row => {
        const t = row.dataset.workRow.toLowerCase();
        const y = row.dataset.yazar.toLowerCase();
        const tur = row.dataset.tur;
        const don = row.dataset.donem;
        const cik = row.dataset.cikmis;
        let show = true;
        if (term && !t.includes(term) && !y.includes(term)) show = false;
        if (tf && tf !== 'hepsi' && tur !== tf) show = false;
        if (df && df !== 'hepsi' && don !== df) show = false;
        if (cf === 'cikmis' && cik !== 'true') show = false;
        row.style.display = show ? '' : 'none';
      });
    }
    srch?.addEventListener('input', run);
    turF?.addEventListener('change', run);
    donF?.addEventListener('change', run);
    cikF?.addEventListener('change', run);
  };

  const turler = [...new Set(works.map(w => w.tur).filter(t => t && t !== '—'))].sort();
  const donems = [...new Set(works.map(w => w.donem))];
  const cikmisN = works.filter(w => w.cikmis).length;

  const headerTitle = isTarih ? '⚔️ Olaylar & Antlaşmalar' : '📚 Eserler';
  const headerSub = isTarih
    ? `${works.length} olay/antlaşma · savaşlar, barış antlaşmaları, kritik tarihî olaylar.`
    : `${works.length} eser · ${cikmisN}'si ÖSYM'de soruldu.`;
  return `
    <header class="mb-5">
      <h1 class="text-3xl font-bold mb-1">${headerTitle}</h1>
      <p class="text-slate-600 dark:text-slate-400 text-sm">${headerSub}</p>
    </header>

    <div class="flex gap-2 mb-4 flex-wrap">
      <input id="wSearch" type="search" placeholder="Eser veya yazar ara: Aşk-ı Memnu, Halit Ziya..."
             class="flex-1 min-w-[200px] px-3 py-2 rounded-md border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900" />
      <select id="wTurFilter" class="px-3 py-2 rounded-md border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900">
        <option value="hepsi">Tüm türler</option>
        ${turler.map(t => `<option value="${t}">${t}</option>`).join('')}
      </select>
      <select id="wDonemFilter" class="px-3 py-2 rounded-md border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900">
        <option value="hepsi">Tüm dönemler</option>
        ${donems.map(d => `<option value="${d}">${periodTheme(d).label}</option>`).join('')}
      </select>
      <select id="wCikmisFilter" class="px-3 py-2 rounded-md border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900">
        <option value="hepsi">Hepsi</option>
        <option value="cikmis">⭐ ÖSYM'de soruldu</option>
      </select>
    </div>

    <div class="overflow-x-auto bg-white dark:bg-slate-900 rounded-lg border border-slate-200 dark:border-slate-700">
      <table class="w-full text-sm">
        <thead class="bg-primary-700 text-white">
          <tr>
            <th class="text-left px-3 py-2">Eser</th>
            <th class="text-left px-2 py-2">Yazar</th>
            <th class="text-left px-2 py-2">Tür</th>
            <th class="text-left px-2 py-2">Dönem</th>
            <th class="text-center px-2 py-2">ÖSYM</th>
          </tr>
        </thead>
        <tbody>
          ${works.map(w => {
            const th = periodTheme(w.donem);
            return `
              <tr data-work-row="${w.title}" data-yazar="${w.yazar}" data-tur="${w.tur}" data-donem="${w.donem}" data-cikmis="${w.cikmis}"
                  class="border-t border-slate-200 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-800/50">
                <td class="px-3 py-2 font-semibold">
                  <a href="#/eserler/${w.slug}-${w.yazarSlug}" class="text-primary-700 dark:text-primary-100 hover:underline">${w.title}</a>
                </td>
                <td class="px-2 py-2">
                  <a href="#/yazarlar/${w.yazarSlug}" class="text-slate-600 dark:text-slate-400 hover:underline">${w.yazar}</a>
                </td>
                <td class="px-2 py-2 text-xs">${w.tur || '—'}</td>
                <td class="px-2 py-2"><span class="inline-flex items-center gap-1 text-[10px] px-2 py-0.5 rounded ${th.bg} ${th.text}"><span class="w-1 h-1 rounded-full ${th.dot}"></span>${th.label}</span></td>
                <td class="text-center px-2 py-2">${w.cikmis ? '⭐' : ''}</td>
              </tr>
            `;
          }).join('')}
        </tbody>
      </table>
    </div>
  `;
}

export async function renderWorkDetail(combinedSlug) {
  // Slug format: workSlug-yazarSlug (eser-yazar) — son tire'den yazar slug'ı al
  const works = await Data.works();
  const authors = await Data.authors();
  // Birden fazla "eser-yazar" eşleşmesi olabilir, tam match dene
  let w = works.find(x => `${x.slug}-${x.yazarSlug}` === combinedSlug);
  // Fallback: sadece slug eşleşmesi
  if (!w) w = works.find(x => x.slug === combinedSlug);
  if (!w) return `<p>Eser bulunamadı.</p><a href="#/eserler" class="text-primary-700 underline">← Eserler listesine dön</a>`;

  const yazar = authors.find(a => slugify(a.name) === w.yazarSlug);
  const th = periodTheme(w.donem);

  return `
    <nav class="text-sm mb-3 text-slate-500"><a href="#/eserler" class="hover:underline">← Eserler</a></nav>

    <div class="rounded-2xl ${th.bg} p-6 border-2 border-slate-200 dark:border-slate-700 mb-5">
      <div class="flex items-start justify-between gap-3 flex-wrap">
        <div class="flex-1 min-w-0">
          <h1 class="text-3xl font-bold ${th.text} mb-2">${w.title}</h1>
          <div class="flex flex-wrap gap-2 mb-3">
            <span class="inline-flex items-center gap-1 text-xs font-semibold px-3 py-1 rounded-full bg-white/70 dark:bg-slate-900/60 ${th.text}">
              <span class="w-2 h-2 rounded-full ${th.dot}"></span>${th.label}
            </span>
            <span class="text-xs font-semibold px-3 py-1 rounded-full bg-white/70 dark:bg-slate-900/60 ${th.text}">📖 ${w.tur || '—'}</span>
            ${w.yil ? `<span class="text-xs font-semibold px-3 py-1 rounded-full bg-white/70 dark:bg-slate-900/60 ${th.text}">📅 ${w.yil}</span>` : ''}
            ${w.cikmis ? `<span class="text-xs font-semibold px-3 py-1 rounded-full bg-warn-500/30 text-warn-500">⭐ ÖSYM'de çıktı</span>` : ''}
          </div>
          <div class="text-sm ${th.text}">
            Yazar: <a href="#/yazarlar/${w.yazarSlug}" class="font-bold underline">${w.yazar}</a>
          </div>
        </div>
      </div>
    </div>

    ${yazar ? `
      <div class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg p-4 mb-4">
        <h3 class="font-bold mb-2 text-sm">📜 Yazar hakkında</h3>
        ${yazar.anekdot ? `<p class="text-sm italic mb-2">"${yazar.anekdot}"</p>` : ''}
        <div class="text-xs text-slate-500">Soru sayısı: ${yazar.soru_sayisi} · Yıllar: ${yazar.yillar.join(', ')}</div>
        <a href="#/yazarlar/${w.yazarSlug}" class="inline-block mt-2 text-xs text-primary-700 dark:text-primary-100 hover:underline">→ Yazarın trading card profilini aç</a>
      </div>
    ` : ''}
  `;
}
