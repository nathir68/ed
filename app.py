import os
import uuid
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from database import get_db_connection
from flask_socketio import SocketIO, emit, join_room, leave_room

app = Flask(__name__)
app.secret_key = 'educonnect_super_secret_key'
socketio = SocketIO(app, cors_allowed_origins="*")

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'ppt', 'pptx', 'jpg', 'jpeg', 'png'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ---------- ROUTES ----------

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        conn = get_db_connection()
        if not conn:
            flash("Database connection error.", "error")
            return redirect(url_for('login'))
            
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            session['user_role'] = user['role']
            session['user_subject'] = user['subject']
            session['user_class_grade'] = user['class_grade']
            
            if user['role'] == 'teacher':
                return redirect(url_for('teacher_dashboard'))
            else:
                return redirect(url_for('student_dashboard'))
        else:
            flash("Invalid email or password", "error")
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/signup/<role>', methods=['GET', 'POST'])
def signup(role):
    if role not in ['teacher', 'student']:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        hashed_password = generate_password_hash(password)
        
        subject = request.form.get('subject', None)
        institution = request.form.get('institution', None)
        class_grade = request.form.get('class_grade', None)
        
        conn = get_db_connection()
        if not conn:
            flash("Database connection error.", "error")
            return redirect(url_for('signup', role=role))
            
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO users (name, email, password_hash, role, subject, institution, class_grade)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (name, email, hashed_password, role, subject, institution, class_grade))
            conn.commit()
            flash("Registration successful. Please login.", "success")
            return redirect(url_for('login'))
        except Exception as e:
            conn.rollback()
            flash("Email already registered or another error occurred.", "error")
        finally:
            cursor.close()
            conn.close()
            
    return render_template('signup.html', role=role)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/teacher/dashboard')
def teacher_dashboard():
    if 'user_id' not in session or session.get('user_role') != 'teacher':
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT COUNT(*) as count FROM resources WHERE teacher_id = %s", (session['user_id'],))
    total_notes = cursor.fetchone()['count']
    
    cursor.execute("SELECT COUNT(*) as count FROM classes WHERE teacher_id = %s AND date >= CURDATE()", (session['user_id'],))
    active_classes = cursor.fetchone()['count']
    
    cursor.execute("SELECT * FROM resources WHERE teacher_id = %s ORDER BY created_at DESC LIMIT 3", (session['user_id'],))
    recent_notes = cursor.fetchall()
    
    cursor.execute("SELECT * FROM classes WHERE teacher_id = %s AND date >= CURDATE() ORDER BY date ASC, time ASC LIMIT 2", (session['user_id'],))
    upcoming_classes = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    stats = {
        'total_notes': total_notes,
        'active_classes': active_classes
    }
    
    return render_template('teacher_dashboard.html', stats=stats, recent_notes=recent_notes, upcoming_classes=upcoming_classes)

@app.route('/student/dashboard')
def student_dashboard():
    if 'user_id' not in session or session.get('user_role') != 'student':
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT COUNT(*) as count FROM resources")
    total_notes = cursor.fetchone()['count']
    
    cursor.execute("SELECT COUNT(*) as count FROM classes WHERE date >= CURDATE()")
    active_classes = cursor.fetchone()['count']
    
    cursor.execute("""
        SELECT c.*, u.name as teacher_name 
        FROM classes c 
        JOIN users u ON c.teacher_id = u.id 
        WHERE c.date >= CURDATE() 
        ORDER BY c.date ASC, c.time ASC LIMIT 3
    """)
    upcoming_classes = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    stats = {
        'total_notes': total_notes,
        'active_classes': active_classes
    }
    
    return render_template('student_dashboard.html', stats=stats, upcoming_classes=upcoming_classes)

@app.route('/teacher/upload', methods=['GET', 'POST'])
def teacher_upload():
    if 'user_id' not in session or session.get('user_role') != 'teacher':
        return redirect(url_for('login'))
        
    if request.method == 'POST':
        title = request.form['title']
        subject = request.form['subject']
        description = request.form.get('description', '')
        target_class = request.form.get('target_class', 'all')
        tags = request.form.get('tags', '')
        
        if 'file' not in request.files:
            flash('No file part', 'error')
            return redirect(request.url)
            
        file = request.files['file']
        if file.filename == '':
            flash('No selected file', 'error')
            return redirect(request.url)
            
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            file_size = os.path.getsize(file_path)
            file_type = filename.rsplit('.', 1)[1].lower()
            file_url = f"/static/uploads/{filename}"
            
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO resources (teacher_id, title, subject, description, target_class, file_url, file_type, file_size, tags)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (session['user_id'], title, subject, description, target_class, file_url, file_type, file_size, tags))
            conn.commit()
            cursor.close()
            conn.close()
            
            flash("Resource uploaded successfully!", "success")
            return redirect(url_for('teacher_dashboard'))
            
    return render_template('teacher_upload.html')

