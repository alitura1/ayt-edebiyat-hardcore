// REV6 — Firebase ESM dinamik yükleme + auth + firestore singleton
import { FIREBASE_CONFIG, FIREBASE_CDN } from './firebase-config.js';

let _app = null;
let _auth = null;
let _db = null;
let _loadPromise = null;

async function loadFirebase() {
  if (_loadPromise) return _loadPromise;
  _loadPromise = (async () => {
    const [{ initializeApp }, authMod, fsMod] = await Promise.all([
      import(`${FIREBASE_CDN}/firebase-app.js`),
      import(`${FIREBASE_CDN}/firebase-auth.js`),
      import(`${FIREBASE_CDN}/firebase-firestore.js`),
    ]);
    _app = initializeApp(FIREBASE_CONFIG);
    _auth = authMod.getAuth(_app);
    _db = fsMod.getFirestore(_app);
    // Offline persistence (sessionStorage fallback)
    try {
      await fsMod.enableIndexedDbPersistence(_db, { synchronizeTabs: true });
    } catch(e) {
      console.warn('Firestore persistence skip:', e.code);
    }
    return { app: _app, auth: _auth, db: _db, authMod, fsMod };
  })();
  return _loadPromise;
}

export async function getFirebase() {
  return loadFirebase();
}

// Convenience: Auth helpers (email/password + Google)
export async function authSignUpEmail(email, password) {
  const { auth, authMod } = await loadFirebase();
  const cred = await authMod.createUserWithEmailAndPassword(auth, email, password);
  return cred.user;
}

export async function authSignInEmail(email, password) {
  const { auth, authMod } = await loadFirebase();
  const cred = await authMod.signInWithEmailAndPassword(auth, email, password);
  return cred.user;
}

// REV12 — Google login YENİ PENCERE + BroadcastChannel hile
// Ana sekme aynı kalır, login ayrı pencerede tamamlanır
export async function authSignInGoogle() {
  return new Promise((resolve, reject) => {
    if (!('BroadcastChannel' in window)) {
      reject(new Error('Tarayıcı BroadcastChannel desteklemiyor (eski Safari?). E-mail/şifre kullan.'));
      return;
    }
    const channel = new BroadcastChannel('auth');
    let resolved = false;
    const timeoutId = setTimeout(() => {
      if (!resolved) {
        channel.close();
        reject(new Error('Giriş zaman aşımı (60sn). Tekrar dene.'));
      }
    }, 60000);

    channel.onmessage = async (event) => {
      const d = event.data;
      if (!d || !d.type) return;
      resolved = true;
      clearTimeout(timeoutId);
      channel.close();
      if (d.type === 'auth-success') {
        // Ana sekmede Firebase auth state otomatik geldi mi? Persistence sayesinde evet.
        // Yine de force re-init: getFirebase + onAuthStateChanged tetiklenir
        try {
          const { auth, authMod } = await loadFirebase();
          // Auth.currentUser hemen set olmayabilir — kısa bekleme
          await new Promise(r => setTimeout(r, 400));
          if (!auth.currentUser) {
            // Auth state sync'i için sayfayı yenile (cleanest)
            location.reload();
            return;
          }
          resolve(auth.currentUser);
        } catch (e) {
          // Hata olursa yenile, auth state otomatik gelsin
          location.reload();
        }
      } else if (d.type === 'auth-error') {
        reject(new Error(d.message || 'Google girişi başarısız'));
      }
    };

    // Popup penceresi (toolbar yok, fixed boyut → popup-like davranır)
    const w = window.open(
      './auth-popup.html',
      'gauth',
      'width=520,height=680,toolbar=no,location=no,menubar=no'
    );
    if (!w) {
      clearTimeout(timeoutId);
      channel.close();
      reject(new Error('Pop-up engellendi. Tarayıcı adres çubuğundaki pop-up ikonuna tıklayıp izin ver.'));
    } else {
      w.focus();
    }
  });
}

export async function authSignOut() {
  const { auth, authMod } = await loadFirebase();
  await authMod.signOut(auth);
}

export async function authCurrentUser() {
  const { auth } = await loadFirebase();
  return auth.currentUser;
}

export async function onAuthChange(cb) {
  const { auth, authMod } = await loadFirebase();
  return authMod.onAuthStateChanged(auth, cb);
}

// Firestore helpers — REV20 subject-aware
// Yeni path: users/{uid}/subjects/{subject}  (4 segment, doc)
// Legacy path: users/{uid}/app/state  (4 segment, doc) — geriye dönük okuma için

export async function fsGetUserDoc(uid, subject = 'edebiyat') {
  const { db, fsMod } = await loadFirebase();
  const ref = fsMod.doc(db, 'users', uid, 'subjects', subject);
  const snap = await fsMod.getDoc(ref);
  return snap.exists() ? snap.data() : null;
}

export async function fsSetUserDoc(uid, subject, data) {
  const { db, fsMod } = await loadFirebase();
  const ref = fsMod.doc(db, 'users', uid, 'subjects', subject);
  await fsMod.setDoc(ref, { ...data, updated_at: fsMod.serverTimestamp() }, { merge: true });
}

// Legacy okuma — eski users/{uid}/app/state path'inden veri çekmek için
export async function fsGetLegacyUserDoc(uid) {
  const { db, fsMod } = await loadFirebase();
  const ref = fsMod.doc(db, 'users', uid, 'app', 'state');
  const snap = await fsMod.getDoc(ref);
  return snap.exists() ? snap.data() : null;
}
