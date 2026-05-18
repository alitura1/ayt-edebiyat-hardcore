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

export async function authSignInGoogle() {
  const { auth, authMod } = await loadFirebase();
  const provider = new authMod.GoogleAuthProvider();
  // REV8 — signInWithRedirect: pop-up engelleme sorunu yok, daha güvenilir
  // Geri dönüşte getRedirectResult app.js DOMContentLoaded'da yakalanır
  await authMod.signInWithRedirect(auth, provider);
  // Bu satıra ulaşmaz; sayfa Google'a yönlendirilir
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

// Firestore helpers
export async function fsGetUserDoc(uid, sub = 'state') {
  const { db, fsMod } = await loadFirebase();
  const ref = fsMod.doc(db, 'users', uid, 'app', sub);
  const snap = await fsMod.getDoc(ref);
  return snap.exists() ? snap.data() : null;
}

export async function fsSetUserDoc(uid, sub, data) {
  const { db, fsMod } = await loadFirebase();
  const ref = fsMod.doc(db, 'users', uid, 'app', sub);
  await fsMod.setDoc(ref, { ...data, updated_at: fsMod.serverTimestamp() }, { merge: true });
}