@app.route('/student/notes')
def student_notes():
    if 'user_id' not in session or session.get('user_role') != 'student':
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT r.*, u.name as teacher_name 
        FROM resources r
        JOIN users u ON r.teacher_id = u.id
        ORDER BY r.created_at DESC
    """)
    notes = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('student_notes.html', notes=notes)

# ---------- NEW ROUTES ----------

@app.route('/teacher/classes', methods=['GET', 'POST'])
def teacher_classes():
    if 'user_id' not in session or session.get('user_role') != 'teacher':
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        title = request.form['title']
        subject = request.form['subject']
        date = request.form['date']
        time = request.form['time']
        duration = request.form['duration']
        platform = 'Native'
        room_id = uuid.uuid4().hex
        meeting_link = f"/meeting/{room_id}"
        
        cursor.execute("""
            INSERT INTO classes (teacher_id, title, subject, date, time, duration, platform, meeting_link)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (session['user_id'], title, subject, date, time, duration, platform, meeting_link))
        conn.commit()
        flash("Live session scheduled successfully!", "success")
        return redirect(url_for('teacher_classes'))

    cursor.execute("SELECT * FROM classes WHERE teacher_id = %s ORDER BY date ASC, time ASC", (session['user_id'],))
    classes = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('teacher_classes.html', classes=classes)

@app.route('/student/classes')
def student_classes():
    if 'user_id' not in session or session.get('user_role') != 'student':
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT c.*, u.name as teacher_name 
        FROM classes c
        JOIN users u ON c.teacher_id = u.id
        WHERE c.date >= CURDATE()
        ORDER BY c.date ASC, c.time ASC
    """)
    classes = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('student_classes.html', classes=classes)

@app.route('/resource/<int:id>')
def resource_view(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT r.*, u.name as teacher_name 
        FROM resources r
        JOIN users u ON r.teacher_id = u.id
        WHERE r.id = %s
    """, (id,))
    resource = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    if not resource:
        flash("Resource not found.", "error")
        if session.get('user_role') == 'teacher':
            return redirect(url_for('teacher_dashboard'))
        return redirect(url_for('student_notes'))
        
    return render_template('resource_view.html', resource=resource)

@app.route('/teacher/resource/<int:id>/delete', methods=['POST'])
def teacher_delete_resource(id):
    if 'user_id' not in session or session.get('user_role') != 'teacher':
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT file_url FROM resources WHERE id = %s AND teacher_id = %s", (id, session['user_id']))
    resource = cursor.fetchone()
    
    if resource:
        # Delete dependent live presentations first to satisfy foreign key constraints
        cursor.execute("DELETE FROM live_presentations WHERE resource_id = %s", (id,))
        
        cursor.execute("DELETE FROM resources WHERE id = %s", (id,))
        conn.commit()
        flash("Resource deleted successfully.", "success")
        
        # Optionally remove the physical file here
        file_path = resource['file_url'].lstrip('/')
        if os.path.exists(file_path):
            os.remove(file_path)
    else:
        flash("Resource not found or permission denied.", "error")
        
    cursor.close()
    conn.close()
    
    return redirect(url_for('teacher_dashboard'))

