// REV10 — "Şu Anki Yazar" — yazar görünür tanıtım + eser tahmin sorusu
import { slugify } from './data.js';
import { loadState, saveState } from './store.js';

// Yazara ait eser tahmin sorusu üretir
// Doğru eser: yazarın works.json'daki eserlerinden 1 random
// 4 çeldirici: aynı dönemden başka yazarların eserleri
export function buildEserSoru(author, works) {
  if (!author || !Array.isArray(works) || works.length === 0) return null;
  const yazarAdi = author.name;
  const authorWorks = works.filter(w => w.yazar === yazarAdi);
  if (authorWorks.length === 0) return null;

  const dogruEser = authorWorks[Math.floor(Math.random() * authorWorks.length)];
  const otherWorks = works.filter(w => w.yazar !== yazarAdi);
  const sameDonem = otherWorks.filter(w => w.donem === author.donem);
  const pool = sameDonem.length >= 8 ? sameDonem : otherWorks;
  const cleanPool = pool.filter(w => w.title !== dogruEser.title);
  const shuffled = [...cleanPool].sort(() => Math.random() - 0.5);
  const distractors = shuffled.slice(0, 4);
  if (distractors.length < 4) return null;
  const all = [dogruEser, ...distractors].sort(() => Math.random() - 0.5).map((w, i) => ({
    id: String.fromCharCode(65 + i),
    title: w.title,
    isCorrect: w === dogruEser,
  }));
  return { dogruEser, distractors, choices: all };
}

export function dailyHero(authors, works = []) {
  // Pool — anekdotu olan + soru_sayisi >= 1
  const enriched = authors.filter(a => a.anekdot && a.soru_sayisi >= 1);
  const basePool = enriched.length ? enriched : authors.filter(a => a.soru_sayisi >= 1);
  if (basePool.length === 0) return { author: null, eserSoru: null };

  // History — son 20 yazarı tekrar etmemek için
  const s = loadState();
  if (!s.daily_hero) s.daily_hero = { seen: {}, history: [] };
  if (!Array.isArray(s.daily_hero.history)) s.daily_hero.history = [];
  const recent = new Set(s.daily_hero.history.slice(-20));
  const fresh = basePool.filter(a => !recent.has(slugify(a.name)));
  const pool = fresh.length ? fresh : basePool;

  const author = pool[Math.floor(Math.random() * pool.length)];

  // History'ye ekle
  s.daily_hero.history.push(slugify(author.name));
  while (s.daily_hero.history.length > 40) s.daily_hero.history.shift();
  saveState(s);

  // REV10 — yazar tahmin distractors kaldırıldı; sadece eser sorusu
  const eserSoru = buildEserSoru(author, works);

  return { author, eserSoru };
}

// Geçmişi temizle (settings'den çağrılabilir)
export function resetHeroHistory() {
  const s = loadState();
  if (!s.daily_hero) s.daily_hero = { seen: {}, history: [] };
  s.daily_hero.history = [];
  saveState(s);
}
