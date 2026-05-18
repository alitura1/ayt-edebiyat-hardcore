import { Data, periodTheme, slugify } from '../lib/data.js';
import { loadState, updateProgress, recordSrs } from '../lib/store.js';
import { tickStreak, streakInfo, currentBadge, nextBadge } from '../lib/streak.js';
import { dailyHero } from '../lib/daily.js';

function shuffle(arr) {
  const a = [...arr];
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

export async function renderHome() {
  const s = loadState();
  const authors = await Data.authors();
  const cards = await Data.cards();
  const allCards = [...cards, ...s.custom_kartlar];

  const totalCorrect = Object.values(s.progress).reduce((a,p) => a + p.dogru, 0);
  const totalSolved = Object.values(s.progress).reduce((a,p) => a + p.cozuldu, 0);
  const accuracy = totalSolved > 0 ? Math.round((totalCorrect / totalSolved) * 100) : 0;
  const errorCount = s.hata_defteri.length;
  const customCount = s.custom_kartlar.length;

  // Daily Hero — REV6: her sayfa açılışta farklı yazar
  const hero = dailyHero(authors, allCards);
  const heroAuthor = hero.author;
  const heroCard = hero.miniCard;
  const heroSlug = heroAuthor ? slugify(heroAuthor.name) : '';
  const heroTheme = heroAuthor ? periodTheme(heroAuthor.donem || heroAuthor.konular?.[0]) : null;
  const heroAnswered = false;  // her açılışta yeni soru

  // Streak
  const sk = streakInfo();
  const curBadge = currentBadge(sk.current);
  const nxtBadge = nextBadge(sk.current);
  const streakColor = sk.status === 'active_today' ? 'text-ok-500' : sk.status === 'at_risk' ? 'text-warn-500' : sk.status === 'broken' ? 'text-slate-400' : 'text-slate-400';

  window.__pageSetup = () => {
    // Yenile butonu — sayfayı tekrar render
    document.getElementById('heroReroll')?.addEventListener('click', () => {
      // hashchange tetiklemek için tek manuel re-render
      window.dispatchEvent(new HashChangeEvent('hashchange'));
    });
    // Daily Hero mini quiz inline cevap
    const opts = document.querySelectorAll('[data-hero-opt]');
    let answered = heroAnswered;
    opts.forEach(btn => {
      btn.addEventListener('click', () => {
        if (answered || !heroCard) return;
        answered = true;
        const chosen = btn.dataset.heroOpt;
        const isCorrect = chosen === heroCard.dogru;
        opts.forEach(b => {
          b.disabled = true;
          if (b.dataset.heroOpt === heroCard.dogru) b.classList.add('correct');
          if (b.dataset.heroOpt === chosen && !isCorrect) b.classList.add('wrong');
        });
        updateProgress(heroCard.id, isCorrect);
        recordSrs(heroCard.id, isCorrect);
        const streakRes = tickStreak();

        document.getElementById('heroFeedback')?.classList.remove('hidden');

        if (streakRes.bumped) {
          const toast = document.createElement('div');
          toast.className = 'fixed bottom-4 left-1/2 -translate-x-1/2 z-50 bg-accent-500 text-white px-4 py-2 rounded-lg shadow-lg text-sm font-bold';
          toast.textContent = `🔥 Streak ${streakRes.current} gün!`;
          document.body.appendChild(toast);
          setTimeout(() => toast.remove(), 2500);
        }

        // Header rozet güncelle
        try { window.dispatchEvent(new HashChangeEvent('hashchange')); } catch(e){}
      });
    });
  };

  return `
    <section class="text-center mb-6">
      <h1 class="text-2xl md:text-3xl font-bold text-primary-700 dark:text-primary-100 mb-1">
        AYT Edebiyat <span class="text-accent-500">Hardcore</span>
      </h1>
      <p class="text-slate-600 dark:text-slate-400 text-sm max-w-2xl mx-auto">
        Futbol takip eder gibi yazarları tanı. Her gün gir, hata yap, sürekli karşılaş — ezberlemeden ezberle.
      </p>
    </section>

    <!-- DAILY HERO + STREAK -->
    <div class="grid lg:grid-cols-3 gap-4 mb-5 max-w-5xl mx-auto">
      <!-- Hero: 2 kolon -->
      <div class="lg:col-span-2">
        ${heroAuthor ? `
          <div class="rounded-2xl overflow-hidden ${heroTheme.bg} border-2 border-slate-200 dark:border-slate-700">
            <div class="p-5">
              <div class="flex items-center justify-between gap-2 mb-2">
                <span class="text-xs font-bold uppercase tracking-wider ${heroTheme.text} opacity-80">★ Şu Anki Yazar</span>
                <button id="heroReroll" class="text-xs px-2 py-1 rounded-full bg-white/70 dark:bg-slate-900/60 ${heroTheme.text} font-bold hover:bg-white">🔄 Yenile</button>
              </div>
              <h2 class="text-2xl md:text-3xl font-bold ${heroTheme.text} mb-2">${heroAuthor.name}</h2>
              <div class="flex flex-wrap gap-2 mb-3">
                <span class="text-xs px-2 py-0.5 rounded-full bg-white/70 dark:bg-slate-900/60 ${heroTheme.text} font-semibold">
                  <span class="inline-block w-1.5 h-1.5 rounded-full ${heroTheme.dot} align-middle mr-1"></span>${heroTheme.label}
                </span>
                <span class="text-xs px-2 py-0.5 rounded-full bg-white/70 dark:bg-slate-900/60 ${heroTheme.text} font-semibold">📖 ${heroAuthor.pozisyon || 'Çok yönlü'}</span>
                <span class="text-xs px-2 py-0.5 rounded-full bg-white/70 dark:bg-slate-900/60 ${heroTheme.text} font-semibold">${heroAuthor.soru_sayisi} soru / son ${Math.max(...heroAuthor.yillar)}</span>
              </div>
              ${heroAuthor.anekdot ? `
                <p class="text-sm italic ${heroTheme.text} leading-relaxed mb-3">"${heroAuthor.anekdot}"</p>
              ` : ''}
              <div class="flex flex-wrap gap-2">
                <a href="#/yazarlar/${heroSlug}" class="bg-white dark:bg-slate-900 ${heroTheme.text} px-4 py-2 rounded-md font-bold text-sm shadow">Profili Aç →</a>
                ${heroAuthor.klasik_tuzak ? `<details class="bg-white/70 dark:bg-slate-900/60 ${heroTheme.text} px-3 py-2 rounded-md text-xs"><summary class="cursor-pointer font-bold">⚠ ÖSYM Tuzağı</summary><p class="mt-2">${heroAuthor.klasik_tuzak}</p></details>` : ''}
              </div>
            </div>
            ${heroCard ? `
              <div class="bg-white/85 dark:bg-slate-900/85 p-4 border-t-2 border-slate-200 dark:border-slate-700">
                <div class="text-xs font-bold uppercase tracking-wider text-slate-500 mb-2">⚡ Hızlı Soru</div>
                <p class="text-sm mb-3">${heroCard.soru}</p>
                <div class="grid gap-1.5">
                  ${shuffle(heroCard.secenekler.map(o => ({...o}))).map(o => `
                    <button data-hero-opt="${o.id}" class="opt" ${heroAnswered ? 'disabled' : ''}>
                      <span class="opt-letter">${o.id}</span>
                      <span class="flex-1 text-sm">${o.text}</span>
                    </button>
                  `).join('')}
                </div>
                <div id="heroFeedback" class="mt-3 ${heroAnswered ? '' : 'hidden'} space-y-2">
                  <div class="ezber-box text-sm">
                    <strong>✓ Doğru cevap: ${heroCard.dogru}</strong><br>${heroCard.aciklama || ''}
                  </div>
                  ${heroCard.tuzak ? `<div class="tuzak-box text-sm"><strong>⚠ TUZAK</strong><br>${heroCard.tuzak}</div>` : ''}
                </div>
              </div>
            ` : ''}
          </div>
        ` : `
          <div class="rounded-2xl bg-slate-100 dark:bg-slate-800 p-6 text-center text-slate-500">Bugünün yazarı yükleniyor...</div>
        `}
      </div>

      <!-- Streak + Hızlı Atış CTA -->
      <div class="space-y-3">
        <div class="bg-white dark:bg-slate-900 border-2 border-accent-500/30 rounded-2xl p-4 text-center">
          <div class="text-xs uppercase tracking-wider text-slate-500 mb-1">🔥 Streak</div>
          <div class="text-4xl font-bold ${streakColor} mb-1">${sk.current}</div>
          <div class="text-xs text-slate-500 mb-2">${sk.current === 0 ? 'Henüz başlamadın' : sk.current === 1 ? '1 gün' : sk.current + ' gün üst üste'}</div>
          ${curBadge ? `<div class="text-xs">${curBadge.emoji} <strong>${curBadge.label}</strong> rozeti kazandın</div>` : ''}
          ${nxtBadge ? `<div class="text-[10px] text-slate-500 mt-1">Sonraki: ${nxtBadge.emoji} ${nxtBadge.label} (${nxtBadge.d - sk.current} gün)</div>` : ''}
          <div class="text-[10px] text-slate-500 mt-1">En uzun: ${sk.longest || 0} gün</div>
          ${sk.status === 'at_risk' ? `<div class="mt-2 text-xs text-warn-500 font-bold">⚠ Bugün soru çöz, kaybetme!</div>` : ''}
          ${sk.status === 'broken' ? `<div class="mt-2 text-xs text-accent-500">Seri koptu — yeniden başla</div>` : ''}
        </div>

        <a href="#/atis" class="block bg-gradient-to-br from-accent-500 to-accent-700 text-white rounded-2xl p-5 text-center shadow-lg hover:shadow-xl transition-all">
          <div class="text-4xl mb-1">⚡</div>
          <div class="text-lg font-bold">HIZLI ATIŞ</div>
          <div class="text-xs opacity-90 mt-1">Bas, soru gelsin — sonsuz mod</div>
          ${s.atis?.best_run > 0 ? `<div class="text-xs mt-2 bg-white/20 inline-block px-2 py-0.5 rounded">Best: ${s.atis.best_run} 🔥</div>` : ''}
        </a>
      </div>
    </div>

    ${totalSolved > 0 ? `
    <section class="grid grid-cols-3 gap-3 mb-5 max-w-3xl mx-auto">
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

    <section class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3 max-w-6xl mx-auto">
      ${shortcut('quiz/setup', '🎯', 'Quiz', 'Konu seç, çöz', 'accent')}
      ${shortcut('konular', '📚', '13 Konu', 'Öğretim + ezber', 'primary')}
      ${shortcut('yazarlar', '👤', '85 Yazar', 'Trading kartlar', 'primary')}
      ${shortcut('eserler', '📖', 'Eserler', '251 eser', 'primary')}
      ${shortcut('gruplar', '👥', 'Gruplar', 'Garip, II. Yeni...', 'primary')}
      ${shortcut('koleksiyon', '🎴', 'Koleksiyon', 'Kaç tanıdın?', 'accent')}
      ${shortcut('tahminler', '🔮', 'Tahminler', '2026 boşluk', 'primary')}
      ${shortcut('program', '📅', 'Program', '4 haftalık', 'primary')}
      ${shortcut('sozluk', '📓', 'Sözlük', 'Akım/eser', 'primary')}
      ${shortcut('kartlar', '🃏', 'Kartlar', `${allCards.length} kart`, 'primary')}
      ${shortcut('istatistik', '📊', 'İstatistik', 'İlerleme grafiği', 'primary')}
      ${shortcut('ayarlar', '⚙️', 'Ayarlar', 'Tema, sıfırla', 'primary')}
    </section>

    <section class="mt-8 max-w-3xl mx-auto bg-warn-500/10 border border-warn-500/30 rounded-lg p-4">
      <h3 class="font-bold mb-2 flex items-center gap-2 text-sm"><span>💡</span> Stratejin</h3>
      <ul class="text-xs text-slate-700 dark:text-slate-300 space-y-1 list-disc list-inside">
        <li>İlk 6 soru (sözcükte/cümlede/paragraf) pure yorum — pratik istiyor, ezberlenmez.</li>
        <li>Geri kalan 18 soru ezberlenebilir/konuya dayalı — <strong>15-20 net hedefin</strong> bu 18'den çıkar.</li>
        <li>Her gün gir, Hızlı Atış'a bas, yanlışlar otomatik geri gelir. Futbol kartı toplar gibi.</li>
      </ul>
    </section>
  `;
}

function shortcut(route, icon, title, desc, accent) {
  const accentClass = accent === 'accent'
    ? 'border-accent-500/30 hover:border-accent-500 hover:bg-accent-500/5'
    : 'border-primary-500/20 hover:border-primary-500 hover:bg-primary-50 dark:hover:bg-primary-900/30';
  return `
    <a href="#/${route}" class="block bg-white dark:bg-slate-900 border-2 ${accentClass} rounded-xl p-3 transition-all hover:shadow-md text-center">
      <div class="text-2xl mb-1">${icon}</div>
      <div class="font-bold text-sm mb-0.5">${title}</div>
      <p class="text-[10px] text-slate-500 line-clamp-1">${desc}</p>
    </a>
  `;
}
