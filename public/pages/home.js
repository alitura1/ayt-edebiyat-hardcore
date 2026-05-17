import { loadState } from '../lib/store.js';

export async function renderHome() {
  const s = loadState();
  const totalProgress = Object.keys(s.progress).length;
  const totalCorrect = Object.values(s.progress).reduce((a,p) => a + p.dogru, 0);
  const totalSolved = Object.values(s.progress).reduce((a,p) => a + p.cozuldu, 0);
  const accuracy = totalSolved > 0 ? Math.round((totalCorrect / totalSolved) * 100) : 0;
  const errorCount = s.hata_defteri.length;
  const customCount = s.custom_kartlar.length;

  return `
    <section class="text-center mb-8">
      <h1 class="text-3xl md:text-4xl font-bold text-primary-700 dark:text-primary-100 mb-2">
        AYT Edebiyat <span class="text-accent-500">Hardcore</span> Hazırlık
      </h1>
      <p class="text-slate-600 dark:text-slate-400 max-w-2xl mx-auto">
        2018-2025 arası <strong>192 ÖSYM sorusu</strong> tek tek analiz edildi.
        ÖSYM'nin mantığı, tuzakları, tekrar eden yazarları ve 2026 tahminleri burada.
      </p>
    </section>

    ${totalSolved > 0 ? `
    <section class="grid grid-cols-3 gap-3 mb-8 max-w-2xl mx-auto">
      <div class="bg-primary-50 dark:bg-primary-900/40 rounded-lg p-3 text-center">
        <div class="text-2xl font-bold text-primary-700 dark:text-primary-100">${totalSolved}</div>
        <div class="text-xs text-slate-600 dark:text-slate-400">Çözülen</div>
      </div>
      <div class="bg-ok-500/10 dark:bg-ok-500/20 rounded-lg p-3 text-center">
        <div class="text-2xl font-bold text-ok-500">%${accuracy}</div>
        <div class="text-xs text-slate-600 dark:text-slate-400">Doğruluk</div>
      </div>
      <div class="bg-accent-500/10 dark:bg-accent-500/20 rounded-lg p-3 text-center">
        <div class="text-2xl font-bold text-accent-500">${errorCount}</div>
        <div class="text-xs text-slate-600 dark:text-slate-400">Hata defteri</div>
      </div>
    </section>
    ` : ''}

    <section class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 max-w-5xl mx-auto">
      ${shortcut('quiz/setup', '🎯', 'Quiz Başlat', 'ÖSYM tarzı 4 şıklı test. Konu/zorluk seç, 10-30 soru çöz.', 'accent')}
      ${shortcut('konular', '📚', '13 Konu Öğretim', 'Divan, Cumhuriyet, Akımlar... Her konunun ÖSYM mantığı + ezber paketi.', 'primary')}
      ${shortcut('yazarlar', '👤', '85 Yazar Veritabanı', '50 tekrar + 35 tek sefer. Hangi yıl hangi eserle çıkmış, MEBİ sayfası nerede.', 'primary')}
      ${shortcut('tahminler', '🔮', '2026 Tahminleri', '8 yıllık trend + boşluk haritası + güçlü adaylar (Yedi Meşale, Hisarcılar...).', 'accent')}
      ${shortcut('program', '📅', '1 Aylık Program', 'Her gün ne çalış? Doküman + MEBİ + sorular paralel takvim.', 'primary')}
      ${shortcut('sozluk', '📖', 'Mini Sözlük', 'Akım × yazar × eser tabloları. Tanzimat "ilk"leri, söz sanatları.', 'primary')}
      ${shortcut('kartlar', '🃏', 'Kart Havuzu', `${customCount > 0 ? customCount + ' özel kart + ' : ''}otomatik kartlar — yönet, ekle, düzenle.`, 'primary')}
      ${shortcut('istatistik', '📊', 'İlerleme', 'Konu bazlı zayıflık, doğruluk grafiği, hata defteri.', 'primary')}
      ${shortcut('ayarlar', '⚙️', 'Ayarlar', 'Tema, ses, export/import, sıfırla.', 'primary')}
    </section>

    <section class="mt-12 max-w-3xl mx-auto bg-warn-500/10 border border-warn-500/30 rounded-lg p-5">
      <h3 class="font-bold mb-2 flex items-center gap-2">
        <span>💡</span> Stratejin
      </h3>
      <ul class="text-sm text-slate-700 dark:text-slate-300 space-y-1 list-disc list-inside">
        <li>İlk 6 soru (sözcükte/cümlede/paragraf) → pure yorum, çalışma değil pratik istiyor. Zaten yapıyorsun.</li>
        <li>Geri kalan 18 soru → ezberlenebilir/konuya dayalı. <strong>15-20 net hedefin</strong> bu 18'den çıkar.</li>
        <li>Bu site → ÖSYM mantığı + tahmin + quiz pratiği. MEBİ özet PDF konu sayfalarında entegre.</li>
      </ul>
    </section>
  `;
}

function shortcut(route, icon, title, desc, accent) {
  const accentClass = accent === 'accent'
    ? 'border-accent-500/30 hover:border-accent-500 hover:bg-accent-500/5'
    : 'border-primary-500/20 hover:border-primary-500 hover:bg-primary-50 dark:hover:bg-primary-900/30';
  return `
    <a href="#/${route}" class="block bg-white dark:bg-slate-900 border-2 ${accentClass} rounded-xl p-5 transition-all hover:shadow-md">
      <div class="text-3xl mb-2">${icon}</div>
      <div class="font-bold text-lg mb-1">${title}</div>
      <p class="text-sm text-slate-600 dark:text-slate-400">${desc}</p>
    </a>
  `;
}
