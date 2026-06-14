/* Demo/Mock data layer — used when VITE_DEMO_MODE=true */

const delay = (ms) => new Promise((r) => setTimeout(r, ms));

// ─── In-memory stores ────────────────────────────────────────
let users = {
  'teacher-1': {
    uid: 'teacher-1',
    fullName: 'Mrs. Priya Sharma',
    email: 'priya@school.edu',
    role: 'teacher',
    subject: 'Mathematics',
    institution: 'Delhi Public School',
    employeeId: 'EMP001',
    classGrade: null,
    rollNumber: null,
    createdAt: new Date('2026-01-15').toISOString(),
  },
  'teacher-2': {
    uid: 'teacher-2',
    fullName: 'Mr. Rajesh Kumar',
    email: 'rajesh@school.edu',
    role: 'teacher',
    subject: 'Physics',
    institution: 'Delhi Public School',
    employeeId: 'EMP002',
    classGrade: null,
    rollNumber: null,
    createdAt: new Date('2026-02-01').toISOString(),
  },
  'student-1': {
    uid: 'student-1',
    fullName: 'Arjun Patel',
    email: 'arjun@student.edu',
    role: 'student',
    subject: null,
    institution: 'Delhi Public School',
    employeeId: null,
    classGrade: '10th',
    rollNumber: 'STU2026001',
    createdAt: new Date('2026-03-01').toISOString(),
  },
  'student-2': {
    uid: 'student-2',
    fullName: 'Sneha Reddy',
    email: 'sneha@student.edu',
    role: 'student',
    subject: null,
    institution: 'Delhi Public School',
    employeeId: null,
    classGrade: '10th',
    rollNumber: 'STU2026002',
    createdAt: new Date('2026-03-05').toISOString(),
  },
};

let notes = [
  {
    id: 'note-1',
    title: 'Trigonometry — Chapter 3',
    subject: 'Mathematics',
    description: 'Complete notes covering sine, cosine, tangent identities and their applications in problem solving. Includes practice problems and worked examples.',
    fileUrl: '#',
    fileName: 'trig_chapter3.pdf',
    fileType: 'pdf',
    fileSize: 2048000,
    tags: ['trigonometry', 'chapter3', 'identities'],
    teacherId: 'teacher-1',
    teacherName: 'Mrs. Priya Sharma',
    targetClass: 'all',
    downloads: 42,
    createdAt: new Date('2026-06-01').toISOString(),
    updatedAt: new Date('2026-06-01').toISOString(),
  },
  {
    id: 'note-2',
    title: 'Quadratic Equations',
    subject: 'Mathematics',
    description: 'Detailed explanation of quadratic equations, discriminant analysis, roots, and graphical representation.',
    fileUrl: '#',
    fileName: 'quadratic_equations.pdf',
    fileType: 'pdf',
    fileSize: 1536000,
    tags: ['algebra', 'quadratic', 'equations'],
    teacherId: 'teacher-1',
    teacherName: 'Mrs. Priya Sharma',
    targetClass: '10th',
    downloads: 28,
    createdAt: new Date('2026-05-28').toISOString(),
    updatedAt: new Date('2026-05-28').toISOString(),
  },
  {
    id: 'note-3',
    title: 'Newton\'s Laws of Motion',
    subject: 'Physics',
    description: 'Comprehensive notes on all three laws of motion with real-world examples, diagrams, and numerical problems.',
    fileUrl: '#',
    fileName: 'newtons_laws.pptx',
    fileType: 'ppt',
    fileSize: 4096000,
    tags: ['physics', 'mechanics', 'newton'],
    teacherId: 'teacher-2',
    teacherName: 'Mr. Rajesh Kumar',
    targetClass: 'all',
    downloads: 65,
    createdAt: new Date('2026-06-03').toISOString(),
    updatedAt: new Date('2026-06-03').toISOString(),
  },
  {
    id: 'note-4',
    title: 'Probability & Statistics Basics',
    subject: 'Mathematics',
    description: 'Introduction to probability theory, permutations, combinations, and basic statistical measures.',
    fileUrl: '#',
    fileName: 'probability_stats.docx',
    fileType: 'doc',
    fileSize: 1024000,
    tags: ['probability', 'statistics', 'combinatorics'],
    teacherId: 'teacher-1',
    teacherName: 'Mrs. Priya Sharma',
    targetClass: '10th',
    downloads: 19,
    createdAt: new Date('2026-06-04').toISOString(),
    updatedAt: new Date('2026-06-04').toISOString(),
  },
  {
    id: 'note-5',
    title: 'Electromagnetic Waves',
    subject: 'Physics',
    description: 'Study material covering the electromagnetic spectrum, properties of EM waves, and practical applications.',
    fileUrl: '#',
    fileName: 'em_waves.pdf',
    fileType: 'pdf',
    fileSize: 3072000,
    tags: ['physics', 'electromagnetic', 'waves'],
    teacherId: 'teacher-2',
    teacherName: 'Mr. Rajesh Kumar',
    targetClass: '10th',
    downloads: 37,
    createdAt: new Date('2026-06-05').toISOString(),
    updatedAt: new Date('2026-06-05').toISOString(),
  },
];

