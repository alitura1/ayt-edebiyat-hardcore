import { Data, topicLabel, slugify, getDataSubject, periodTheme } from '../lib/data.js';

export async function renderTopicList() {
  const idx = await Data.topicsIndex();
  const subject = getDataSubject();
  const isTarih = subject === 'tarih';
  const isFen = subject === 'fen';
  const headerIcon = isFen ? '⚗' : (isTarih ? '⏳' : '📚');
  const headerTitle = isFen
    ? `${idx.length} Ünite · 3 Ders`
    : (isTarih ? `${idx.length} Dönem` : `${idx.length} Konu`);
  const headerSub = isFen
    ? '8 yıllık ÖSYM frekansına göre sıralı. Fizik / Kimya / Biyoloji filtreleyerek dersine odaklan; sıcak alanları öncele.'
    : (isTarih
      ? 'Soru sayısına göre sıralı. ÖSYM 8 yılda hangi dönemden kaç soru çıkarmış, hangi konu 2026 boşluk adayı — hepsi içeride.'
      : 'Frekansa göre sıralı. ÖSYM her konuda ne soruyor, hangi alt başlık 2026 boşluk adayı — hepsi içeride.');

  // Fen için ders filter chip'leri + sıcaklığa göre sıralama
  const fenFilterBar = isFen ? `
    <div class="flex flex-wrap items-center gap-2 mb-5">
      <span class="text-xs text-slate-500 mr-1">Ders:</span>
      <button class="ders-chip active" data-ders="hepsi">Hepsi (${idx.length})</button>
      <button class="ders-chip" data-ders="fizik">⚛ Fizik (${idx.filter(t=>t.ders==='fizik').length})</button>
      <button class="ders-chip" data-ders="kimya">🧪 Kimya (${idx.filter(t=>t.ders==='kimya').length})</button>
      <button class="ders-chip" data-ders="biyoloji">🧬 Biyoloji (${idx.filter(t=>t.ders==='biyoloji').length})</button>
      <span class="text-xs text-slate-500 ml-3 mr-1">Öncelik:</span>
      <button class="ders-chip" data-oncelik="sicak">🔥 Sıcak</button>
      <button class="ders-chip" data-oncelik="hepsi">Tümü</button>
    </div>
  ` : '';

  // Fen sıralama: önce sıcak, sonra toplam frekans
  const sortedIdx = isFen
    ? [...idx].sort((a, b) => {
        const oncA = a.oncelik === 'sicak' ? 0 : a.oncelik === 'orta' ? 1 : 2;
        const oncB = b.oncelik === 'sicak' ? 0 : b.oncelik === 'orta' ? 1 : 2;
        if (oncA !== oncB) return oncA - oncB;
        return (b.toplam || 0) - (a.toplam || 0);
      })
    : idx;

  // Fen post-render setup (ders chip + öncelik chip filter)
  if (isFen) {
    window.__pageSetup = () => {
      let currentDers = 'hepsi';
      let currentOncelik = 'hepsi';
      const run = () => {
        document.querySelectorAll('[data-topic-card]').forEach(card => {
          const cardDers = card.dataset.ders;
          const cardOnc = card.dataset.oncelik;
          let show = true;
          if (currentDers !== 'hepsi' && cardDers !== currentDers) show = false;
          if (currentOncelik !== 'hepsi' && cardOnc !== currentOncelik) show = false;
          card.style.display = show ? '' : 'none';
        });
      };
      document.querySelectorAll('.ders-chip[data-ders]').forEach(btn => {
        btn.addEventListener('click', () => {
          currentDers = btn.dataset.ders;
          document.querySelectorAll('.ders-chip[data-ders]').forEach(b => b.classList.toggle('active', b === btn));
          run();
        });
      });
      document.querySelectorAll('.ders-chip[data-oncelik]').forEach(btn => {
        btn.addEventListener('click', () => {
          currentOncelik = btn.dataset.oncelik;
          document.querySelectorAll('.ders-chip[data-oncelik]').forEach(b => b.classList.toggle('active', b === btn));
          run();
        });
      });
    };
  }

  return `
    <header class="mb-6">
      <h1 class="text-3xl font-bold mb-1">${headerIcon} ${headerTitle}</h1>
      <p class="text-slate-600 dark:text-slate-400 text-sm">${headerSub}</p>
    </header>
    ${fenFilterBar}
    <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
      ${sortedIdx.map(t => {
        const dersTh = isFen ? periodTheme(t.ders) : null;
        const oncelikCls = (t.oncelik === 'sicak' || t.oncelik === 'ÇOK YÜKSEK' || t.oncelik === 'YÜKSEK') ? 'oncelik-sicak'
                          : t.oncelik === 'orta' || t.oncelik === 'ORTA' ? 'oncelik-orta'
                          : 'oncelik-dusuk';
        const oncelikLabel = t.oncelik === 'sicak' ? '🔥 SICAK' : t.oncelik === 'orta' ? '🟡 ORTA' : t.oncelik === 'dusuk' ? '⚪ DÜŞÜK' : t.oncelik;
        const dersBadge = isFen && dersTh
          ? `<span class="inline-flex items-center gap-1 text-[10px] px-2 py-0.5 rounded ${dersTh.bg} ${dersTh.text}"><span class="w-1.5 h-1.5 rounded-full ${dersTh.dot}"></span>${dersTh.label}</span>`
          : '';
        const altOrKart = isFen
          ? `<span title="Bu üniteden kart sayısı">🎴 ${t.kart_say || 0} kart</span>`
          : `<span>${t.alt_basliklar} alt başlık</span>`;
        return `
        <a href="#/konular/${t.slug}" data-topic-card data-ders="${t.ders || ''}" data-oncelik="${t.oncelik || ''}"
           class="block bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg p-4 hover:border-primary-500 transition">
          <div class="flex items-center justify-between gap-3 mb-2">
            <div class="font-bold text-lg">${t.title}</div>
            <span class="text-sm bg-primary-700 text-white px-2 py-0.5 rounded-full font-bold">${t.toplam} soru</span>
          </div>
          <div class="flex items-center gap-2 text-xs text-slate-500 dark:text-slate-400 mb-2 flex-wrap">
            ${dersBadge}
            ${dersBadge ? '<span>·</span>' : ''}
            ${altOrKart}
            <span>·</span>
            <span class="${oncelikCls}">${oncelikLabel}</span>
            <span>·</span>
            <span title="MEBİ Konu Özet sayfa aralığı">📘 MEBİ s.${t.mebi_pages}</span>
          </div>
          <p class="text-sm text-slate-600 dark:text-slate-400">${t.kisa_aciklama}</p>
        </a>
        `;
      }).join('')}
    </div>
  `;
}

