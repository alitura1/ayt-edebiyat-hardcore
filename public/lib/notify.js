// REV6 M10 — Web Notification + ileride SW push
// Sade strateji: kullanıcı izin verir, ayarlardaki saatler için browser local reminder
import { loadState, saveState } from './store.js';
import { streakInfo } from './streak.js';

export function notifyPermissionStatus() {
  if (!('Notification' in window)) return 'unsupported';
  return Notification.permission; // "granted" | "denied" | "default"
}

export async function requestNotifyPermission() {
  if (!('Notification' in window)) return 'unsupported';
  const p = await Notification.requestPermission();
  return p;
}

export function showLocalNotification(title, options = {}) {
  if (Notification.permission !== 'granted') return null;
  return new Notification(title, {
    icon: '/assets/icon-192.svg',
    badge: '/assets/icon-192.svg',
    ...options,
  });
}

// Ayarlardaki saatler için (örn 18:00 ve 21:00) kontrol — tab açıkken
// her dakika check, saat eşleşirse + bugün gösterilmediyse bildirim at
let _lastCheckedDay = null;
let _shownToday = new Set();

export function startNotifyScheduler() {
  if (typeof window === 'undefined') return;
  // Permission kontrolü her tick'te yapılır
  setInterval(checkAndNotify, 60 * 1000);  // dakikada 1
  // İlk açılışta da bir kontrol
  setTimeout(checkAndNotify, 5000);
}

function checkAndNotify() {
  try {
    if (Notification.permission !== 'granted') return;
    const s = loadState();
    const notify = s.notify;
    if (!notify || !notify.enabled || !Array.isArray(notify.hours)) return;

    const now = new Date();
    const today = `${now.getFullYear()}-${now.getMonth()}-${now.getDate()}`;
    if (today !== _lastCheckedDay) {
      _shownToday = new Set();
      _lastCheckedDay = today;
    }

    const hour = now.getHours();
    const minute = now.getMinutes();

    for (const target of notify.hours) {
      if (hour === target && minute < 5 && !_shownToday.has(target)) {
        _shownToday.add(target);
        showSmartReminder(target);
      }
    }
  } catch(e) { /* sessizce */ }
}

function showSmartReminder(targetHour) {
  const sk = streakInfo();
  const s = loadState();
  const todaySolved = Object.values(s.progress || {}).filter(p => {
    const last = new Date(p.son || 0);
    const now = new Date();
    return last.getFullYear() === now.getFullYear() && last.getMonth() === now.getMonth() && last.getDate() === now.getDate();
  }).length;

  let title, body;
  if (sk.status === 'at_risk' && todaySolved === 0) {
    title = '🔥 Streak\'in tehlikede!';
    body = `${sk.current} günlük serini bugün kaybedebilirsin. Hızlı Atış'a bas!`;
  } else if (todaySolved === 0) {
    title = '⚡ Bugün henüz 0 soru çözdün';
    body = 'Sadece 1 kart yeter. Şu Anki Yazara göz at.';
  } else if (todaySolved < 5) {
    title = '🎯 Devam et!';
    body = `Bugün ${todaySolved} soru çözdün. Hedef 10 olsun?`;
  } else {
    return; // bugün yeterince çözüldü
  }

  showLocalNotification(title, { body, tag: 'daily-reminder' });
}
