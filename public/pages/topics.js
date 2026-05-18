import { Data, topicLabel, slugify } from '../lib/data.js';

export async function renderTopicList() {
  const idx = await Data.topicsIndex();
  return `
    <header class="mb-6">
      <h1 class="text-3xl font-bold mb-1">📚 13 Konu</h1>
      <p class="text-slate-600 dark:text-slate-400 text-sm">Frekansa göre sıralı. ÖSYM her konuda ne soruyor, hangi alt başlık 2026 boşluk adayı — hepsi içeride.</p>
    </header>
    <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
      ${idx.map(t => `
        <a href="#/konular/${t.slug}" class="block bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg p-4 hover:border-primary-500 transition">
          <div class="flex items-center justify-between gap-3 mb-2">
            <div class="font-bold text-lg">${t.title}</div>
            <span class="text-sm bg-primary-700 text-white px-2 py-0.5 rounded-full font-bold">${t.toplam} soru</span>
          </div>
          <div class="flex items-center gap-2 text-xs text-slate-500 dark:text-slate-400 mb-2">
            <span>${t.alt_basliklar} alt başlık</span>
            <span>·</span>
            <span class="font-semibold ${oncelikColor(t.oncelik)}">${t.oncelik} öncelik</span>
            <span>·</span>
            <span title="MEBİ Konu Özet sayfa aralığı">📘 MEBİ s.${t.mebi_pages}</span>
          </div>
          <p class="text-sm text-slate-600 dark:text-slate-400">${t.kisa_aciklama}</p>
        </a>
      `).join('')}
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