@app.route('/meeting/<room_id>')
def meeting_room(room_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('meeting_room.html', room_id=room_id, user_name=session.get('user_name'), user_role=session.get('user_role'))

# ---------- LIVE PRESENTATION (LOCKDOWN) ----------

@app.route('/teacher/presentation/start/<int:resource_id>', methods=['GET', 'POST'])
def start_presentation(resource_id):
    if session.get('user_role') != 'teacher':
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM resources WHERE id = %s AND teacher_id = %s", (resource_id, session['user_id']))
    resource = cursor.fetchone()
    
    if not resource:
        cursor.close()
        conn.close()
        return "Resource not found or unauthorized", 404
        
    if request.method == 'POST':
        duration = int(request.form.get('duration', 45))
        room_code = uuid.uuid4().hex[:8].upper()
        
        cursor.execute("""
            INSERT INTO live_presentations (room_code, teacher_id, resource_id, duration_minutes)
            VALUES (%s, %s, %s, %s)
        """, (room_code, session['user_id'], resource_id, duration))
        conn.commit()
        cursor.close()
        conn.close()
        
        return redirect(url_for('presentation_dashboard', room_code=room_code))
        
    cursor.close()
    conn.close()
    return render_template('presentation_start.html', resource=resource)

@app.route('/teacher/presentation/dashboard/<room_code>')
def presentation_dashboard(room_code):
    if session.get('user_role') != 'teacher':
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT p.*, r.title, r.file_url, r.file_type 
        FROM live_presentations p 
        JOIN resources r ON p.resource_id = r.id 
        WHERE p.room_code = %s AND p.teacher_id = %s AND p.is_active = 1
    """, (room_code, session['user_id']))
    presentation = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if not presentation:
        return "Presentation not found or ended.", 404
        
    return render_template('presentation_dashboard.html', presentation=presentation)

@app.route('/presentation/<room_code>')
def student_presentation(room_code):
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT p.*, r.title, r.file_url, r.file_type, u.name as teacher_name
        FROM live_presentations p 
        JOIN resources r ON p.resource_id = r.id
        JOIN users u ON p.teacher_id = u.id
        WHERE p.room_code = %s AND p.is_active = 1
    """, (room_code,))
    presentation = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if not presentation:
        return "This presentation has ended or does not exist.", 404
        
    return render_template('presentation_student.html', presentation=presentation, user_name=session.get('user_name'))

@app.route('/api/presentation/end/<room_code>', methods=['POST'])
def end_presentation(room_code):
    if session.get('user_role') != 'teacher':
        return {"error": "Unauthorized"}, 401
        
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE live_presentations SET is_active = 0 WHERE room_code = %s AND teacher_id = %s", (room_code, session['user_id']))
    conn.commit()
    cursor.close()
    conn.close()
    
    socketio.emit('presentation_ended', {'room': room_code}, to=room_code)
    return {"status": "success"}

# ---------- WEBRTC & PRESENTATION SIGNALING ----------

@socketio.on('join_presentation')
def on_join_presentation(data):
    room = data['room']
    user_name = data['user_name']
    join_room(room)
    emit('student_joined', {'sid': request.sid, 'user_name': user_name}, to=room, include_self=False)

@socketio.on('focus_alert')
def on_focus_alert(data):
    room = data['room']
    user_name = data['user_name']
    alert_type = data['alert_type']
    emit('student_focus_alert', {'sid': request.sid, 'user_name': user_name, 'alert_type': alert_type}, to=room, include_self=False)
    
@socketio.on('focus_restored')
def on_focus_restored(data):
    room = data['room']
    user_name = data['user_name']
    emit('student_focus_restored', {'sid': request.sid, 'user_name': user_name}, to=room, include_self=False)

@socketio.on('join')
def on_join(data):
    room = data['room']
    user_name = data.get('user_name', 'Anonymous')
    role = data.get('role', 'student')
    join_room(room)
    # Broadcast to others in the room that a user has joined
    emit('user_joined', {'sid': request.sid, 'user_name': user_name, 'role': role}, to=room, include_self=False)

@socketio.on('offer')
def on_offer(data):
    target_sid = data.get('target_sid')
    if target_sid:
        data['sender_sid'] = request.sid
        emit('offer', data, to=target_sid)

@socketio.on('answer')
def on_answer(data):
    target_sid = data.get('target_sid')
    if target_sid:
        data['sender_sid'] = request.sid
        emit('answer', data, to=target_sid)

@socketio.on('ice_candidate')
def on_ice_candidate(data):
    target_sid = data.get('target_sid')
    if target_sid:
        data['sender_sid'] = request.sid
        emit('ice_candidate', data, to=target_sid)

@socketio.on('chat_message')
def on_chat_message(data):
    room = data['room']
    emit('chat_message', {
        'sender_name': data['sender_name'],
        'message': data['message']
    }, to=room, include_self=False)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', debug=True, port=5000, allow_unsafe_werkzeug=True)
