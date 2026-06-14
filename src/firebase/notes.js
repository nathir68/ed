import { isDemoMode } from './config';
import { demoNotes, demoStats } from './mockData';

export async function uploadNote(metadata) {
  if (isDemoMode) {
    return demoNotes.uploadNote(metadata);
  }

  const { db, storage } = await import('./config');
  const { collection, addDoc } = await import('firebase/firestore');
  const { ref, uploadBytes, getDownloadURL } = await import('firebase/storage');

  let fileUrl = '';
  if (metadata.file) {
    const storageRef = ref(storage, `notes/${Date.now()}_${metadata.file.name}`);
    await uploadBytes(storageRef, metadata.file);
    fileUrl = await getDownloadURL(storageRef);
  }

  const noteData = {
    title: metadata.title,
    subject: metadata.subject,
    description: metadata.description,
    fileUrl,
    fileName: metadata.file?.name || '',
    fileType: metadata.fileType,
    fileSize: metadata.file?.size || 0,
    tags: metadata.tags || [],
    teacherId: metadata.teacherId,
    teacherName: metadata.teacherName,
    targetClass: metadata.targetClass || 'all',
    downloads: 0,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  };

  const docRef = await addDoc(collection(db, 'notes'), noteData);
  return { id: docRef.id, ...noteData };
}

export async function getNotesByTeacher(teacherId) {
  if (isDemoMode) {
    return demoNotes.getNotesByTeacher(teacherId);
  }

  const { db } = await import('./config');
  const { collection, query, where, orderBy, getDocs } = await import('firebase/firestore');

  const q = query(
    collection(db, 'notes'),
    where('teacherId', '==', teacherId),
    orderBy('createdAt', 'desc')
  );
  const snapshot = await getDocs(q);
  return snapshot.docs.map((d) => ({ id: d.id, ...d.data() }));
}

export async function getAllNotes(filters = {}) {
  if (isDemoMode) {
    return demoNotes.getAllNotes(filters);
  }

  const { db } = await import('./config');
  const { collection, query, orderBy, getDocs } = await import('firebase/firestore');

  const q = query(collection(db, 'notes'), orderBy('createdAt', 'desc'));
  const snapshot = await getDocs(q);
  let results = snapshot.docs.map((d) => ({ id: d.id, ...d.data() }));

  if (filters.subject) results = results.filter((n) => n.subject === filters.subject);
  if (filters.fileType) results = results.filter((n) => n.fileType === filters.fileType);
  if (filters.search) {
    const s = filters.search.toLowerCase();
    results = results.filter(
      (n) =>
        n.title.toLowerCase().includes(s) ||
        n.subject.toLowerCase().includes(s) ||
        (n.tags || []).some((t) => t.toLowerCase().includes(s))
    );
  }
  return results;
}

export async function getNoteById(noteId) {
  if (isDemoMode) {
    return demoNotes.getNoteById(noteId);
  }

  const { db } = await import('./config');
  const { doc, getDoc } = await import('firebase/firestore');
  const docSnap = await getDoc(doc(db, 'notes', noteId));
  return docSnap.exists() ? { id: docSnap.id, ...docSnap.data() } : null;
}

export async function updateNote(noteId, updates) {
  if (isDemoMode) {
    return demoNotes.updateNote(noteId, updates);
  }

  const { db } = await import('./config');
  const { doc, updateDoc } = await import('firebase/firestore');
  await updateDoc(doc(db, 'notes', noteId), { ...updates, updatedAt: new Date().toISOString() });
}

export async function deleteNote(noteId) {
  if (isDemoMode) {
    return demoNotes.deleteNote(noteId);
  }

  const { db } = await import('./config');
  const { doc, deleteDoc } = await import('firebase/firestore');
  await deleteDoc(doc(db, 'notes', noteId));
}

export async function incrementDownload(noteId) {
  if (isDemoMode) {
    return demoNotes.incrementDownload(noteId);
  }

  const { db } = await import('./config');
  const { doc, updateDoc, increment } = await import('firebase/firestore');
  await updateDoc(doc(db, 'notes', noteId), { downloads: increment(1) });
}

export async function getTeacherStats(teacherId) {
  if (isDemoMode) {
    return demoStats.getTeacherStats(teacherId);
  }
  // Firebase implementation would aggregate from collections
  return demoStats.getTeacherStats(teacherId);
}

export async function getStudentStats() {
  if (isDemoMode) {
    return demoStats.getStudentStats();
  }
  return demoStats.getStudentStats();
}
