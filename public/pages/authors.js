import { Data, topicLabel, slugify, periodTheme, altKonuToAuthorSlug, getDataSubject } from '../lib/data.js';
import { loadState } from '../lib/store.js';
import { authorMastery, LEVELS, cardsForAuthor } from '../lib/mastery.js';

function escapeHtml(s) {
  return String(s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}

export async function renderAuthorList() {
  // TYT Fen'de yazar/kişi veritabanı yok — empty state göster
  if (getDataSubject() === 'fen') {
    return `
      <section class="max-w-2xl mx-auto py-12 px-4 text-center">
        <div class="text-5xl mb-4">⚗</div>
        <h1 class="text-2xl font-bold mb-2">TYT Fen'de yazar veritabanı yok</h1>
        <p class="text-slate-600 dark:text-slate-400 mb-6">Fen Bilimleri ünite tabanlı çalışılır. Konu listesine geçerek 24 üniteyi keşfedebilirsin.</p>
        <a href="#/konular" class="inline-block px-6 py-3 rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white font-semibold">📚 Konulara Git</a>
      </section>
    `;
  }
  const authors = await Data.authors();
  const cards = await Data.cards();
  const state = loadState();
  const allCards = [...cards, ...state.custom_kartlar];

  // Mastery sayımları
  let cTanis = 0, cTani = 0, cOgr = 0;
  const masteryFor = {};
  for (const a of authors) {
    const lvl = authorMastery(a.name, allCards, state);
    masteryFor[a.name] = lvl;
    if (lvl === 'tanisilmadi') cTanis++;
    else if (lvl === 'tanidin') cTani++;
    else if (lvl === 'ogrendin') cOgr++;
  }

  const recurring = authors.filter(a => a.soru_sayisi >= 2);
  const single = authors.filter(a => a.soru_sayisi === 1);

  window.__pageSetup = () => {
    const q = document.getElementById('authorSearch');
    const filter = document.getElementById('authorFilter');
    const masteryF = document.getElementById('masteryFilter');
    function run() {
      const term = q.value.toLowerCase().trim();
      const f = filter.value;
      const mf = masteryF.value;
      document.querySelectorAll('[data-author-row]').forEach(row => {
        const name = row.dataset.authorRow.toLowerCase();
        const grup = row.dataset.grup;
        const mastery = row.dataset.mastery;
        let show = true;
        if (term && !name.includes(term)) show = false;
        if (f && f !== 'hepsi' && grup !== f) show = false;
        if (mf && mf !== 'hepsi' && mastery !== mf) show = false;
        row.style.display = show ? '' : 'none';
      });
    }
    q?.addEventListener('input', run);
    filter?.addEventListener('change', run);
    masteryF?.addEventListener('change', run);
  };

  const isTarih = getDataSubject() === 'tarih';
  const headerTitle = isTarih ? '👤 Kişi Veritabanı' : '👤 Yazar Veritabanı';
  const headerSub = isTarih
    ? `${authors.length} tarihî şahsiyet / 79 soru — ${recurring.length} tekrar, ${single.length} tek sefer.`
    : `${authors.length} yazar / 192 soru — ${recurring.length} tekrar, ${single.length} tek sefer.`;
  return `
    <header class="mb-6">
      <h1 class="text-3xl font-bold mb-1">${headerTitle}</h1>
      <p class="text-slate-600 dark:text-slate-400 text-sm">${headerSub}</p>
      <div class="flex flex-wrap gap-2 mt-3 text-xs">
        <span class="inline-flex items-center gap-1 px-2 py-1 rounded bg-slate-200 dark:bg-slate-800">${LEVELS.tanisilmadi.emoji} Tanışmadın: ${cTanis}</span>
        <span class="inline-flex items-center gap-1 px-2 py-1 rounded bg-warn-500/20 text-warn-500">${LEVELS.tanidin.emoji} Tanıdın: ${cTani}</span>
        <span class="inline-flex items-center gap-1 px-2 py-1 rounded bg-ok-500/20 text-ok-500">${LEVELS.ogrendin.emoji} Öğrendin: ${cOgr}</span>
        <a href="#/koleksiyon" class="ml-auto inline-flex items-center gap-1 px-3 py-1 bg-primary-700 text-white rounded hover:bg-primary-700/90">🎴 Koleksiyona git</a>
      </div>
    </header>
    <div class="flex gap-2 mb-4 flex-wrap">
      <input id="authorSearch" type="search" placeholder="Yazar ara: Fuzuli, Yakup Kadri..."
             class="flex-1 min-w-[200px] px-3 py-2 rounded-md border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900" />
      <select id="authorFilter" class="px-3 py-2 rounded-md border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900">
        <option value="hepsi">Tüm gruplar</option>
        <option value="A">Tablo A — Tekrar edenler (2+)</option>
        <option value="B">Tablo B — Tek sefer</option>
      </select>
      <select id="masteryFilter" class="px-3 py-2 rounded-md border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900">
        <option value="hepsi">Tüm seviyeler</option>
        <option value="tanisilmadi">${LEVELS.tanisilmadi.emoji} Tanışmadın</option>
        <option value="tanidin">${LEVELS.tanidin.emoji} Tanıdın</option>
        <option value="ogrendin">${LEVELS.ogrendin.emoji} Öğrendin</option>
      </select>
    </div>
    <div class="overflow-x-auto bg-white dark:bg-slate-900 rounded-lg border border-slate-200 dark:border-slate-700">
      <table class="w-full text-sm">
        <thead class="bg-primary-700 text-white">
          <tr>
            <th class="text-center px-2 py-2 w-8">Sev.</th>
            <th class="text-left px-3 py-2">Yazar</th>
            <th class="text-left px-2 py-2">Dönem</th>
            <th class="text-center px-2 py-2">Soru</th>
            <th class="text-left px-2 py-2">Yıllar</th>
            <th class="text-center px-2 py-2">MEBİ</th>
            <th class="text-left px-2 py-2">Bilinmesi Gereken Diğer Eserleri</th>
          </tr>
        </thead>
        <tbody>
          ${authors.map(a => {
            const lvl = masteryFor[a.name];
            const th = periodTheme(a.donem || a.konular[0]);
            return `
            <tr data-author-row="${a.name}" data-konu="${a.konular[0] || ''}" data-grup="${a.soru_sayisi >= 2 ? 'A' : 'B'}" data-mastery="${lvl}"
                class="border-t border-slate-200 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-800/50">
              <td class="text-center px-2 py-2" title="${LEVELS[lvl].label}">${LEVELS[lvl].emoji}</td>
              <td class="px-3 py-2 font-semibold">
                <a href="#/yazarlar/${slugify(a.name)}" class="text-primary-700 dark:text-primary-100 hover:underline">${a.name}</a>
                ${a.anma_yili_2026 ? '<span title="2026 Ziya Gökalp Anma Yılı" class="ml-1 text-amber-500">⭐</span>' : a.anma_yili_dalga ? '<span title="2026 Anma Yılı dalgası (Milli Edebiyat)" class="ml-1 text-amber-400/70">🌊</span>' : ''}
              </td>
              <td class="px-2 py-2"><span class="inline-flex items-center gap-1 text-xs px-2 py-0.5 rounded ${th.bg} ${th.text}"><span class="w-1.5 h-1.5 rounded-full ${th.dot}"></span>${th.label}</span></td>
              <td class="text-center px-2 py-2 ${a.soru_sayisi >= 5 ? 'font-bold text-accent-500' : ''}">${a.soru_sayisi}</td>
              <td class="px-2 py-2 text-slate-600 dark:text-slate-400">${a.yillar.join(', ')}</td>
              <td class="text-center px-2 py-2 text-xs text-slate-500">${a.mebi_sayfa || '—'}</td>
              <td class="px-2 py-2 text-xs text-slate-600 dark:text-slate-400">${a.diger_eserler || '—'}</td>
            </tr>`;
          }).join('')}
        </tbody>
      </table>
    </div>
  `;
}

export async function renderAuthorDetail(slug) {
  const authors = await Data.authors();
  const cards = await Data.cards();
  const state = loadState();
  const allCards = [...cards, ...state.custom_kartlar];

  // Çıkmış soruların tam metni için
  let cikmisData = null;
  try { cikmisData = await Data.cikmis(); } catch(e) { /* opsiyonel */ }

  const a = authors.find(x => slugify(x.name) === slug);
  if (!a) return `<p>Yazar bulunamadı.</p><a href="#/yazarlar" class="text-primary-700 underline">← Yazar listesine dön</a>`;

  const th = periodTheme(a.donem || a.konular[0]);
  const mastery = authorMastery(a.name, allCards, state);
  const aCards = cardsForAuthor(a.name, allCards);
  const rakipler = (a.rakipleri || []).map(name => {
    const r = authors.find(x => x.name === name);
    return { name, slug: r ? slugify(name) : null, mevcut: !!r };
  });

  // Stat: bu yazarda kullanıcının doğruluğu
  let totalCozuldu = 0, totalDogru = 0;
  for (const c of aCards) {
    const p = state.progress[c.id];
    if (p) { totalCozuldu += p.cozuldu; totalDogru += p.dogru; }
  }
  const accPct = totalCozuldu > 0 ? Math.round((totalDogru / totalCozuldu) * 100) : null;

  // Yıldız sayısı (1-7) — soru sayısına göre
  const yildiz = Math.min(7, a.soru_sayisi);
  const yildizStr = '★'.repeat(yildiz) + '☆'.repeat(7 - yildiz);

  return `
    <nav class="text-sm mb-3 text-slate-500"><a href="#/yazarlar" class="hover:underline">← Yazar listesi</a></nav>

    <!-- TRADING CARD HEADER -->
    <div class="rounded-2xl overflow-hidden border-2 border-slate-200 dark:border-slate-700 mb-6 ${th.bg}">
      <div class="p-6">
        <div class="flex items-start justify-between gap-3 flex-wrap">
          <div class="flex-1 min-w-0">
            <h1 class="text-3xl font-bold ${th.text} mb-2">${a.name}</h1>
            <div class="flex flex-wrap gap-2 mb-3">
              <span class="inline-flex items-center gap-1 text-xs font-semibold px-3 py-1 rounded-full bg-white/70 dark:bg-slate-900/50 ${th.text}">
                <span class="w-2 h-2 rounded-full ${th.dot}"></span>${th.label}
              </span>
              <span class="inline-flex items-center gap-1 text-xs font-semibold px-3 py-1 rounded-full bg-white/70 dark:bg-slate-900/50 ${th.text}">
                📖 ${a.pozisyon || 'Çok yönlü'}
              </span>
              <span class="inline-flex items-center gap-1 text-xs font-semibold px-3 py-1 rounded-full bg-white/70 dark:bg-slate-900/50 ${th.text}">
                ${LEVELS[mastery].emoji} ${LEVELS[mastery].label}
              </span>
            </div>
            <div class="text-sm ${th.text} font-mono tracking-wide">${yildizStr} <span class="font-bold">${a.soru_sayisi} SORU</span></div>
            <div class="text-xs ${th.text} opacity-80 mt-1">
              Yıllar: ${a.yillar.join(', ')} · Son: ${Math.max(...a.yillar)}
            </div>
          </div>
          <div class="bg-white/80 dark:bg-slate-900/70 rounded-xl p-3 text-center min-w-[110px]">
            <div class="text-xs ${th.text} opacity-70">Senin doğruluğun</div>
            <div class="text-2xl font-bold ${th.text}">${accPct !== null ? '%' + accPct : '—'}</div>
            <div class="text-[10px] ${th.text} opacity-70">${totalDogru}/${totalCozuldu}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- REV19 — 2026 ANMA YILI ROZETİ (Ziya Gökalp + Milli Ed. dalgası) -->
    ${a.anma_yili_2026 ? `
      <div class="mb-4 rounded-lg p-3 flex items-center gap-3 bg-gradient-to-r from-amber-400/20 to-yellow-300/10 border-2 border-amber-400/50">
        <div class="text-2xl">⭐</div>
        <div class="flex-1">
          <div class="text-xs font-bold uppercase tracking-wider text-amber-700 dark:text-amber-300">2026 Anma Yılı</div>
          <div class="text-sm font-bold mt-0.5 text-amber-800 dark:text-amber-200">Resmî Ziya Gökalp Yılı (150. doğum yılı · TÜRKSOY)</div>
          <div class="text-[11px] text-slate-600 dark:text-slate-400 mt-1">2026'da AYT Edebiyat'ta vurgu ihtimali yüksek — bu yazara öncelik ver.</div>
        </div>
      </div>
    ` : a.anma_yili_dalga ? `
      <div class="mb-4 rounded-lg p-2.5 flex items-center gap-2 bg-amber-400/10 border border-amber-400/30">
        <div class="text-lg">🌊</div>
        <div class="text-[11px] text-amber-700 dark:text-amber-300 font-semibold">2026 Ziya Gökalp Anma Yılı dalgası — Genç Kalemler / Milli Edebiyat çevresi öne çıkabilir.</div>
      </div>
    ` : ''}

    <!-- REV17 — 2026 PRIORITY BADGE -->
    ${a.priority_2026 && a.priority_2026 !== 'İHMAL' ? `
      <div class="mb-4 rounded-lg p-3 flex items-center gap-3 ${
        a.priority_2026 === 'ÇOK YÜKSEK' ? 'bg-accent-500/10 border-2 border-accent-500/40' :
        a.priority_2026 === 'YÜKSEK' ? 'bg-warn-500/10 border-2 border-warn-500/40' :
        'bg-primary-500/10 border-2 border-primary-500/30'
      }">
        <div class="text-2xl">🎯</div>
        <div class="flex-1">
          <div class="text-xs font-bold uppercase tracking-wider opacity-75">2026 Önceliği (Pattern Engine)</div>
          <div class="text-sm font-bold mt-0.5">
            <span class="${
              a.priority_2026 === 'ÇOK YÜKSEK' ? 'text-accent-700 dark:text-accent-200' :
              a.priority_2026 === 'YÜKSEK' ? 'text-warn-700 dark:text-warn-200' :
              'text-primary-700 dark:text-primary-100'
            }">${a.priority_2026}</span>
            <span class="text-slate-500 ml-1">— skor ${Math.round(a.due_score_2026 || 0)}/100</span>
          </div>
          ${a.rationale_2026 ? `<div class="text-[11px] text-slate-500 mt-1">${a.rationale_2026}</div>` : ''}
        </div>
        <a href="#/sistem" class="text-[10px] underline text-slate-500 hover:text-primary-500">Detay</a>
      </div>
    ` : ''}

    <!-- ANEKDOT -->
    ${a.anekdot ? `
      <div class="bg-white dark:bg-slate-900 border-l-4 border-primary-700 dark:border-primary-100 rounded-r-lg p-4 mb-4">
        <div class="text-xs font-bold uppercase tracking-wider text-primary-700 dark:text-primary-100 mb-2">⚡ Anekdot</div>
        <p class="text-sm italic leading-relaxed">${a.anekdot}</p>
      </div>
    ` : ''}

    <!-- KLASİK ÖSYM TUZAĞI -->
    ${a.klasik_tuzak ? `
      <div class="tuzak-box mb-4">
        <strong>⚠ KLASİK ÖSYM TUZAĞI</strong>
        <div class="mt-1 text-sm">${a.klasik_tuzak}</div>
      </div>
    ` : ''}

    <!-- RAKİPLERİ -->
    ${rakipler.length ? `
      <div class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg p-4 mb-4">
        <h3 class="font-bold mb-2 text-sm">🥊 Rakipleri (sık karıştırılan)</h3>
        <div class="flex flex-wrap gap-2">
          ${rakipler.map(r => r.mevcut
            ? `<a href="#/yazarlar/${r.slug}" class="inline-block px-3 py-1 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 rounded-md text-sm">${r.name}</a>`
            : `<span class="inline-block px-3 py-1 bg-slate-50 dark:bg-slate-900 text-slate-400 dark:text-slate-500 rounded-md text-sm" title="Veritabanında yok">${r.name}</span>`
          ).join('')}
        </div>
      </div>
    ` : ''}

    <!-- MEBİ + DİĞER ESERLER -->
    <div class="grid md:grid-cols-2 gap-4 mb-4">
      <div class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg p-4">
        <h3 class="font-bold mb-2 text-sm">📘 MEBİ Konu Özeti</h3>
        ${a.mebi_sayfa
          ? `<div class="mebi-box"><strong>📘 ayt-tde.pdf</strong> → sayfa <strong>${a.mebi_sayfa}</strong></div>`
          : `<p class="text-sm text-slate-500">MEBİ özet sayfası eşlenmemiş</p>`}
      </div>
      <div class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg p-4">
        <h3 class="font-bold mb-2 text-sm">📚 Bilinmesi Gereken Diğer Eserleri (2026 aday)</h3>
        <p class="text-sm text-slate-600 dark:text-slate-400">${a.diger_eserler || '—'}</p>
      </div>
    </div>

    <!-- ÇIKMIŞ SORULAR (tam metniyle expand) -->
    ${a.occurrences && a.occurrences.length ? `
      <div class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg p-4 mb-4">
        <h3 class="font-bold mb-3 text-sm">📜 Çıkmış Soru Geçmişi <span class="text-xs text-slate-500 font-normal">— tam metin için aç</span></h3>
        <ul class="space-y-2 text-sm">
          ${a.occurrences.map(o => {
            const q = cikmisData?.questions.find(x => x.year === o.year && x.qno === o.qno);
            return `
              <li class="border-b border-slate-100 dark:border-slate-800 pb-2">
                <details>
                  <summary class="flex items-center gap-2 cursor-pointer">
                    <span class="bg-primary-50 dark:bg-primary-900/50 text-primary-700 dark:text-primary-100 text-xs font-bold px-2 py-0.5 rounded">${o.year}</span>
                    <span>Soru ${o.qno}</span>
                    <span class="text-slate-500 text-xs">· ${topicLabel(o.topic)}</span>
                    ${q ? '<span class="ml-auto text-xs text-primary-700 dark:text-primary-100">▼ aç</span>' : '<span class="ml-auto text-xs text-slate-400">tam metin yok</span>'}
                  </summary>
                  ${q ? `
                    <div class="mt-2 ml-2 p-3 bg-slate-50 dark:bg-slate-800 rounded text-xs leading-relaxed whitespace-pre-wrap">${escapeHtml(q.soru)}</div>
                    ${q.secenekler && q.secenekler.length ? `
                      <div class="mt-2 ml-2 grid gap-1">
                        ${q.secenekler.map(s => `<div class="text-xs flex gap-2"><strong class="text-primary-700 dark:text-primary-100">${s.id})</strong><span>${escapeHtml(s.text)}</span></div>`).join('')}
                      </div>
                    ` : ''}
                    <div class="mt-2 ml-2 text-[10px] text-slate-500">Kaynak: MEB Çıkmış Sorular ${q.year}-AYT s.${q.page}</div>
                  ` : ''}
                </details>
              </li>
            `;
          }).join('')}
        </ul>
      </div>
    ` : ''}

    <!-- AKSİYON BUTONLARI -->
    <div class="flex flex-wrap gap-2 sticky bottom-3">
      ${aCards.length > 0 ? `
        <a href="#/quiz?yazar=${slugify(a.name)}&sayi=${Math.min(aCards.length, 10)}" class="flex-1 min-w-[150px] text-center bg-accent-500 hover:bg-accent-700 text-white font-bold py-3 px-4 rounded-lg shadow-md">
          🎯 Bu yazardan ${Math.min(aCards.length, 10)} soru çöz
        </a>
        <a href="#/atis?yazar=${slugify(a.name)}" class="flex-1 min-w-[150px] text-center bg-primary-700 hover:bg-primary-700/90 text-white font-bold py-3 px-4 rounded-lg shadow-md">
          ⚡ Bu yazardan Hızlı Atış
        </a>
      ` : `
        <div class="flex-1 text-center text-sm text-slate-500 py-3">Bu yazara ait kart bulunamadı</div>
      `}
    </div>
  `;
}
