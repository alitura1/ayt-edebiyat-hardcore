// REV5 — Günün Kahramanı: tarih-seeded deterministic yazar seçimi
import { altKonuToAuthorSlug, slugify } from './data.js';
import { localDateStr } from './streak.js';

// FNV-1a deterministic hash
function hashStr(s) {
  let h = 2166136261 >>> 0;
  for (let i = 0; i < s.length; i++) {
    h ^= s.charCodeAt(i);
    h = (h * 16777619) >>> 0;
  }
  return h >>> 0;
}

export function todayKey() { return localDateStr(); }

// Anekdotu olan + soru_sayisi >= 1 olan yazarlardan, tarih bazlı seç
// Eğer anekdotlu yazar yoksa fallback: en çok sorulan yazar
export function dailyHero(authors, cards, dateKey = null) {
  const key = dateKey || todayKey();
  const enriched = authors.filter(a => a.anekdot && a.soru_sayisi >= 1);
  const pool = enriched.length ? enriched : authors.filter(a => a.soru_sayisi >= 1);
  if (pool.length === 0) return { author: null, miniCard: null };

  const idx = hashStr(key) % pool.length;
  const author = pool[idx];

  // O yazara ait bir kart deterministic seç
  const slug = slugify(author.name);
  const aCards = cards.filter(c => altKonuToAuthorSlug(c.alt_konu) === slug);
  let miniCard = null;
  if (aCards.length) {
    const cIdx = hashStr(key + ':card') % aCards.length;
    miniCard = aCards[cIdx];
  }
  return { author, miniCard, key };
}
