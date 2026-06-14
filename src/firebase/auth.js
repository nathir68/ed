import { isDemoMode } from './config';
import { demoAuth } from './mockData';

// Firebase imports (only used when not in demo mode)
let createUserWithEmailAndPassword, signInWithEmailAndPassword, signOut, sendPasswordResetEmail, onAuthStateChanged, firebaseAuth;

if (!isDemoMode) {
  import('firebase/auth').then((mod) => {
    createUserWithEmailAndPassword = mod.createUserWithEmailAndPassword;
    signInWithEmailAndPassword = mod.signInWithEmailAndPassword;
    signOut = mod.signOut;
    sendPasswordResetEmail = mod.sendPasswordResetEmail;
    onAuthStateChanged = mod.onAuthStateChanged;
  });
  import('./config').then((mod) => {
    firebaseAuth = mod.auth;
  });
}

export async function signUpUser(email, password, profileData) {
  if (isDemoMode) {
    return demoAuth.signUp(email, password, profileData);
  }

  const { auth, db } = await import('./config');
  const { createUserWithEmailAndPassword } = await import('firebase/auth');
  const { doc, setDoc } = await import('firebase/firestore');

  const credential = await createUserWithEmailAndPassword(auth, email, password);
  const uid = credential.user.uid;

  const userData = {
    uid,
    email,
    ...profileData,
    createdAt: new Date().toISOString(),
  };

  await setDoc(doc(db, 'users', uid), userData);
  return userData;
}

export async function loginUser(email, password) {
  if (isDemoMode) {
    return demoAuth.login(email, password);
  }

  const { auth } = await import('./config');
  const { signInWithEmailAndPassword } = await import('firebase/auth');
  const { doc, getDoc } = await import('firebase/firestore');
  const { db } = await import('./config');

  const credential = await signInWithEmailAndPassword(auth, email, password);
  const uid = credential.user.uid;

  const userDoc = await getDoc(doc(db, 'users', uid));
  if (!userDoc.exists()) throw new Error('User profile not found');

  return userDoc.data();
}

export async function logoutUser() {
  if (isDemoMode) {
    return demoAuth.logout();
  }

  const { auth } = await import('./config');
  const { signOut } = await import('firebase/auth');
  await signOut(auth);
}

export async function resetPassword(email) {
  if (isDemoMode) {
    return demoAuth.resetPassword(email);
  }

  const { auth } = await import('./config');
  const { sendPasswordResetEmail } = await import('firebase/auth');
  await sendPasswordResetEmail(auth, email);
}

export async function getUserProfile(uid) {
  if (isDemoMode) {
    return demoAuth.getUserProfile(uid);
  }

  const { db } = await import('./config');
  const { doc, getDoc } = await import('firebase/firestore');
  const userDoc = await getDoc(doc(db, 'users', uid));
  return userDoc.exists() ? userDoc.data() : null;
}

export function getStoredUser() {
  if (isDemoMode) {
    return demoAuth.getStoredUser();
  }
  return null;
}
