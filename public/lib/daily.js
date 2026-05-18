// REV11 — Karışık Mod: Mod A (yazar→eser) veya Mod B (eser→yazar) random
import { slugify } from './data.js';
import { loadState, saveState } from './store.js';

// Yazarın adını metinde *** ile maskele (Mod B'de eser tanıtımı için)
function escapeRegex(s) {
  return s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}
export function maskAuthorName(text, fullName) {
  if (!text || !fullName) return text || '';
  let masked = text;
  masked = masked.replace(new RegExp(escapeRegex(fullName), 'gi'), '***');
  for (const token of fullName.split(/\s+/)) {
    if (token.length < 3) continue;
    masked = masked.replace(new RegExp('\\b' + escapeRegex(token) + '\\b', 'gi'), '***');
  }
  return masked;
}

// Mod B: Yazarın bir eseri + 4 çeldirici yazar (aynı dönemden)
export function buildYazarSoru(author, authors, works) {
  if (!author || !Array.isArray(works) || works.length === 0) return null;
  const authorWorks = works.filter(w => w.yazar === author.name);
  if (authorWorks.length === 0) return null;

  const targetEser = authorWorks[Math.floor(Math.random() * authorWorks.length)];
  const otherAuthors = authors.filter(a => a.name !== author.name);
  const sameDonem = otherAuthors.filter(a => a.donem === author.donem);
  const pool = sameDonem.length >= 4 ? sameDonem : otherAuthors;
  const shuffled = [...pool].sort(() => Math.random() - 0.5);
  const distractorAuthors = shuffled.slice(0, 4);
  if (distractorAuthors.length < 4) return null;

  const all = [author, ...distractorAuthors].sort(() => Math.random() - 0.5).map((a, i) => ({
    id: String.fromCharCode(65 + i),
    name: a.name,
    isCorrect: a.name === author.name,
  }));
  return { targetEser, distractorAuthors, choices: all };
}

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
  if (basePool.length === 0) return { mode: 'none', author: null, eserSoru: null, yazarSoru: null };

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

  // REV11 — Karışık mod: %50 eser, %50 yazar
  const preferred = Math.random() < 0.5 ? 'eser' : 'yazar';
  let eserSoru = null, yazarSoru = null;
  if (preferred === 'eser') {
    eserSoru = buildEserSoru(author, works);
    if (!eserSoru) yazarSoru = buildYazarSoru(author, authors, works);
  } else {
    yazarSoru = buildYazarSoru(author, authors, works);
    if (!yazarSoru) eserSoru = buildEserSoru(author, works);
  }
  const mode = eserSoru ? 'eser' : (yazarSoru ? 'yazar' : 'none');

  return { mode, author, eserSoru, yazarSoru };
}

// Geçmişi temizle (settings'den çağrılabilir)
export function resetHeroHistory() {
  const s = loadState();
  if (!s.daily_hero) s.daily_hero = { seen: {}, history: [] };
  s.daily_hero.history = [];
  saveState(s);
}
