import { Data, periodTheme, slugify, getDataSubject } from '../lib/data.js';
import { loadState } from '../lib/store.js';
import { tickStreak, streakInfo, currentBadge, nextBadge } from '../lib/streak.js';
import { dailyHero, maskAuthorName } from '../lib/daily.js';
import { dailyTarihHero, markDailyAnswered } from '../lib/daily-tarih.js';

function escape(s) {
  return String(s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}
function shuffle(arr) {
  const a = [...arr];
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

export async function renderHome() {
  const subject = getDataSubject();
  if (subject === 'tarih') return renderTarihHome();
  return renderEdebiyatHome();
}

async function renderTarihHome() {
  const s = loadState();
  const cards = await Data.cards();
  const periods = await Data.periods();
  const people = await Data.people();
  const treaties = await Data.treaties();
  const events = await Data.events();
  const glossary = await Data.glossary();
  const allCards = [...cards, ...s.custom_kartlar];

  const totalCorrect = Object.values(s.progress).reduce((a,p) => a + p.dogru, 0);
  const totalSolved = Object.values(s.progress).reduce((a,p) => a + p.cozuldu, 0);
  const accuracy = totalSolved > 0 ? Math.round((totalCorrect / totalSolved) * 100) : 0;
  const errorCount = s.hata_defteri.length;

  // En sıcak 3 dönem (soru sayısına göre)
  const hotPeriods = [...periods].sort((a, b) => (b.soru_sayisi || 0) - (a.soru_sayisi || 0)).slice(0, 6);

  // Daily Tarih Hero — günlük kişi/antlaşma/olay tahmin oyunu
  const hero = dailyTarihHero(people, treaties, events, glossary);

  // Streak
  const sk = streakInfo();
  const curBadge = currentBadge(sk.current);
  const nxtBadge = nextBadge(sk.current);
  const streakColor = sk.status === 'active_today' ? 'text-ok-500' : sk.status === 'at_risk' ? 'text-warn-500' : sk.status === 'broken' ? 'text-slate-400' : 'text-slate-400';

  window.__pageSetup = () => {
    function bumpStreak() {
      const sr = tickStreak();
      if (sr.bumped) {
        const toast = document.createElement('div');
        toast.className = 'fixed bottom-4 left-1/2 -translate-x-1/2 z-50 bg-amber-600 text-white px-4 py-2 rounded-lg shadow-lg text-sm font-bold';
        toast.textContent = `🔥 Streak ${sr.current} gün!`;
        document.body.appendChild(toast);
        setTimeout(() => toast.remove(), 2500);
      }
    }
    // Hero tahmin butonları
    const opts = document.querySelectorAll('[data-hero-opt]');
    let answered = false;
    opts.forEach(btn => {
      btn.addEventListener('click', () => {
        if (answered) return;
        answered = true;
        const isCorrect = btn.dataset.heroOpt === 'correct';
        opts.forEach(b => {
          b.disabled = true;
          if (b.dataset.heroOpt === 'correct') b.classList.add('correct');
          if (b === btn && !isCorrect) b.classList.add('wrong');
        });
        document.getElementById('heroGuess')?.classList.add('hidden');
        document.getElementById('heroReveal')?.classList.remove('hidden');
        if (hero?.entityId) markDailyAnswered(hero.entityId, isCorrect);
        bumpStreak();
      });
    });
  };

  return `
    <section class="text-center mb-6">
      <h1 class="text-2xl md:text-3xl font-bold mb-1" style="color:#B45309;">
        AYT Tarih <span style="color:#991B1B;">Hardcore</span>
      </h1>
      <p class="text-slate-600 dark:text-slate-400 text-sm max-w-2xl mx-auto">
        Tarihçi olma, tarihi yendin sayılır. 10 dönem · 671 kart · 8 yıllık ÖSYM analizi.
      </p>
    </section>

    <div class="grid lg:grid-cols-3 gap-4 mb-5 max-w-5xl mx-auto">
      <!-- Sol: Daily Tarih Hero (kişi/antlaşma/olay tahmin) -->
      <div class="lg:col-span-2">
        ${hero ? renderTarihHeroCard(hero) : `
          <div class="bg-amber-50 dark:bg-amber-900/20 rounded-2xl border-2 border-amber-500/30 p-5 text-center text-slate-600 dark:text-slate-300">
            Bugün için Daily Hero yüklenemedi. (Veri henüz tam dolu değil)
          </div>
        `}

        <div class="mt-3 bg-amber-50 dark:bg-amber-900/20 rounded-2xl border-2 border-amber-500/30 p-4">
          <div class="flex items-center justify-between mb-2">
            <span class="text-xs font-bold uppercase tracking-wider text-amber-800 dark:text-amber-200">🔥 En Sıcak 6 Dönem</span>
            <a href="#/konular" class="text-xs px-2 py-1 rounded-full bg-white/70 dark:bg-slate-900/60 text-amber-800 dark:text-amber-200 font-bold">Tüm Dönemler →</a>
          </div>
          <div class="grid sm:grid-cols-2 gap-1.5">
            ${hotPeriods.map(p => `
              <a href="#/konular/${p.slug}" class="block bg-white/85 dark:bg-slate-900/85 rounded-md px-2 py-1.5 hover:shadow-md transition-all">
                <div class="flex items-center justify-between">
                  <span class="font-bold text-xs" style="color:#B45309;">${escape(p.ad)}</span>
                  <span class="text-xs font-bold bg-amber-500/20 text-amber-800 dark:text-amber-200 px-1.5 py-0.5 rounded-full">${p.soru_sayisi}</span>
                </div>
              </a>
            `).join('')}
          </div>

          <div class="mt-3 grid sm:grid-cols-3 gap-1.5">
            <a href="#/tahminler" class="text-xs bg-amber-500 text-white px-2 py-1.5 rounded font-bold text-center hover:bg-amber-600">🔮 2026 Tahminleri</a>
            <a href="#/program" class="text-xs bg-amber-700 text-white px-2 py-1.5 rounded font-bold text-center hover:bg-amber-800">📅 Program</a>
            <a href="#/quiz/setup" class="text-xs bg-red-700 text-white px-2 py-1.5 rounded font-bold text-center hover:bg-red-800">🎯 Quiz</a>
          </div>
        </div>
      </div>

      <!-- Sağ: Streak + Hızlı Atış -->
      <div class="space-y-3">
        <div class="bg-white dark:bg-slate-900 border-2 border-amber-500/30 rounded-2xl p-4 text-center">
          <div class="text-xs uppercase tracking-wider text-slate-500 mb-1">🔥 Streak</div>
          <div class="text-4xl font-bold ${streakColor} mb-1">${sk.current}</div>
          <div class="text-xs text-slate-500 mb-2">${sk.current === 0 ? 'Henüz başlamadın' : sk.current === 1 ? '1 gün' : sk.current + ' gün üst üste'}</div>
          ${curBadge ? `<div class="text-xs">${curBadge.emoji} <strong>${curBadge.label}</strong> rozeti</div>` : ''}
          ${nxtBadge ? `<div class="text-[10px] text-slate-500 mt-1">Sonraki: ${nxtBadge.emoji} ${nxtBadge.label} (${nxtBadge.d - sk.current} gün)</div>` : ''}
          <div class="text-[10px] text-slate-500 mt-1">En uzun: ${sk.longest || 0} gün</div>
          ${sk.status === 'at_risk' ? `<div class="mt-2 text-xs text-warn-500 font-bold">⚠ Bugün soru çöz, kaybetme!</div>` : ''}
        </div>

        <a href="#/atis" class="block bg-gradient-to-br from-amber-500 to-red-700 text-white rounded-2xl p-5 text-center shadow-lg hover:shadow-xl transition-all">
          <div class="text-4xl mb-1">⚡</div>
          <div class="text-lg font-bold">HIZLI ATIŞ</div>
          <div class="text-xs opacity-90 mt-1">Bas, soru gelsin — sonsuz mod</div>
          ${s.atis?.best_run > 0 ? `<div class="text-xs mt-2 bg-white/20 inline-block px-2 py-0.5 rounded">Best: ${s.atis.best_run} 🔥</div>` : ''}
        </a>
      </div>
    </div>

    ${totalSolved > 0 ? `
    <section class="grid grid-cols-3 gap-3 mb-5 max-w-3xl mx-auto">
      <div class="bg-amber-50 dark:bg-amber-900/40 rounded-lg p-3 text-center">
        <div class="text-2xl font-bold" style="color:#B45309;">${totalSolved}</div>
        <div class="text-xs text-slate-600 dark:text-slate-400">Çözülen</div>
      </div>
      <div class="bg-ok-500/10 dark:bg-ok-500/20 rounded-lg p-3 text-center">
        <div class="text-2xl font-bold text-ok-500">%${accuracy}</div>
        <div class="text-xs text-slate-600 dark:text-slate-400">Doğruluk</div>
      </div>
      <div class="bg-red-500/10 dark:bg-red-500/20 rounded-lg p-3 text-center">
        <div class="text-2xl font-bold text-red-700 dark:text-red-300">${errorCount}</div>
        <div class="text-xs text-slate-600 dark:text-slate-400">Hata defteri</div>
      </div>
    </section>
    ` : ''}

    <section class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3 max-w-6xl mx-auto">
      ${shortcut('quiz/setup', '🎯', 'Quiz', 'Konu seç, çöz', 'accent')}
      ${shortcut('konular', '⏳', `${periods.length} Dönem`, 'Öğretim + ezber', 'primary')}
      ${shortcut('yazarlar', '👤', `${people.length} Kişi`, 'Padişah, lider', 'primary')}
      ${shortcut('eserler', '⚔️', 'Olaylar', `${events.length} savaş`, 'primary')}
      ${shortcut('gruplar', '🏛️', 'Hanedanlar', 'Osmanlı, Selçuklu...', 'primary')}
      ${shortcut('koleksiyon', '🎴', 'Koleksiyon', 'Kaç tanıdın?', 'accent')}
      ${shortcut('tahminler', '🔮', 'Tahminler', '2026 boşluk', 'primary')}
      ${shortcut('program', '📅', 'Program', '4 haftalık', 'accent')}
      ${shortcut('sozluk', '📓', 'Sözlük', `${treaties.length} antlaşma`, 'primary')}
      ${shortcut('kartlar', '🃏', 'Kartlar', `${allCards.length} kart`, 'primary')}
      ${shortcut('istatistik', '📊', 'İstatistik', 'İlerleme grafiği', 'primary')}
      ${shortcut('ayarlar', '⚙️', 'Ayarlar', 'Tema, sıfırla', 'primary')}
    </section>

    <section class="mt-8 max-w-3xl mx-auto bg-amber-500/10 border border-amber-500/30 rounded-lg p-4">
      <h3 class="font-bold mb-2 flex items-center gap-2 text-sm"><span>💡</span> Stratejin</h3>
      <ul class="text-xs text-slate-700 dark:text-slate-300 space-y-1 list-disc list-inside">
        <li><strong>Millî Mücadele</strong> + <strong>İslam Öncesi Türk</strong> 8 yılın hepsinde 2+ soru. Her gün bu iki dönemi tekrar et.</li>
        <li><strong>Osmanlı Yükseliş</strong> (Yavuz/Kanuni) 2018-25 sadece 4 soru — 2026 sürpriz adayı. Boşluğu kapat.</li>
        <li>671 kart × günlük 30-40 = 3 haftada tüm konu tamam. Hızlı Atış'ı her gün aç.</li>
      </ul>
    </section>
  `;
}

async function renderEdebiyatHome() {
  const s = loadState();
  const authors = await Data.authors();
  const cards = await Data.cards();
  let works = [];
  try { works = await Data.works(); } catch(e) { /* opsiyonel */ }
  const allCards = [...cards, ...s.custom_kartlar];

  const totalCorrect = Object.values(s.progress).reduce((a,p) => a + p.dogru, 0);
  const totalSolved = Object.values(s.progress).reduce((a,p) => a + p.cozuldu, 0);
  const accuracy = totalSolved > 0 ? Math.round((totalCorrect / totalSolved) * 100) : 0;
  const errorCount = s.hata_defteri.length;

  // REV11+12 — Daily Hero karışık mod + yan sanayi soru
  const hero = dailyHero(authors, works);
  const heroAuthor = hero.author;
  const heroMode = hero.mode;  // 'eser' | 'yazar' | 'none'
  const eserSoru = hero.eserSoru;
  const yazarSoru = hero.yazarSoru;
  const sideQ = hero.sideQ;  // yan sanayi sorusu
  const heroSlug = heroAuthor ? slugify(heroAuthor.name) : '';
  const heroTheme = heroAuthor ? periodTheme(heroAuthor.donem || heroAuthor.konular?.[0]) : null;
  // REV13 — otherEserler kaldırıldı (spoiler önleme). Detay için "Profili Aç" butonu.
  const maskedAnekdot = heroAuthor ? maskAuthorName(heroAuthor.anekdot || '', heroAuthor.name) : '';

  // Streak
  const sk = streakInfo();
  const curBadge = currentBadge(sk.current);
  const nxtBadge = nextBadge(sk.current);
  const streakColor = sk.status === 'active_today' ? 'text-ok-500' : sk.status === 'at_risk' ? 'text-warn-500' : sk.status === 'broken' ? 'text-slate-400' : 'text-slate-400';

  window.__pageSetup = () => {
    document.getElementById('heroReroll')?.addEventListener('click', () => {
      window.dispatchEvent(new HashChangeEvent('hashchange'));
    });

    function bumpStreak() {
      const streakRes = tickStreak();
      if (streakRes.bumped) {
        const toast = document.createElement('div');
        toast.className = 'fixed bottom-4 left-1/2 -translate-x-1/2 z-50 bg-accent-500 text-white px-4 py-2 rounded-lg shadow-lg text-sm font-bold';
        toast.textContent = `🔥 Streak ${streakRes.current} gün!`;
        document.body.appendChild(toast);
        setTimeout(() => toast.remove(), 2500);
      }
    }

    function bindOpts(selector, dataKey, guessId, revealId, onAfter) {
      const opts = document.querySelectorAll(selector);
      let answered = false;
      opts.forEach(btn => {
        btn.addEventListener('click', () => {
          if (answered) return;
          answered = true;
          const isCorrect = btn.dataset[dataKey] === 'correct';
          opts.forEach(b => {
            b.disabled = true;
            if (b.dataset[dataKey] === 'correct') b.classList.add('correct');
            if (b === btn && !isCorrect) b.classList.add('wrong');
          });
          document.getElementById(guessId)?.classList.add('hidden');
          document.getElementById(revealId)?.classList.remove('hidden');
          bumpStreak();
          // Yan sanayi sorusu varsa onu göster
          if (typeof onAfter === 'function') onAfter();
        });
      });
    }

    function showSide() {
      const side = document.getElementById('sideGuess');
      if (side) side.classList.remove('hidden');
      // Side şıkları bind
      bindOpts('[data-side-opt]', 'sideOpt', 'sideGuess', 'sideReveal', null);
    }

    if (heroMode === 'eser' && eserSoru) {
      bindOpts('[data-eser-opt]', 'eserOpt', 'eserGuess', 'eserReveal', sideQ ? showSide : null);
    } else if (heroMode === 'yazar' && yazarSoru) {
      bindOpts('[data-yazar-opt]', 'yazarOpt', 'yazarGuess', 'yazarReveal', sideQ ? showSide : null);
    }
  };

  return `
    <section class="text-center mb-6">
      <h1 class="text-2xl md:text-3xl font-bold text-primary-700 dark:text-primary-100 mb-1">
        AYT Edebiyat <span class="text-accent-500">Hardcore</span>
      </h1>
      <p class="text-slate-600 dark:text-slate-400 text-sm max-w-2xl mx-auto">
        Futbol kartı gibi yazarı tahmin et. Her gün gir, hata yap, sürekli karşılaş — ezberlemeden ezberle.
      </p>
    </section>

    <!-- DAILY HERO TAHMİN OYUNU + STREAK -->
    <div class="grid lg:grid-cols-3 gap-4 mb-5 max-w-5xl mx-auto">
      <!-- Hero: 2 kolon -->
      <div class="lg:col-span-2">
        ${heroAuthor ? `
          <div class="rounded-2xl overflow-hidden ${heroTheme.bg} border-2 border-slate-200 dark:border-slate-700">
            <div class="p-5">
              <div class="flex items-center justify-between gap-2 mb-3">
                <span class="text-xs font-bold uppercase tracking-wider ${heroTheme.text} opacity-80">★ ${heroMode === 'yazar' ? 'Şu Anki Eser' : 'Şu Anki Yazar'}</span>
                <button id="heroReroll" class="text-xs px-2 py-1 rounded-full bg-white/70 dark:bg-slate-900/60 ${heroTheme.text} font-bold hover:bg-white">🔄 Yenile</button>
              </div>

              ${heroMode === 'eser' && eserSoru ? `
                <!-- MOD A: YAZAR GÖRÜNÜR → ESER SORULUR -->
                <h2 class="text-2xl md:text-3xl font-bold ${heroTheme.text} mb-3">${escape(heroAuthor.name)}</h2>
                <div class="flex flex-wrap gap-2 mb-3">
                  <span class="text-xs px-2 py-0.5 rounded-full bg-white/70 dark:bg-slate-900/60 ${heroTheme.text} font-semibold"><span class="inline-block w-1.5 h-1.5 rounded-full ${heroTheme.dot} align-middle mr-1"></span>${heroTheme.label}</span>
                  <span class="text-xs px-2 py-0.5 rounded-full bg-white/70 dark:bg-slate-900/60 ${heroTheme.text} font-semibold">📖 ${heroAuthor.pozisyon || 'Çok yönlü'}</span>
                  <span class="text-xs px-2 py-0.5 rounded-full bg-white/70 dark:bg-slate-900/60 ${heroTheme.text} font-semibold">${heroAuthor.soru_sayisi} soru / son ${Math.max(...heroAuthor.yillar)}</span>
                </div>
                ${heroAuthor.anekdot ? `<p class="text-sm italic ${heroTheme.text} leading-relaxed mb-3">"${escape(heroAuthor.anekdot)}"</p>` : ''}
                ${heroAuthor.klasik_tuzak ? `
                  <div class="bg-accent-500/15 border border-accent-500/40 rounded-lg p-3 mb-3">
                    <div class="text-[10px] font-bold uppercase ${heroTheme.text} opacity-80 mb-1">⚠ Klasik ÖSYM Tuzağı</div>
                    <p class="text-xs ${heroTheme.text}">${escape(heroAuthor.klasik_tuzak)}</p>
                  </div>
                ` : ''}

                <div id="eserGuess" class="bg-white/85 dark:bg-slate-900/85 rounded-lg p-4 mt-3">
                  <div class="text-xs font-bold uppercase tracking-wider text-slate-600 dark:text-slate-300 mb-3">📚 Sence onun eserlerinden hangisi?</div>
                  <div class="grid gap-1.5">
                    ${eserSoru.choices.map(c => `
                      <button data-eser-opt="${c.isCorrect ? 'correct' : 'wrong'}" class="opt">
                        <span class="opt-letter">${c.id}</span>
                        <span class="flex-1 text-sm">${escape(c.title)}</span>
                      </button>
                    `).join('')}
                  </div>
                </div>

                <div id="eserReveal" class="hidden mt-3">
                  <div class="bg-ok-500/15 border border-ok-500/40 rounded-lg p-3 mb-3">
                    <div class="text-[10px] font-bold uppercase ${heroTheme.text} opacity-80 mb-1">✓ Doğru Eser</div>
                    <div class="text-lg font-bold ${heroTheme.text}">${escape(eserSoru.dogruEser.title)}</div>
                    <div class="text-xs ${heroTheme.text} opacity-80 mt-1">${eserSoru.dogruEser.tur || ''} ${eserSoru.dogruEser.yil ? '· ' + eserSoru.dogruEser.yil : ''}</div>
                    <div class="mt-2">
                      <span class="inline-flex items-center gap-1 text-[10px] font-bold px-2 py-0.5 rounded ${eserSoru.dogruEser.cikmis ? "bg-warn-500/30 text-warn-500" : "bg-primary-50 dark:bg-primary-900/40 text-primary-700 dark:text-primary-100"}">
                        ${eserSoru.dogruEser.cikmis ? "⭐ ÖSYM'de soruldu" : "📘 MEBİ kapsamında — ÖSYM henüz sormadı"}
                      </span>
                    </div>
                  </div>
                </div>

                ${sideQ?.dogruCagdas ? `
                  <!-- YAN SANAYİ: çağdaş tahmin (Mod A) -->
                  <div id="sideGuess" class="hidden bg-white/85 dark:bg-slate-900/85 rounded-lg p-4 mt-3 border-2 border-dashed ${heroTheme.text} border-current/30">
                    <div class="text-xs font-bold uppercase tracking-wider text-slate-600 dark:text-slate-300 mb-3">👥 Peki çağdaşlarından (aynı dönem) hangisi?</div>
                    <div class="grid gap-1.5">
                      ${sideQ.choices.map(c => `
                        <button data-side-opt="${c.isCorrect ? 'correct' : 'wrong'}" class="opt">
                          <span class="opt-letter">${c.id}</span>
                          <span class="flex-1 text-sm">${escape(c.name)}</span>
                        </button>
                      `).join('')}
                    </div>
                  </div>
                  <div id="sideReveal" class="hidden mt-3">
                    <div class="bg-ok-500/15 border border-ok-500/40 rounded-lg p-3 mb-3">
                      <div class="text-[10px] font-bold uppercase ${heroTheme.text} opacity-80 mb-1">✓ Çağdaş Yazar</div>
                      <div class="text-lg font-bold ${heroTheme.text}">${escape(sideQ.dogruCagdas.name)}</div>
                      <div class="text-xs ${heroTheme.text} opacity-80 mt-1">${heroTheme.label} · ${sideQ.dogruCagdas.pozisyon || ''}</div>
                    </div>
                  </div>
                ` : ''}
              ` : heroMode === 'yazar' && yazarSoru ? `
                <!-- MOD B: ESER GÖRÜNÜR → YAZAR SORULUR -->
                <h2 class="text-2xl md:text-3xl font-bold ${heroTheme.text} mb-3">${escape(yazarSoru.targetEser.title)}</h2>
                <div class="flex flex-wrap gap-2 mb-3">
                  <span class="text-xs px-2 py-0.5 rounded-full bg-white/70 dark:bg-slate-900/60 ${heroTheme.text} font-semibold"><span class="inline-block w-1.5 h-1.5 rounded-full ${heroTheme.dot} align-middle mr-1"></span>${heroTheme.label}</span>
                  <span class="text-xs px-2 py-0.5 rounded-full bg-white/70 dark:bg-slate-900/60 ${heroTheme.text} font-semibold">📖 ${yazarSoru.targetEser.tur || 'Eser'}</span>
                  ${yazarSoru.targetEser.yil ? `<span class="text-xs px-2 py-0.5 rounded-full bg-white/70 dark:bg-slate-900/60 ${heroTheme.text} font-semibold">📅 ${yazarSoru.targetEser.yil}</span>` : ''}
                  <span class="text-xs px-2 py-0.5 rounded-full font-bold ${yazarSoru.targetEser.cikmis ? 'bg-warn-500/30 text-warn-500' : 'bg-primary-50 dark:bg-primary-900/40 text-primary-700 dark:text-primary-100'}">
                    ${yazarSoru.targetEser.cikmis ? "⭐ ÖSYM'de" : "📘 MEBİ"}
                  </span>
                </div>
                ${maskedAnekdot ? `<p class="text-sm italic ${heroTheme.text} leading-relaxed mb-3">İpucu: "${escape(maskedAnekdot)}"</p>` : ''}

                <div id="yazarGuess" class="bg-white/85 dark:bg-slate-900/85 rounded-lg p-4 mt-3">
                  <div class="text-xs font-bold uppercase tracking-wider text-slate-600 dark:text-slate-300 mb-3">👤 Sence bu eserin yazarı kim?</div>
                  <div class="grid gap-1.5">
                    ${yazarSoru.choices.map(c => `
                      <button data-yazar-opt="${c.isCorrect ? 'correct' : 'wrong'}" class="opt">
                        <span class="opt-letter">${c.id}</span>
                        <span class="flex-1 text-sm">${escape(c.name)}</span>
                      </button>
                    `).join('')}
                  </div>
                </div>

                <div id="yazarReveal" class="hidden mt-3">
                  <div class="bg-ok-500/15 border border-ok-500/40 rounded-lg p-3 mb-3">
                    <div class="text-[10px] font-bold uppercase ${heroTheme.text} opacity-80 mb-1">✓ Doğru Yazar</div>
                    <div class="text-lg font-bold ${heroTheme.text}">${escape(heroAuthor.name)}</div>
                    <div class="text-xs ${heroTheme.text} opacity-80 mt-1">${heroTheme.label} · ${heroAuthor.pozisyon || ''}</div>
                  </div>
                  ${heroAuthor.anekdot ? `<p class="text-sm italic ${heroTheme.text} leading-relaxed mb-3">"${escape(heroAuthor.anekdot)}"</p>` : ''}
                  ${heroAuthor.klasik_tuzak ? `
                    <div class="bg-accent-500/15 border border-accent-500/40 rounded-lg p-3 mb-3">
                      <div class="text-[10px] font-bold uppercase ${heroTheme.text} opacity-80 mb-1">⚠ Klasik ÖSYM Tuzağı</div>
                      <p class="text-xs ${heroTheme.text}">${escape(heroAuthor.klasik_tuzak)}</p>
                    </div>
                  ` : ''}
                </div>

                ${sideQ?.dogruEser ? `
                  <!-- YAN SANAYİ: aynı yazarın başka eseri (Mod B) -->
                  <div id="sideGuess" class="hidden bg-white/85 dark:bg-slate-900/85 rounded-lg p-4 mt-3 border-2 border-dashed ${heroTheme.text} border-current/30">
                    <div class="text-xs font-bold uppercase tracking-wider text-slate-600 dark:text-slate-300 mb-3">📚 Peki onun BAŞKA bir eseri?</div>
                    <div class="grid gap-1.5">
                      ${sideQ.choices.map(c => `
                        <button data-side-opt="${c.isCorrect ? 'correct' : 'wrong'}" class="opt">
                          <span class="opt-letter">${c.id}</span>
                          <span class="flex-1 text-sm">${escape(c.title)}</span>
                        </button>
                      `).join('')}
                    </div>
                  </div>
                  <div id="sideReveal" class="hidden mt-3">
                    <div class="bg-ok-500/15 border border-ok-500/40 rounded-lg p-3 mb-3">
                      <div class="text-[10px] font-bold uppercase ${heroTheme.text} opacity-80 mb-1">✓ Başka Bir Eseri</div>
                      <div class="text-lg font-bold ${heroTheme.text}">${escape(sideQ.dogruEser.title)}</div>
                      <div class="text-xs ${heroTheme.text} opacity-80 mt-1">${sideQ.dogruEser.tur || ''}</div>
                      <div class="mt-2">
                        <span class="inline-flex items-center gap-1 text-[10px] font-bold px-2 py-0.5 rounded ${sideQ.dogruEser.cikmis ? 'bg-warn-500/30 text-warn-500' : 'bg-primary-50 dark:bg-primary-900/40 text-primary-700 dark:text-primary-100'}">
                          ${sideQ.dogruEser.cikmis ? "⭐ ÖSYM'de soruldu" : "📘 MEBİ kapsamında — ÖSYM henüz sormadı"}
                        </span>
                      </div>
                    </div>
                  </div>
                ` : ''}
              ` : `
                <!-- Fallback: yazarın hiç eseri yok, sadece tanıtım -->
                <h2 class="text-2xl md:text-3xl font-bold ${heroTheme.text} mb-3">${escape(heroAuthor.name)}</h2>
                <div class="flex flex-wrap gap-2 mb-3">
                  <span class="text-xs px-2 py-0.5 rounded-full bg-white/70 dark:bg-slate-900/60 ${heroTheme.text} font-semibold"><span class="inline-block w-1.5 h-1.5 rounded-full ${heroTheme.dot} align-middle mr-1"></span>${heroTheme.label}</span>
                  <span class="text-xs px-2 py-0.5 rounded-full bg-white/70 dark:bg-slate-900/60 ${heroTheme.text} font-semibold">📖 ${heroAuthor.pozisyon || 'Çok yönlü'}</span>
                </div>
                ${heroAuthor.anekdot ? `<p class="text-sm italic ${heroTheme.text} leading-relaxed mb-3">"${escape(heroAuthor.anekdot)}"</p>` : ''}
              `}

              <div class="flex flex-wrap gap-2 mt-3">
                <a href="#/yazarlar/${heroSlug}" class="bg-white dark:bg-slate-900 ${heroTheme.text} px-4 py-2 rounded-md font-bold text-sm shadow">Profili Aç →</a>
                <a href="#/atis?yazar=${heroSlug}" class="bg-accent-500 text-white px-4 py-2 rounded-md font-bold text-sm shadow">⚡ Bu yazardan Hızlı Atış</a>
              </div>
            </div>
          </div>
        ` : `
          <div class="rounded-2xl bg-slate-100 dark:bg-slate-800 p-6 text-center text-slate-500">Yazar yükleniyor...</div>
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
      ${shortcut('program', '📅', 'Program', '4 haftalık', 'accent')}
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

function renderTarihHeroCard(hero) {
  if (!hero || !hero.choices) return '';
  const mode = hero.mode;

  // Mod-spesifik metinler ve veri
  let modBadge, modQuestion, ipucu, hint, revealTitle, revealBody;
  if (mode === 'kisi') {
    modBadge = '★ TARİHÎ ŞAHSİYET';
    modQuestion = '👤 Sence bu tanım kime ait?';
    ipucu = hero.anekdot || '';
    hint = `İpucu: <em>"${escape(ipucu)}"</em>`;
    revealTitle = '✓ Doğru Kişi';
    revealBody = `<div class="text-lg font-bold" style="color:#B45309;">${escape(hero.target.name)}</div>
                  <div class="text-xs text-slate-600 dark:text-slate-300 mt-1">${escape(hero.target.donem || '')}</div>`;
  } else if (mode === 'antlasma') {
    modBadge = '★ TARİHÎ ANTLAŞMA';
    modQuestion = '📜 Sence bu hangi antlaşma?';
    ipucu = hero.ipucu || '';
    hint = `İpucu (ana madde): <em>${escape(ipucu.slice(0, 220))}</em>`;
    revealTitle = '✓ Doğru Antlaşma';
    revealBody = `<div class="text-lg font-bold" style="color:#B45309;">${escape(hero.target.isim)} (${hero.target.yil})</div>
                  <div class="text-xs text-slate-600 dark:text-slate-300 mt-1">${escape(hero.target.taraflar)}</div>
                  <div class="text-xs text-slate-600 dark:text-slate-300 mt-2">📌 ${escape(hero.target.sonuc || '')}</div>`;
  } else if (mode === 'olay') {
    modBadge = '★ TARİHÎ SAVAŞ';
    modQuestion = '⚔️ Sence bu hangi savaş/olay?';
    ipucu = hero.sebep || '';
    hint = `İpucu (sebep): <em>${escape(ipucu.slice(0, 220))}</em>`;
    revealTitle = '✓ Doğru Olay';
    revealBody = `<div class="text-lg font-bold" style="color:#B45309;">${escape(hero.target.isim)} (${hero.target.yil})</div>
                  <div class="text-xs text-slate-600 dark:text-slate-300 mt-1">${escape(hero.target.taraflar)}</div>
                  <div class="text-xs text-slate-600 dark:text-slate-300 mt-2">📌 Sonuç: ${escape(hero.target.sonuc || '')}</div>`;
  }

  return `
    <div class="rounded-2xl overflow-hidden bg-gradient-to-br from-amber-50 to-orange-50 dark:from-amber-900/30 dark:to-orange-900/20 border-2 border-amber-500/40">
      <div class="p-5">
        <div class="flex items-center justify-between gap-2 mb-3">
          <span class="text-xs font-bold uppercase tracking-wider text-amber-800 dark:text-amber-200 opacity-90">${modBadge}</span>
          <a href="#/" class="text-xs px-2 py-1 rounded-full bg-white/70 dark:bg-slate-900/60 text-amber-800 dark:text-amber-200 font-bold hover:bg-white">🔄 Yenile</a>
        </div>

        <p class="text-sm md:text-base text-slate-700 dark:text-slate-200 leading-relaxed mb-4">${hint}</p>

        <div id="heroGuess" class="bg-white/85 dark:bg-slate-900/85 rounded-lg p-4">
          <div class="text-xs font-bold uppercase tracking-wider text-slate-600 dark:text-slate-300 mb-3">${modQuestion}</div>
          <div class="grid gap-1.5">
            ${hero.choices.map(c => `
              <button data-hero-opt="${c.isCorrect ? 'correct' : 'wrong'}" class="opt">
                <span class="opt-letter">${c.id}</span>
                <span class="flex-1 text-sm">${escape(c.name)}${c.yil ? ` <span class="text-xs text-slate-500">(${c.yil})</span>` : ''}</span>
              </button>
            `).join('')}
          </div>
        </div>

        <div id="heroReveal" class="hidden mt-3 bg-ok-500/15 border border-ok-500/40 rounded-lg p-3">
          <div class="text-[10px] font-bold uppercase text-amber-800 dark:text-amber-200 opacity-80 mb-1">${revealTitle}</div>
          ${revealBody}
        </div>
      </div>
    </div>
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
