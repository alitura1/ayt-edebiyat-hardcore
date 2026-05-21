// REV27 — Tarih Daily Hero: Edebiyat tarzı 2 yönlü eşleme
// 5 mod: olay-padisah, padisah-olay, yil-antlasma, antlasma-yil, yil-savas
// İpucu göster → entite tahmin et + yan sanayi sorusu
// Edebiyat'taki "Bu eser kimin?" / "Bu yazarın eseri hangisi?" pattern'i

import { loadState, saveState } from './store.js';

function todayKey() {
  return new Date().toISOString().slice(0, 10);
}

function shuffle(arr) {
  const a = [...arr];
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

function pickRandom(arr, n) {
  return shuffle(arr).slice(0, n);
}

// Gün bazlı deterministic random (aynı gün aynı soru)
function dayRandom(seed) {
  let s = 0;
  for (const ch of seed) s = (s * 31 + ch.charCodeAt(0)) >>> 0;
  return () => {
    s = (s * 1103515245 + 12345) >>> 0;
    return (s / 0xffffffff);
  };
}

// Padişah tablosunu glossary'den parse et
// satır: [sira, isim, yillar, olaylar, donem]
function parsePadisahlar(glossary) {
  if (!glossary?.bolumler) return [];
  const padisahBolum = glossary.bolumler.find(b => b.baslik && b.baslik.includes('Padişah'));
  if (!padisahBolum?.satirlar) return [];
  return padisahBolum.satirlar
    .map(row => ({
      sira: row[0],
      isim: row[1],
      yillar: row[2],
      olaylar: row[3] || '',
      donem: row[4] || '',
    }))
    .filter(p => p.isim && p.isim !== 'Fetret Devri' && p.olaylar.length > 10);
}

function firstOlay(padisahOlaylar) {
  return (padisahOlaylar.split(',')[0] || '').trim();
}

export function dailyTarihHero(people, treaties, events, glossary) {
  const state = loadState();
  const tk = todayKey();
  const seen = state.daily_hero?.seen || {};

  // Bugün için cache var mı?
  if (seen[tk] && seen[tk].entityId) {
    return seen[tk];
  }

  const rand = dayRandom(tk);
  const padisahlar = parsePadisahlar(glossary);
  const wars = (events || []).filter(e => e.tur === 'savas');

  // Mevcut modları belirle
  const modes = [];
  if (padisahlar.length >= 5) {
    modes.push('olay-padisah'); // Olay göster → padişah tahmin
    modes.push('padisah-olay'); // Padişah göster → olay tahmin
  }
  if (treaties && treaties.length >= 5) {
    modes.push('yil-antlasma');   // Yıl göster → antlaşma tahmin
    modes.push('antlasma-yil');   // Antlaşma göster → yıl tahmin
  }
  if (wars.length >= 5) {
    modes.push('yil-savas');      // Yıl göster → savaş tahmin
  }
  if (modes.length === 0) return null;

  const mode = modes[Math.floor(rand() * modes.length)];
  let hero = null;

  if (mode === 'olay-padisah') {
    // İPUCU: padişahın ilk önemli olayı. DOĞRU: padişah adı. 4 çeldirici: aynı dönemden padişahlar
    const target = padisahlar[Math.floor(rand() * padisahlar.length)];
    const olay = firstOlay(target.olaylar);
    if (!olay || olay.length < 8) return null;

    const sameDonem = padisahlar.filter(p => p.donem === target.donem && p.isim !== target.isim);
    let distractors = pickRandom(sameDonem, 4);
    if (distractors.length < 4) {
      // Fallback: tüm padişahlardan ekle
      const others = padisahlar.filter(p => p.isim !== target.isim && !distractors.find(d => d.isim === p.isim));
      distractors = distractors.concat(pickRandom(others, 4 - distractors.length));
    }

    const choices = shuffle([target, ...distractors]).map((p, i) => ({
      id: String.fromCharCode(65 + i),
      name: p.isim,
      isCorrect: p.isim === target.isim,
    }));

    // Yan sanayi: aynı dönemden çağdaş padişah
    const cagdas = sameDonem[0]?.isim || padisahlar.find(p => p.donem === target.donem && p.isim !== target.isim)?.isim || '—';

    hero = {
      mode: 'olay-padisah',
      entityId: `olay-padisah-${target.isim}`,
      ipucu_label: 'Bu olay/icraat hangi padişaha aittir?',
      ipucu: olay,
      donem: target.donem,
      donem_yillar: target.yillar,
      choices,
      yan_label: 'Yan Soru — Çağdaşı kim?',
      yan_cevap: cagdas,
      target_name: target.isim,
    };
  } else if (mode === 'padisah-olay') {
    // İPUCU: padişah adı + yıllar. DOĞRU: olay. 4 çeldirici: aynı dönem başka padişahların olayları
    const candidates = padisahlar.filter(p => firstOlay(p.olaylar).length > 8);
    if (candidates.length < 5) return null;
    const target = candidates[Math.floor(rand() * candidates.length)];
    const dogruOlay = firstOlay(target.olaylar);

    const sameDonem = candidates.filter(p => p.donem === target.donem && p.isim !== target.isim);
    let pool = sameDonem;
    if (pool.length < 4) {
      pool = candidates.filter(p => p.isim !== target.isim);
    }
    const wrong_picked = pickRandom(pool, 4);
    const choices = shuffle([
      { id: 'X', name: dogruOlay, isCorrect: true },
      ...wrong_picked.map(p => ({ id: 'X', name: firstOlay(p.olaylar), isCorrect: false })),
    ]).map((c, i) => ({ ...c, id: String.fromCharCode(65 + i) }));

    // Yan sanayi: aynı padişahın 2. olayı
    const olaylar = target.olaylar.split(',').map(s => s.trim()).filter(o => o.length > 8);
    const yan = olaylar[1] || olaylar[0] || '—';

    hero = {
      mode: 'padisah-olay',
      entityId: `padisah-olay-${target.isim}`,
      ipucu_label: `${target.isim} (${target.yillar}) hangi olayı/icraatı gerçekleştirmiştir?`,
      ipucu: `${target.isim} — ${target.donem} dönemi`,
      donem: target.donem,
      donem_yillar: target.yillar,
      choices,
      yan_label: 'Yan Soru — Aynı padişahın diğer icraatı?',
      yan_cevap: yan,
      target_name: dogruOlay,
    };
  } else if (mode === 'yil-antlasma') {
    // İPUCU: yıl + ana madde. DOĞRU: antlaşma adı. 4 çeldirici: ±100 yıl
    const target = treaties[Math.floor(rand() * treaties.length)];
    const sameCentury = treaties.filter(t => t.isim !== target.isim && Math.abs((t.yil || 0) - (target.yil || 0)) < 100);
    let distractors = pickRandom(sameCentury, 4);
    if (distractors.length < 4) {
      const broader = treaties.filter(t => t.isim !== target.isim && !distractors.find(d => d.isim === t.isim));
      distractors = distractors.concat(pickRandom(broader, 4 - distractors.length));
    }

    const choices = shuffle([target, ...distractors]).map((t, i) => ({
      id: String.fromCharCode(65 + i),
      name: t.isim,
      isCorrect: t.isim === target.isim,
    }));

    // Yan sanayi: aynı yüzyıldan başka antlaşma
    const yan = sameCentury[0]?.isim || '—';

    hero = {
      mode: 'yil-antlasma',
      entityId: `yil-antlasma-${target.isim}-${target.yil}`,
      ipucu_label: `${target.yil} yılında imzalanan antlaşma hangisidir?`,
      ipucu: target.ana_madde || target.sonuc || '',
      donem: target.taraflar || '',
      donem_yillar: String(target.yil),
      choices,
      yan_label: 'Yan Soru — Aynı yüzyıldan başka antlaşma?',
      yan_cevap: yan,
      target_name: target.isim,
    };
  } else if (mode === 'antlasma-yil') {
    // İPUCU: antlaşma adı + maddesi. DOĞRU: yıl. 4 çeldirici: ±100 yıl
    const target = treaties[Math.floor(rand() * treaties.length)];
    const sameCentury = treaties.filter(t => t.yil !== target.yil && Math.abs((t.yil || 0) - (target.yil || 0)) < 100);
    let distractors = pickRandom(sameCentury, 4);
    if (distractors.length < 4) {
      const broader = treaties.filter(t => t.yil !== target.yil && !distractors.find(d => d.yil === t.yil));
      distractors = distractors.concat(pickRandom(broader, 4 - distractors.length));
    }
    // Yıl olarak şıklar
    const targetYil = String(target.yil);
    const choices = shuffle([
      { name: targetYil, isCorrect: true },
      ...distractors.map(t => ({ name: String(t.yil), isCorrect: false })),
    ]).map((c, i) => ({ ...c, id: String.fromCharCode(65 + i) }));

    hero = {
      mode: 'antlasma-yil',
      entityId: `antlasma-yil-${target.isim}`,
      ipucu_label: `${target.isim} antlaşması hangi yılda imzalanmıştır?`,
      ipucu: target.ana_madde || target.taraflar || '',
      donem: target.taraflar || '',
      donem_yillar: '',
      choices,
      yan_label: 'Yan Soru — Tarafları?',
      yan_cevap: target.taraflar || '—',
      target_name: targetYil,
    };
  } else if (mode === 'yil-savas') {
    // İPUCU: yıl + sebep. DOĞRU: savaş adı. 4 çeldirici: ±100 yıl
    const target = wars[Math.floor(rand() * wars.length)];
    const sameCentury = wars.filter(w => w.isim !== target.isim && Math.abs((w.yil || 0) - (target.yil || 0)) < 100);
    let distractors = pickRandom(sameCentury, 4);
    if (distractors.length < 4) {
      const broader = wars.filter(w => w.isim !== target.isim && !distractors.find(d => d.isim === w.isim));
      distractors = distractors.concat(pickRandom(broader, 4 - distractors.length));
    }

    const choices = shuffle([target, ...distractors]).map((w, i) => ({
      id: String.fromCharCode(65 + i),
      name: w.isim,
      isCorrect: w.isim === target.isim,
    }));

    hero = {
      mode: 'yil-savas',
      entityId: `yil-savas-${target.isim}-${target.yil}`,
      ipucu_label: `${target.yil} yılında gerçekleşen savaş/olay hangisidir?`,
      ipucu: target.sebep || target.taraflar || '',
      donem: target.taraflar || '',
      donem_yillar: String(target.yil),
      choices,
      yan_label: 'Yan Soru — Sonucu?',
      yan_cevap: target.sonuc || '—',
      target_name: target.isim,
    };
  }

  return hero;
}

export function markDailyAnswered(entityId, isCorrect) {
  const state = loadState();
  state.daily_hero = state.daily_hero || { seen: {} };
  const tk = todayKey();
  state.daily_hero.seen[tk] = {
    ...(state.daily_hero.seen[tk] || {}),
    entityId,
    answered: true,
    correct: isCorrect,
  };
  saveState(state);
}
