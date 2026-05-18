// REV8 — "Şu Anki Yazar" tahmin oyunu
// Yazar adı gizli, ipuçlarıyla 5 şıktan tahmin. Çeldirici: aynı dönem+pozisyon yazarlar.
import { slugify } from './data.js';
import { loadState, saveState } from './store.js';

// REV9 — yazara ait eser tahmin sorusu üretir
// Doğru eser: yazarın works.json'daki eserlerinden 1 random
// 4 çeldirici: aynı dönemden başka yazarların eserleri
export function buildEserSoru(author, works) {
  if (!author || !Array.isArray(works) || works.length === 0) return null;
  const yazarAdi = author.name;
  const authorWorks = works.filter(w => w.yazar === yazarAdi);
  if (authorWorks.length === 0) return null;  // bu yazara aşama C yok

  const dogruEser = authorWorks[Math.floor(Math.random() * authorWorks.length)];
  const otherWorks = works.filter(w => w.yazar !== yazarAdi);
  // Aynı dönem + tercihen benzer tür çeldirici
  const sameDonem = otherWorks.filter(w => w.donem === author.donem);
  const pool = sameDonem.length >= 8 ? sameDonem : otherWorks;
  // Doğru cevabı eşleştiren title olmasın (aynı eser farklı yazarda olabilir, edge case)
  const cleanPool = pool.filter(w => w.title !== dogruEser.title);
  const shuffled = [...cleanPool].sort(() => Math.random() - 0.5);
  const distractors = shuffled.slice(0, 4);
  if (distractors.length < 4) return null;
  // 5 şık karıştır
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
  if (basePool.length === 0) return { author: null, distractors: [], eserSoru: null };

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

  // Eser tahmin sorusu (works.json varsa)
  const eserSoru = buildEserSoru(author, works);

  return { author, distractors, eserSoru };
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
