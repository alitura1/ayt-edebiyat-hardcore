// REV8 — "Şu Anki Yazar" tahmin oyunu
// Yazar adı gizli, ipuçlarıyla 5 şıktan tahmin. Çeldirici: aynı dönem+pozisyon yazarlar.
import { slugify } from './data.js';
import { loadState, saveState } from './store.js';

export function dailyHero(authors) {
  // Pool — anekdotu olan + soru_sayisi >= 1
  const enriched = authors.filter(a => a.anekdot && a.soru_sayisi >= 1);
  const basePool = enriched.length ? enriched : authors.filter(a => a.soru_sayisi >= 1);
  if (basePool.length === 0) return { author: null, distractors: [] };

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

  // Çeldiriciler — aynı dönem+pozisyon > aynı dönem > tüm
  const all = authors.filter(a => a.name !== author.name);
  const samePosDonem = all.filter(a => a.donem === author.donem && a.pozisyon === author.pozisyon);
  const sameDonem = all.filter(a => a.donem === author.donem);
  let pool2;
  if (samePosDonem.length >= 4) pool2 = samePosDonem;
  else if (sameDonem.length >= 4) pool2 = sameDonem;
  else pool2 = all;
  const shuffled = [...pool2].sort(() => Math.random() - 0.5);
  const distractors = shuffled.slice(0, 4);

  return { author, distractors };
}

// Geçmişi temizle (settings'den çağrılabilir)
export function resetHeroHistory() {
  const s = loadState();
  if (!s.daily_hero) s.daily_hero = { seen: {}, history: [] };
  s.daily_hero.history = [];
  saveState(s);
}

// Yardımcı: yazarın adını metinde *** ile maskele
function escapeRegex(s) {
  return s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}
export function maskAuthorName(text, fullName) {
  if (!text || !fullName) return text || '';
  let masked = text;
  // Tam ad eşleşmesi
  masked = masked.replace(new RegExp(escapeRegex(fullName), 'gi'), '***');
  // Token bazlı (3+ harf)
  for (const token of fullName.split(/\s+/)) {
    if (token.length < 3) continue;
    masked = masked.replace(new RegExp('\\b' + escapeRegex(token) + '\\b', 'gi'), '***');
  }
  return masked;
}
