import { isDemoMode } from './config';
import { demoClasses } from './mockData';

export function generateJitsiLink(subject) {
  const slug = subject.toLowerCase().replace(/\s+/g, '-');
  const id = Math.random().toString(36).substring(2, 8);
  return `https://meet.jit.si/educonnect-${slug}-${id}`;
}

export async function createClass(classData) {
  if (isDemoMode) {
    return demoClasses.createClass(classData);
  }

  const { db } = await import('./config');
  const { collection, addDoc } = await import('firebase/firestore');

  const docRef = await addDoc(collection(db, 'classes'), {
    ...classData,
    status: 'upcoming',
    createdAt: new Date().toISOString(),
  });
  return { id: docRef.id, ...classData, status: 'upcoming' };
}

export async function getClassesByTeacher(teacherId) {
  if (isDemoMode) {
    return demoClasses.getClassesByTeacher(teacherId);
  }

  const { db } = await import('./config');
  const { collection, query, where, orderBy, getDocs } = await import('firebase/firestore');

  const q = query(
    collection(db, 'classes'),
    where('teacherId', '==', teacherId),
    orderBy('date', 'desc')
  );
  const snapshot = await getDocs(q);
  return snapshot.docs.map((d) => ({ id: d.id, ...d.data() }));
}

export async function getUpcomingClasses() {
  if (isDemoMode) {
    return demoClasses.getUpcomingClasses();
  }

  const { db } = await import('./config');
  const { collection, query, where, orderBy, getDocs } = await import('firebase/firestore');

  const q = query(
    collection(db, 'classes'),
    where('status', '==', 'upcoming'),
    orderBy('date', 'asc')
  );
  const snapshot = await getDocs(q);
  return snapshot.docs.map((d) => ({ id: d.id, ...d.data() }));
}

export async function getAllClasses() {
  if (isDemoMode) {
    return demoClasses.getAllClasses();
  }

  const { db } = await import('./config');
  const { collection, query, orderBy, getDocs } = await import('firebase/firestore');

  const q = query(collection(db, 'classes'), orderBy('date', 'desc'));
  const snapshot = await getDocs(q);
  return snapshot.docs.map((d) => ({ id: d.id, ...d.data() }));
}

export async function getClassById(classId) {
  if (isDemoMode) {
    return demoClasses.getClassById(classId);
  }

  const { db } = await import('./config');
  const { doc, getDoc } = await import('firebase/firestore');
  const docSnap = await getDoc(doc(db, 'classes', classId));
  return docSnap.exists() ? { id: docSnap.id, ...docSnap.data() } : null;
}

export async function updateClass(classId, updates) {
  if (isDemoMode) {
    return demoClasses.updateClass(classId, updates);
  }

  const { db } = await import('./config');
  const { doc, updateDoc } = await import('firebase/firestore');
  await updateDoc(doc(db, 'classes', classId), updates);
}

export async function deleteClass(classId) {
  if (isDemoMode) {
    return demoClasses.deleteClass(classId);
  }

  const { db } = await import('./config');
  const { doc, deleteDoc } = await import('firebase/firestore');
  await deleteDoc(doc(db, 'classes', classId));
}
