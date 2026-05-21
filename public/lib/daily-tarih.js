// REV20 — Tarih için günlük rastgele tahmin oyunu
// Mod A: padişah → dönem | Mod B: antlaşma → yıl | Mod C: kişi → tipik açı
// Edebiyat'taki dailyHero gibi tarih-spesifik

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

// Seed'li (deterministic per day) random
function dayRandom(seed) {
  let s = 0;
  for (const ch of seed) s = (s * 31 + ch.charCodeAt(0)) >>> 0;
  return () => {
    s = (s * 1103515245 + 12345) >>> 0;
    return (s / 0xffffffff);
  };
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
  const modes = [];
  if (people && people.length >= 5) modes.push('kisi');
  if (treaties && treaties.length >= 5) modes.push('antlasma');
  if (events && events.length >= 5) modes.push('olay');
  if (modes.length === 0) return null;

  const mode = modes[Math.floor(rand() * modes.length)];

  let hero = null;

  if (mode === 'kisi') {
    // İlginç kişileri (anekdotu veya bilgisi olan) tercih et
    const interesting = people.filter(p => p.anekdot && p.anekdot.length > 20);
    if (!interesting.length) return null;
    const target = interesting[Math.floor(rand() * interesting.length)];
    const others = pickRandom(people.filter(p => p.name !== target.name && p.anekdot && p.anekdot.length > 15), 4);
    const choices = shuffle([target, ...others]).map((p, i) => ({
      id: String.fromCharCode(65 + i),
      name: p.name,
      isCorrect: p.name === target.name,
    }));
    hero = {
      mode: 'kisi',
      entityId: target.name,
      target,
      anekdot: target.anekdot,
      choices,
      donem: target.donem,
    };
  } else if (mode === 'antlasma') {
    const target = treaties[Math.floor(rand() * treaties.length)];
    const others = pickRandom(treaties.filter(t => t.yil !== target.yil), 4);
    const choices = shuffle([target, ...others]).map((t, i) => ({
      id: String.fromCharCode(65 + i),
      name: t.isim,
      yil: t.yil,
      isCorrect: t.yil === target.yil && t.isim === target.isim,
    }));
    hero = {
      mode: 'antlasma',
      entityId: target.isim + '-' + target.yil,
      target,
      ipucu: target.ana_madde,
      sonuc: target.sonuc,
      choices,
    };
  } else if (mode === 'olay') {
    const wars = events.filter(e => e.tur === 'savas');
    if (wars.length < 5) return null;
    const target = wars[Math.floor(rand() * wars.length)];
    const others = pickRandom(wars.filter(w => w.isim !== target.isim), 4);
    const choices = shuffle([target, ...others]).map((w, i) => ({
      id: String.fromCharCode(65 + i),
      name: w.isim,
      yil: w.yil,
      isCorrect: w.isim === target.isim,
    }));
    hero = {
      mode: 'olay',
      entityId: target.isim + '-' + target.yil,
      target,
      sebep: target.sebep,
      sonuc: target.sonuc,
      choices,
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