let classes = [
  {
    id: 'class-1',
    title: 'Live Trigonometry Problem Solving',
    subject: 'Mathematics',
    teacherId: 'teacher-1',
    teacherName: 'Mrs. Priya Sharma',
    date: '2026-06-08',
    time: '10:00',
    duration: 60,
    platform: 'jitsi',
    meetingLink: 'https://meet.jit.si/educonnect-math-trig-session',
    status: 'upcoming',
    createdAt: new Date('2026-06-04').toISOString(),
  },
  {
    id: 'class-2',
    title: 'Physics Lab: Force & Motion',
    subject: 'Physics',
    teacherId: 'teacher-2',
    teacherName: 'Mr. Rajesh Kumar',
    date: '2026-06-09',
    time: '14:00',
    duration: 90,
    platform: 'jitsi',
    meetingLink: 'https://meet.jit.si/educonnect-physics-lab-forces',
    status: 'upcoming',
    createdAt: new Date('2026-06-04').toISOString(),
  },
  {
    id: 'class-3',
    title: 'Algebra Revision Session',
    subject: 'Mathematics',
    teacherId: 'teacher-1',
    teacherName: 'Mrs. Priya Sharma',
    date: '2026-06-10',
    time: '11:00',
    duration: 45,
    platform: 'zoom',
    meetingLink: 'https://zoom.us/j/example123',
    status: 'upcoming',
    createdAt: new Date('2026-06-05').toISOString(),
  },
  {
    id: 'class-4',
    title: 'Thermodynamics Introduction',
    subject: 'Physics',
    teacherId: 'teacher-2',
    teacherName: 'Mr. Rajesh Kumar',
    date: '2026-06-12',
    time: '09:00',
    duration: 60,
    platform: 'meet',
    meetingLink: 'https://meet.google.com/abc-defg-hij',
    status: 'upcoming',
    createdAt: new Date('2026-06-05').toISOString(),
  },
];

let nextNoteId = 6;
let nextClassId = 5;

// ─── Auth Functions ──────────────────────────────────────────
export const demoAuth = {
  currentUser: null,

  async signUp(email, password, profileData) {
    await delay(800);
    const uid = `${profileData.role}-${Date.now()}`;
    const user = {
      uid,
      email,
      ...profileData,
      createdAt: new Date().toISOString(),
    };
    users[uid] = user;
    this.currentUser = user;
    localStorage.setItem('educonnect_user', JSON.stringify(user));
    return user;
  },

  async login(email, password) {
    await delay(600);
    const user = Object.values(users).find((u) => u.email === email);
    if (!user) {
      throw new Error('No user found with this email. Please sign up first.');
    }
    this.currentUser = user;
    localStorage.setItem('educonnect_user', JSON.stringify(user));
    return user;
  },

  async logout() {
    await delay(300);
    this.currentUser = null;
    localStorage.removeItem('educonnect_user');
  },

  async resetPassword(email) {
    await delay(500);
    const user = Object.values(users).find((u) => u.email === email);
    if (!user) throw new Error('No account found with this email.');
    return true;
  },

  getStoredUser() {
    const stored = localStorage.getItem('educonnect_user');
    if (stored) {
      const user = JSON.parse(stored);
      this.currentUser = user;
      return user;
    }
    return null;
  },

  async getUserProfile(uid) {
    await delay(200);
    return users[uid] || null;
  },
};

