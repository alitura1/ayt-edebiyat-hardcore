// REV26 — PhET (Colorado Üni.) interaktif fen simülasyonları
// TYT Fen subject'inde aktif; konuyu canlı görmek için iframe embed.
import { Data, getDataSubject, periodTheme } from '../lib/data.js';

export async function renderSimulations() {
  if (getDataSubject() !== 'fen') {
    return `
      <section class="max-w-2xl mx-auto py-12 px-4 text-center">
        <div class="text-5xl mb-4">🔬</div>
        <h1 class="text-2xl font-bold mb-2">Simülasyonlar sadece TYT Fen'de</h1>
        <p class="text-slate-600 dark:text-slate-400 mb-6">PhET fizik/kimya/biyoloji simülasyonları TYT Fen subject'ine özel.</p>
        <a href="#/select-subject" class="inline-block px-5 py-2.5 rounded-lg bg-primary-700 hover:bg-primary-700/90 text-white font-semibold">Ders Değiştir</a>
      </section>
    `;
  }

  const sims = await Data.simulations();

  // Post-render setup (sayfa render edildikten sonra çalışır)
  window.__pageSetup = () => {
    // Sim kart click → modal
    document.querySelectorAll('[data-sim-id]').forEach(card => {
      card.addEventListener('click', (e) => {
        e.preventDefault();
        const id = card.dataset.simId;
        const sim = sims.find(s => s.id === id);
        if (!sim) return;
        openSimModal(sim);
      });
    });
    // Ders chip filter
    document.querySelectorAll('.ders-chip[data-sim-ders]').forEach(btn => {
      btn.addEventListener('click', () => {
        const d = btn.dataset.simDers;
        document.querySelectorAll('.ders-chip[data-sim-ders]').forEach(b => b.classList.toggle('active', b === btn));
        document.querySelectorAll('[data-sim-card]').forEach(card => {
          card.style.display = (d === 'hepsi' || card.dataset.ders === d) ? '' : 'none';
        });
      });
    });
  };

  return `
    <header class="mb-6">
      <h1 class="text-3xl font-bold mb-1">🔬 PhET Simülasyonlar</h1>
      <p class="text-slate-600 dark:text-slate-400 text-sm">
        Konuyu ezberlemeden önce CANLI GÖR. PhET (Colorado Üniv.) ücretsiz interaktif simülasyonları — 12 alan, kalıcılık ✕10.
      </p>
    </header>

    <div class="flex flex-wrap items-center gap-2 mb-5">
      <span class="text-xs text-slate-500 mr-1">Ders:</span>
      <button class="ders-chip active" data-sim-ders="hepsi">Hepsi (${sims.length})</button>
      <button class="ders-chip" data-sim-ders="fizik">⚛ Fizik (${sims.filter(s=>s.ders==='fizik').length})</button>
      <button class="ders-chip" data-sim-ders="kimya">🧪 Kimya (${sims.filter(s=>s.ders==='kimya').length})</button>
      <button class="ders-chip" data-sim-ders="biyoloji">🧬 Biyoloji (${sims.filter(s=>s.ders==='biyoloji').length})</button>
    </div>

    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
      ${sims.map(s => {
        const th = periodTheme(s.ders);
        return `
          <a href="#" data-sim-id="${s.id}" data-sim-card data-ders="${s.ders}"
             class="block bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg p-4 hover:border-emerald-500 transition group">
            <div class="flex items-center justify-between gap-2 mb-2">
              <span class="inline-flex items-center gap-1 text-[10px] font-semibold px-2 py-0.5 rounded ${th.bg} ${th.text}">
                <span class="w-1.5 h-1.5 rounded-full ${th.dot}"></span>${th.label}
              </span>
              <span class="text-xs text-slate-500 group-hover:text-emerald-600">▶ Aç</span>
            </div>
            <h3 class="font-bold text-base mb-1">${s.title}</h3>
            <p class="text-xs text-slate-600 dark:text-slate-400 leading-relaxed">${s.aciklama}</p>
            <div class="mt-2 text-[10px] text-slate-400">${s.kaynak}</div>
          </a>
        `;
      }).join('')}
    </div>

    <div class="mt-8 text-xs text-slate-500 leading-relaxed">
      <strong>💡 İpucu:</strong> Simülasyon açıldığında sol üst köşede dil seçici → "Türkçe" seç. Kavramı kurcalayıp ezberden çıkar, mantığını yakala. Sonra hızlıca site'deki o ünitenin kart havuzuna geç.
    </div>
  `;
}

function openSimModal(sim) {
  const backdrop = document.createElement('div');
  backdrop.className = 'sim-modal-backdrop';
  backdrop.innerHTML = `
    <div class="sim-modal-card">
      <div class="flex items-center justify-between gap-2 p-3 border-b border-slate-200 dark:border-slate-700">
        <h3 class="font-bold">${sim.title}</h3>
        <div class="flex items-center gap-2">
          <a href="${sim.url}" target="_blank" rel="noopener" class="text-xs text-primary-700 dark:text-primary-100 hover:underline" title="Yeni sekmede aç">↗ Yeni sekme</a>
          <button class="sim-close-btn px-3 py-1 text-sm bg-slate-200 dark:bg-slate-700 hover:bg-slate-300 dark:hover:bg-slate-600 rounded">Kapat</button>
        </div>
      </div>
      <iframe class="sim-modal-iframe" src="${sim.url}" allowfullscreen></iframe>
      <div class="p-2 text-[10px] text-slate-500 border-t border-slate-200 dark:border-slate-700">
        Kaynak: ${sim.kaynak} — ücretsiz açık kaynaklı eğitim simülasyonu
      </div>
    </div>
  `;
  document.body.appendChild(backdrop);
  document.body.style.overflow = 'hidden';

  const close = () => {
    backdrop.remove();
    document.body.style.overflow = '';
  };
  backdrop.addEventListener('click', (e) => {
    if (e.target === backdrop) close();
  });
  backdrop.querySelector('.sim-close-btn')?.addEventListener('click', close);
  // ESC ile kapat
  const onKey = (e) => { if (e.key === 'Escape') { close(); document.removeEventListener('keydown', onKey); } };
  document.addEventListener('keydown', onKey);
}
