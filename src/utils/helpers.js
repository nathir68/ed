export function whatsappShare(message, link) {
  const encodedMessage = encodeURIComponent(`${message}\n\n🔗 ${link}`);
  window.open(`https://wa.me/?text=${encodedMessage}`, '_blank');
}

export function shareNoteOnWhatsApp(note) {
  const link = `${window.location.origin}/resource/${note.id}`;
  const message = `📚 *New Notes Available!*\n\nSubject: ${note.subject}\nTopic: ${note.title}\nShared by: ${note.teacherName}\n\n🔗 Access here: ${link}\n\nLogin with your student credentials to download.`;
  whatsappShare(message, '');
}

export function shareClassOnWhatsApp(cls) {
  const link = `${window.location.origin}/class/${cls.id}`;
  const message = `🎥 *Live Class Scheduled!*\n\nSubject: ${cls.subject}\nTopic: ${cls.title}\nTeacher: ${cls.teacherName}\nDate: ${cls.date}\nTime: ${cls.time}\n\n🔗 Join here: ${link}\n\nLogin with your student credentials to join.`;
  whatsappShare(message, '');
}

export function copyToClipboard(text) {
  navigator.clipboard.writeText(text);
}

export function getFileIcon(fileType) {
  switch (fileType) {
    case 'pdf': return '📄';
    case 'doc': case 'docx': return '📝';
    case 'ppt': case 'pptx': return '📊';
    case 'jpg': case 'jpeg': case 'png': case 'gif': return '🖼️';
    default: return '📎';
  }
}

export function getFileTypeLabel(fileType) {
  switch (fileType) {
    case 'pdf': return 'PDF';
    case 'doc': case 'docx': return 'DOC';
    case 'ppt': case 'pptx': return 'PPT';
    case 'jpg': case 'jpeg': case 'png': case 'gif': return 'Image';
    default: return 'File';
  }
}

export function formatFileSize(bytes) {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
}

export function isNewNote(createdAt) {
  const threeDaysAgo = new Date();
  threeDaysAgo.setDate(threeDaysAgo.getDate() - 3);
  return new Date(createdAt) > threeDaysAgo;
}

export function generateCalendarFile(cls) {
  const start = new Date(`${cls.date}T${cls.time}`);
  const end = new Date(start.getTime() + (cls.duration || 60) * 60000);

  const formatDate = (d) => d.toISOString().replace(/[-:]/g, '').split('.')[0] + 'Z';

  const ics = `BEGIN:VCALENDAR
VERSION:2.0
BEGIN:VEVENT
DTSTART:${formatDate(start)}
DTEND:${formatDate(end)}
SUMMARY:${cls.title}
DESCRIPTION:Live class by ${cls.teacherName}\\nSubject: ${cls.subject}\\nJoin: ${cls.meetingLink}
URL:${cls.meetingLink}
END:VEVENT
END:VCALENDAR`;

  const blob = new Blob([ics], { type: 'text/calendar' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `${cls.title.replace(/\s+/g, '_')}.ics`;
  a.click();
  URL.revokeObjectURL(url);
}