function oncelikColor(o) {
  return o === 'ÇOK YÜKSEK' || o === 'YÜKSEK' ? 'text-accent-500' :
         o === 'ORTA' ? 'text-warn-500' : 'text-slate-500';
}

export async function renderTopicDetail(slug) {
  const idx = await Data.topicsIndex();
  const topic = idx.find(t => t.slug === slug);
  if (!topic) return `<p>Konu bulunamadı: ${slug}</p>`;
  const html = await Data.topicHTML(slug);

  // REV15 — Heading'lere otomatik id ata + URL hash anchor scroll
  window.__pageSetup = () => {
    document.querySelectorAll('article.topic-content h2, article.topic-content h3, article.topic-content h4').forEach(h => {
      if (!h.id) {
        const text = (h.textContent || '').replace(/^[▶▸►•]\s*/, '').trim();
        const id = slugify(text);
        if (id) h.id = id;
      }
    });
    // location.hash = "#/konular/divan_edebiyati#gazel"
    const parts = location.hash.split('#');
    if (parts.length >= 3 && parts[2]) {
      const targetId = parts[2];
      const target = document.getElementById(targetId);
      if (target) {
        setTimeout(() => {
          target.scrollIntoView({ behavior: 'smooth', block: 'start' });
          target.classList.add('ring-2', 'ring-accent-500', 'rounded', 'px-2');
          setTimeout(() => target.classList.remove('ring-2', 'ring-accent-500', 'rounded', 'px-2'), 3500);
        }, 200);
      }
    }
  };

  return `
    <nav class="text-sm mb-3 text-slate-500"><a href="#/konular" class="hover:underline">← Tüm konular</a></nav>
    <header class="mb-4 pb-4 border-b border-slate-200 dark:border-slate-700">
      <div class="flex items-center justify-between gap-3 flex-wrap mb-2">
        <h1 class="text-3xl font-bold text-primary-700 dark:text-primary-100">${topic.title}</h1>
        <span class="text-sm bg-primary-700 text-white px-3 py-1 rounded-full font-bold">${topic.toplam} soru / 8 yıl</span>
      </div>
      <p class="text-slate-600 dark:text-slate-400 text-sm">${topic.kisa_aciklama}</p>
      <div class="mt-3 flex gap-2 flex-wrap">
        <a href="#/quiz/setup?konu=${topic.code}" class="text-sm bg-accent-500 hover:bg-accent-700 text-white px-3 py-1.5 rounded-md font-semibold">🎯 Bu konudan quiz başlat</a>
      </div>
    </header>
    <article class="topic-content max-w-none">
      ${html}
    </article>
  `;
}
