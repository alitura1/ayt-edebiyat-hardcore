// REV5 — Günlük streak (login + soru cevaplama)
// Kullanıcı her gün siteye girip min 1 soru cevaplarsa streak +1
// Kopukluk olursa sıfırlanır
import { loadState, saveState } from './store.js';

export function localDateStr(d = new Date()) {
  return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`;
}

function daysBetween(aStr, bStr) {
  const a = new Date(aStr + 'T00:00:00');
  const b = new Date(bStr + 'T00:00:00');
  return Math.round((b - a) / 86400000);
}

// Bir soru cevaplandığında çağrılır — günlük streak'i ilerletir
export function tickStreak() {
  const s = loadState();
  if (!s.streak) s.streak = { current: 0, longest: 0, last_active_date: null, history: [] };
  const today = localDateStr();
  const last = s.streak.last_active_date;
  let bumped = false;

  if (last === today) {
    // bugün zaten tick edildi
  } else if (!last) {
    s.streak.current = 1;
    bumped = true;
  } else {
    const diff = daysBetween(last, today);
    if (diff === 1) { s.streak.current += 1; bumped = true; }
    else if (diff > 1) { s.streak.current = 1; bumped = true; }
    else { /* clock cinliği — dokunma */ }
  }

  if (bumped) {
    s.streak.last_active_date = today;
    s.streak.longest = Math.max(s.streak.longest || 0, s.streak.current);
    if (!Array.isArray(s.streak.history)) s.streak.history = [];
    if (!s.streak.history.includes(today)) {
      s.streak.history.push(today);
      while (s.streak.history.length > 60) s.streak.history.shift();
    }
    saveState(s);
  }
  return { ...s.streak, bumped };
}

// Sayfa açıldığında — kullanıcı bugün gelmemişse uyarı için
export function streakInfo() {
  const s = loadState();
  const sk = s.streak || { current: 0, longest: 0, last_active_date: null, history: [] };
  const today = localDateStr();
  const last = sk.last_active_date;
  if (!last) return { ...sk, status: 'never' };
  const diff = daysBetween(last, today);
  if (diff === 0) return { ...sk, status: 'active_today' };
  if (diff === 1) return { ...sk, status: 'at_risk' };       // dün geldi, bugün henüz değil
  return { ...sk, status: 'broken', would_lose: sk.current };
}

export const STREAK_BADGES = [
  { d: 3,  emoji:'🔥', label:'3 gün' },
  { d: 7,  emoji:'⚡', label:'1 hafta' },
  { d: 14, emoji:'💎', label:'2 hafta' },
  { d: 30, emoji:'👑', label:'1 ay' },
];

export function currentBadge(current) {
  let last = null;
  for (const b of STREAK_BADGES) {
    if (current >= b.d) last = b; else break;
  }
  return last;
}

export function nextBadge(current) {
  for (const b of STREAK_BADGES) {
    if (current < b.d) return b;
  }
  return null;
}
