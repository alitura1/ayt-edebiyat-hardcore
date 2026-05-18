// REV5 — Yazar başına mastery seviyesi
// tanisilmadi: hiç kart gelmedi · tanidin: 1+ kart geldi · ogrendin: 80%+ acc + 60%+ cov + ≥3 çözüm
import { loadState } from './store.js';
import { altKonuToAuthorSlug, slugify } from './data.js';

export const LEVELS = {
  tanisilmadi: { emoji:'⚪', label:'Tanışmadın', cls:'opacity-50 grayscale',                                       rank: 0 },
  tanidin:     { emoji:'🟡', label:'Tanıdın',    cls:'',                                                            rank: 1 },
  ogrendin:    { emoji:'⭐', label:'Öğrendin',   cls:'ring-2 ring-ok-500 dark:ring-ok-500/70',                      rank: 2 },
};

// Yazara ait kartları cards havuzundan ayıklar
export function cardsForAuthor(authorName, allCards) {
  const target = slugify(authorName);
  return allCards.filter(c => altKonuToAuthorSlug(c.alt_konu) === target);
}

export function authorMastery(authorName, allCards, state) {
  const s = state || loadState();
  const cards = cardsForAuthor(authorName, allCards);
  if (cards.length === 0) return 'tanisilmadi';

  const seen = cards.filter(c => (s.progress[c.id]?.cozuldu || 0) > 0);
  if (seen.length === 0) return 'tanisilmadi';

  let totalCozuldu = 0, totalDogru = 0;
  for (const c of seen) {
    const p = s.progress[c.id];
    totalCozuldu += p.cozuldu;
    totalDogru   += p.dogru;
  }
  const acc = totalCozuldu > 0 ? totalDogru / totalCozuldu : 0;
  const coverage = seen.length / cards.length;

  if (acc >= 0.80 && coverage >= 0.60 && totalCozuldu >= 3) return 'ogrendin';
  return 'tanidin';
}

// Tüm yazarların özet sayımı
export function masterySummary(authors, allCards, state) {
  const s = state || loadState();
  const counts = { tanisilmadi: 0, tanidin: 0, ogrendin: 0 };
  const byAuthor = {};
  for (const a of authors) {
    const lvl = authorMastery(a.name, allCards, s);
    counts[lvl]++;
    byAuthor[slugify(a.name)] = lvl;
  }
  return { counts, byAuthor, total: authors.length };
}