// ─── Notes Functions ─────────────────────────────────────────
export const demoNotes = {
  async uploadNote(metadata) {
    await delay(1000);
    const note = {
      id: `note-${nextNoteId++}`,
      ...metadata,
      fileUrl: '#',
      downloads: 0,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };
    notes.unshift(note);
    return note;
  },

  async getNotesByTeacher(teacherId) {
    await delay(400);
    return notes.filter((n) => n.teacherId === teacherId);
  },

  async getAllNotes(filters = {}) {
    await delay(400);
    let result = [...notes];
    if (filters.subject) {
      result = result.filter((n) => n.subject === filters.subject);
    }
    if (filters.fileType) {
      result = result.filter((n) => n.fileType === filters.fileType);
    }
    if (filters.search) {
      const q = filters.search.toLowerCase();
      result = result.filter(
        (n) =>
          n.title.toLowerCase().includes(q) ||
          n.subject.toLowerCase().includes(q) ||
          n.tags.some((t) => t.toLowerCase().includes(q))
      );
    }
    if (filters.sort === 'oldest') {
      result.sort((a, b) => new Date(a.createdAt) - new Date(b.createdAt));
    } else if (filters.sort === 'downloads') {
      result.sort((a, b) => b.downloads - a.downloads);
    } else {
      result.sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));
    }
    return result;
  },

  async getNoteById(noteId) {
    await delay(200);
    return notes.find((n) => n.id === noteId) || null;
  },

  async updateNote(noteId, updates) {
    await delay(500);
    const idx = notes.findIndex((n) => n.id === noteId);
    if (idx === -1) throw new Error('Note not found');
    notes[idx] = { ...notes[idx], ...updates, updatedAt: new Date().toISOString() };
    return notes[idx];
  },

  async deleteNote(noteId) {
    await delay(400);
    notes = notes.filter((n) => n.id !== noteId);
    return true;
  },

  async incrementDownload(noteId) {
    const note = notes.find((n) => n.id === noteId);
    if (note) note.downloads += 1;
  },
};

// ─── Classes Functions ───────────────────────────────────────
export const demoClasses = {
  async createClass(classData) {
    await delay(800);
    const cls = {
      id: `class-${nextClassId++}`,
      ...classData,
      status: 'upcoming',
      createdAt: new Date().toISOString(),
    };
    classes.unshift(cls);
    return cls;
  },

  async getClassesByTeacher(teacherId) {
    await delay(400);
    return classes.filter((c) => c.teacherId === teacherId);
  },

  async getUpcomingClasses() {
    await delay(400);
    const now = new Date();
    return classes
      .filter((c) => {
        const classDate = new Date(`${c.date}T${c.time}`);
        return classDate >= now || c.status === 'upcoming';
      })
      .sort((a, b) => new Date(`${a.date}T${a.time}`) - new Date(`${b.date}T${b.time}`));
  },

  async getAllClasses() {
    await delay(400);
    return [...classes].sort(
      (a, b) => new Date(`${b.date}T${b.time}`) - new Date(`${a.date}T${a.time}`)
    );
  },

  async getClassById(classId) {
    await delay(200);
    return classes.find((c) => c.id === classId) || null;
  },

  async updateClass(classId, updates) {
    await delay(500);
    const idx = classes.findIndex((c) => c.id === classId);
    if (idx === -1) throw new Error('Class not found');
    classes[idx] = { ...classes[idx], ...updates };
    return classes[idx];
  },

  async deleteClass(classId) {
    await delay(400);
    classes = classes.filter((c) => c.id !== classId);
    return true;
  },
};

// ─── Stats ───────────────────────────────────────────────────
export const demoStats = {
  async getTeacherStats(teacherId) {
    await delay(300);
    const teacherNotes = notes.filter((n) => n.teacherId === teacherId);
    const teacherClasses = classes.filter(
      (c) => c.teacherId === teacherId && c.status === 'upcoming'
    );
    const totalStudents = Object.values(users).filter((u) => u.role === 'student').length;
    return {
      totalNotes: teacherNotes.length,
      activeClasses: teacherClasses.length,
      totalStudents,
      totalDownloads: teacherNotes.reduce((sum, n) => sum + n.downloads, 0),
    };
  },

  async getStudentStats() {
    await delay(300);
    const now = new Date();
    const upcomingClasses = classes.filter((c) => new Date(`${c.date}T${c.time}`) >= now);
    return {
      notesAvailable: notes.length,
      upcomingClasses: upcomingClasses.length,
      downloadedResources: Math.floor(Math.random() * 10) + 5,
    };
  },
};
