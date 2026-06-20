import os
import uuid
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, g
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

def create_notification(cursor, department_id, year_of_study, message, link):
    cursor.execute("""
        SELECT id FROM users 
        WHERE role = 'student' AND department_id = %s AND year_of_study = %s
    """, (department_id, year_of_study))
    students = cursor.fetchall()
    # Fetchall gives dicts because we pass cursor=conn.cursor(dictionary=True) in most places, 
    # but let's be safe and access by dict or tuple.
    for student in students:
        user_id = student['id'] if isinstance(student, dict) else student[0]
        cursor.execute("""
            INSERT INTO notifications (user_id, message, link)
            VALUES (%s, %s, %s)
        """, (user_id, message, link))

@app.before_request
def before_request_handler():
    g.notifications = []
    g.is_verified = True
    if 'user_id' in session:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            try:
                cursor.execute("SELECT is_verified FROM users WHERE id = %s", (session['user_id'],))
                user = cursor.fetchone()
                if user:
                    g.is_verified = user.get('is_verified', True)
                    
                cursor.execute("UPDATE users SET last_active = NOW() WHERE id = %s", (session['user_id'],))
                cursor.execute("SELECT * FROM notifications WHERE user_id = %s AND is_read = FALSE ORDER BY created_at DESC", (session['user_id'],))
                g.notifications = cursor.fetchall()
                conn.commit()
            except Exception as e:
                pass
            finally:
                cursor.close()
                conn.close()

# ---------- API ROUTES ----------
@app.route('/api/colleges')
def api_colleges():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, name FROM colleges ORDER BY name")
    colleges = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify({"colleges": colleges})

@app.route('/api/departments/<int:college_id>')
def api_departments(college_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, name FROM departments WHERE college_id = %s ORDER BY name", (college_id,))
    departments = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify({"departments": departments})

# ---------- ROUTES ----------

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/terms')
def terms():
    return render_template('terms.html')

@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')
        
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO contact_messages (name, email, message) VALUES (%s, %s, %s)", (name, email, message))
            conn.commit()
            cursor.close()
            conn.close()
            flash("Your message has been sent successfully!", "success")
        except Exception as e:
            flash("An error occurred while sending your message. Please try again later.", "error")
            
        return redirect(url_for('contact'))
        
    return render_template('contact.html')

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
            session['user_college'] = user['college_id']
            session['user_department'] = user['department_id']
            session['user_year'] = user.get('year_of_study')
            
            if user['role'] == 'teacher':
                return redirect(url_for('teacher_dashboard'))
            elif user['role'] in ['admin', 'college_admin', 'superadmin']:
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('student_dashboard'))
        else:
            flash("Invalid email or password", "error")
            return redirect(url_for('login'))

    return render_template('login.html')

import random
from datetime import datetime, timedelta

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()
            if user:
                otp = str(random.randint(100000, 999999))
                expires_at = datetime.now() + timedelta(minutes=15)
                cursor.execute("INSERT INTO password_resets (email, otp, expires_at) VALUES (%s, %s, %s)", (email, otp, expires_at))
                conn.commit()
                # Simulate sending email
                flash(f"OTP sent to your email! (Simulation: Your OTP is {otp})", "success")
                cursor.close()
                conn.close()
                return redirect(url_for('verify_otp', email=email))
            else:
                flash("Email not found in our system.", "error")
            cursor.close()
            conn.close()
    return render_template('forgot_password.html')

@app.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp():
    email = request.args.get('email')
    if request.method == 'POST':
        email = request.form['email']
        otp = request.form['otp']
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT id FROM password_resets WHERE email = %s AND otp = %s AND expires_at > NOW() ORDER BY created_at DESC LIMIT 1", (email, otp))
            reset = cursor.fetchone()
            cursor.close()
            conn.close()
            if reset:
                flash("OTP verified. Please reset your password.", "success")
                return redirect(url_for('reset_password', email=email, otp=otp))
            else:
                flash("Invalid or expired OTP.", "error")
    return render_template('verify_otp.html', email=email)

@app.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    email = request.args.get('email')
    otp = request.args.get('otp')
    if request.method == 'POST':
        email = request.form['email']
        otp = request.form['otp']
        password = request.form['password']
        
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT id FROM password_resets WHERE email = %s AND otp = %s AND expires_at > NOW() ORDER BY created_at DESC LIMIT 1", (email, otp))
            reset = cursor.fetchone()
            if reset:
                hashed_password = generate_password_hash(password)
                cursor.execute("UPDATE users SET password_hash = %s WHERE email = %s", (hashed_password, email))
                cursor.execute("DELETE FROM password_resets WHERE email = %s", (email,))
                conn.commit()
                flash("Password successfully reset! You can now login.", "success")
                cursor.close()
                conn.close()
                return redirect(url_for('login'))
            else:
                flash("Invalid or expired reset session. Please try again.", "error")
            cursor.close()
            conn.close()
    return render_template('reset_password.html', email=email, otp=otp)

@app.route('/signup')
def generic_signup():
    return render_template('role_selection.html')

@app.route('/signup/<role>', methods=['GET', 'POST'])
def signup(role):
    if role not in ['teacher', 'student', 'college_admin']:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        hashed_password = generate_password_hash(password)
        
        conn = get_db_connection()
        if not conn:
            flash("Database connection error.", "error")
            return redirect(url_for('signup', role=role))
            
        cursor = conn.cursor()
        try:
            if role == 'college_admin':
                college_name = request.form.get('college_name')
                # Check if college exists
                cursor.execute("SELECT id FROM colleges WHERE name = %s", (college_name,))
                if cursor.fetchone():
                    flash("Institution name already exists. Please login or choose another.", "error")
                    return redirect(url_for('signup', role=role))
                    
                cursor.execute("INSERT INTO colleges (name) VALUES (%s)", (college_name,))
                college_id = cursor.lastrowid
                department_id = None
                year_of_study = None
            else:
                college_id = request.form.get('college_id')
                department_id = request.form.get('department_id')
                year_of_study = request.form.get('year_of_study')

            verification_token = uuid.uuid4().hex
            cursor.execute("""
                INSERT INTO users (name, email, password_hash, role, college_id, department_id, year_of_study, is_verified, verification_token)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (name, email, hashed_password, role, college_id, department_id, year_of_study, False, verification_token))
            conn.commit()
            
            verify_url = url_for('verify_email', token=verification_token, _external=True)
            flash(f"Registration successful. For testing, please <a href='{verify_url}'>click here to verify your email</a>.", "success")
            return redirect(url_for('login'))
        except Exception as e:
            conn.rollback()
            flash("Email already registered or another error occurred.", "error")
        finally:
            cursor.close()
            conn.close()
            
    return render_template('signup.html', role=role)

@app.route('/verify-email/<token>')
def verify_email(token):
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE verification_token = %s AND is_verified = FALSE", (token,))
        user = cursor.fetchone()
        if user:
            cursor.execute("UPDATE users SET is_verified = TRUE, verification_token = NULL WHERE id = %s", (user[0],))
            conn.commit()
            flash("Your email has been successfully verified! You can now access all features.", "success")
        else:
            flash("Invalid or expired verification link.", "error")
        cursor.close()
        conn.close()
    return redirect(url_for('login'))
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/notifications/clear')
def clear_notifications():
    if 'user_id' in session:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE notifications SET is_read = TRUE WHERE user_id = %s", (session['user_id'],))
        conn.commit()
        cursor.close()
        conn.close()
    return redirect(request.referrer or url_for('index'))

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
    
    cursor.execute("SELECT COUNT(*) as count FROM resources WHERE department_id = %s AND year_of_study = %s", (session.get('user_department'), session.get('user_year')))
    total_notes = cursor.fetchone()['count']
    
    cursor.execute("SELECT COUNT(*) as count FROM classes WHERE date >= CURDATE() AND department_id = %s AND year_of_study = %s", (session.get('user_department'), session.get('user_year')))
    active_classes = cursor.fetchone()['count']
    
    cursor.execute("""
        SELECT c.*, u.name as teacher_name 
        FROM classes c 
        JOIN users u ON c.teacher_id = u.id 
        WHERE c.date >= CURDATE() AND c.department_id = %s AND c.year_of_study = %s
        ORDER BY c.date ASC, c.time ASC LIMIT 3
    """, (session.get('user_department'), session.get('user_year')))
    upcoming_classes = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    stats = {
        'total_notes': total_notes,
        'active_classes': active_classes
    }
    
    return render_template('student_dashboard.html', stats=stats, upcoming_classes=upcoming_classes)

@app.route('/admin/dashboard')
def admin_dashboard():
    role = session.get('user_role')
    if 'user_id' not in session or role not in ['admin', 'college_admin', 'superadmin']:
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if role == 'superadmin':
        cursor.execute("SELECT COUNT(*) as count FROM users WHERE role = 'student'")
        total_students = cursor.fetchone()['count']
        cursor.execute("SELECT COUNT(*) as count FROM users WHERE role = 'teacher'")
        total_teachers = cursor.fetchone()['count']
        cursor.execute("SELECT COUNT(*) as count FROM resources")
        total_resources = cursor.fetchone()['count']
        cursor.execute("SELECT COUNT(*) as count FROM classes")
        total_classes = cursor.fetchone()['count']
    else:
        # college_admin logic
        col_id = session.get('user_college')
        cursor.execute("SELECT COUNT(*) as count FROM users WHERE role = 'student' AND college_id = %s", (col_id,))
        total_students = cursor.fetchone()['count']
        cursor.execute("SELECT COUNT(*) as count FROM users WHERE role = 'teacher' AND college_id = %s", (col_id,))
        total_teachers = cursor.fetchone()['count']
        cursor.execute("""
            SELECT COUNT(r.id) as count FROM resources r
            JOIN users u ON r.teacher_id = u.id WHERE u.college_id = %s
        """, (col_id,))
        total_resources = cursor.fetchone()['count']
        cursor.execute("""
            SELECT COUNT(c.id) as count FROM classes c
            JOIN users u ON c.teacher_id = u.id WHERE u.college_id = %s
        """, (col_id,))
        total_classes = cursor.fetchone()['count']
    
    cursor.close()
    conn.close()
    
    stats = {
        'students': total_students,
        'teachers': total_teachers,
        'resources': total_resources,
        'classes': total_classes
    }
    
    return render_template('admin_dashboard.html', stats=stats, is_superadmin=(role=='superadmin'))

@app.route('/admin/users')
def admin_users():
    role = session.get('user_role')
    if 'user_id' not in session or role not in ['admin', 'college_admin', 'superadmin']:
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if role == 'superadmin':
        cursor.execute("""
            SELECT u.*, c.name as college_name 
            FROM users u 
            LEFT JOIN colleges c ON u.college_id = c.id
            WHERE u.role != 'superadmin' 
            ORDER BY u.created_at DESC
        """)
    else:
        cursor.execute("""
            SELECT u.*, c.name as college_name 
            FROM users u 
            LEFT JOIN colleges c ON u.college_id = c.id
            WHERE u.role NOT IN ('superadmin', 'college_admin') AND u.college_id = %s 
            ORDER BY u.created_at DESC
        """, (session.get('user_college'),))
        
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    
    from datetime import datetime, timedelta
    now = datetime.now()
    for user in users:
        if user.get('last_active'):
            user['is_online'] = (now - user['last_active']) < timedelta(minutes=5)
        else:
            user['is_online'] = False
            
    return render_template('admin_users.html', users=users, is_superadmin=(role=='superadmin'))

@app.route('/admin/user/<int:id>/delete', methods=['POST'])
def admin_delete_user(id):
    role = session.get('user_role')
    if 'user_id' not in session or role not in ['admin', 'college_admin', 'superadmin']:
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if role == 'superadmin':
        cursor.execute("DELETE FROM live_presentations WHERE teacher_id = %s", (id,))
        cursor.execute("DELETE FROM users WHERE id = %s AND role != 'superadmin'", (id,))
    else:
        # Ensure college admin can only delete their own college users
        cursor.execute("DELETE FROM live_presentations WHERE teacher_id = %s AND teacher_id IN (SELECT id FROM users WHERE college_id = %s)", (id, session.get('user_college')))
        cursor.execute("DELETE FROM users WHERE id = %s AND college_id = %s AND role NOT IN ('superadmin', 'college_admin')", (id, session.get('user_college')))
        
    conn.commit()
    cursor.close()
    conn.close()
    
    flash("User deleted successfully.", "success")
    return redirect(url_for('admin_users'))

@app.route('/admin/departments', methods=['GET', 'POST'])
def admin_departments():
    role = session.get('user_role')
    if 'user_id' not in session or role not in ['college_admin']:
        if role in ['admin', 'superadmin']:
            flash("Superadmins cannot directly manage a specific college's courses from here yet.", "info")
            return redirect(url_for('admin_dashboard'))
        return redirect(url_for('login'))
        
    college_id = session.get('user_college')
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        dept_name = request.form.get('department_name')
        if dept_name:
            try:
                cursor.execute("INSERT INTO departments (college_id, name) VALUES (%s, %s)", (college_id, dept_name))
                conn.commit()
                flash("Department added successfully.", "success")
            except Exception as e:
                conn.rollback()
                flash("Failed to add department.", "error")
                
    cursor.execute("SELECT * FROM departments WHERE college_id = %s ORDER BY name", (college_id,))
    departments = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('admin_departments.html', departments=departments)

@app.route('/admin/department/<int:id>/delete', methods=['POST'])
def admin_delete_department(id):
    role = session.get('user_role')
    if 'user_id' not in session or role not in ['college_admin']:
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM departments WHERE id = %s AND college_id = %s", (id, session.get('user_college')))
        conn.commit()
        flash("Department deleted successfully.", "success")
    except Exception as e:
        conn.rollback()
        flash("Error deleting department. It may be in use.", "error")
    finally:
        cursor.close()
        conn.close()
        
    return redirect(url_for('admin_departments'))

@app.route('/teacher/upload', methods=['GET', 'POST'])
def teacher_upload():
    if 'user_id' not in session or session.get('user_role') != 'teacher':
        return redirect(url_for('login'))
        
    if request.method == 'POST':
        title = request.form['title']
        subject = request.form['subject']
        description = request.form.get('description', '')
        
        department_id = request.form.get('department_id')
        year_of_study = request.form.get('year_of_study')
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
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                INSERT INTO resources (teacher_id, title, subject, description, department_id, year_of_study, file_url, file_type, file_size, tags)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (session['user_id'], title, subject, description, department_id, year_of_study, file_url, file_type, file_size, tags))
            
            # Create notification
            teacher_name = session.get('user_name', 'Your teacher')
            create_notification(cursor, department_id, year_of_study, f"{teacher_name} uploaded a new resource: {title}", "/student/notes")
            
            conn.commit()
            cursor.close()
            conn.close()
            
            flash("Resource uploaded successfully!", "success")
            return redirect(url_for('teacher_dashboard'))
            
    return render_template('teacher_upload.html', college_id=session.get('user_college'))

@app.route('/student/notes')
def student_notes():
    if 'user_id' not in session or session.get('user_role') != 'student':
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    search_query = request.args.get('q', '')
    
    if search_query:
        cursor.execute("""
            SELECT r.*, u.name as teacher_name 
            FROM resources r
            JOIN users u ON r.teacher_id = u.id
            WHERE r.department_id = %s AND r.year_of_study = %s
            AND (r.title LIKE %s OR u.name LIKE %s)
            ORDER BY r.created_at DESC
        """, (session.get('user_department'), session.get('user_year'), f"%{search_query}%", f"%{search_query}%"))
    else:
        cursor.execute("""
            SELECT r.*, u.name as teacher_name 
            FROM resources r
            JOIN users u ON r.teacher_id = u.id
            WHERE r.department_id = %s AND r.year_of_study = %s
            ORDER BY r.created_at DESC
        """, (session.get('user_department'), session.get('user_year')))
        
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
        max_students_raw = request.form.get('max_students', '')
        max_students = int(max_students_raw) if max_students_raw.strip() else 0
        department_id = request.form.get('department_id')
        year_of_study = request.form.get('year_of_study')
        platform = 'Native'
        room_id = uuid.uuid4().hex
        meeting_link = f"/meeting/{room_id}"
        
        cursor.execute("""
            INSERT INTO classes (teacher_id, title, subject, date, time, duration, platform, meeting_link, department_id, year_of_study, max_students)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (session['user_id'], title, subject, date, time, duration, platform, meeting_link, department_id, year_of_study, max_students))
        
        # Create notification
        teacher_name = session.get('user_name', 'Your teacher')
        create_notification(cursor, department_id, year_of_study, f"{teacher_name} scheduled a new live session: {title}", "/student/classes")
        
        conn.commit()
        flash("Live session scheduled successfully!", "success")
        return redirect(url_for('teacher_classes'))

    cursor.execute("SELECT * FROM classes WHERE teacher_id = %s ORDER BY date ASC, time ASC", (session['user_id'],))
    classes = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('teacher_classes.html', classes=classes, college_id=session.get('user_college'))

@app.route('/student/classes')
def student_classes():
    if 'user_id' not in session or session.get('user_role') != 'student':
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    search_query = request.args.get('q', '')
    
    if search_query:
        cursor.execute("""
            SELECT c.*, u.name as teacher_name 
            FROM classes c
            JOIN users u ON c.teacher_id = u.id
            WHERE c.date >= CURDATE() AND c.department_id = %s AND c.year_of_study = %s
            AND (c.topic LIKE %s OR u.name LIKE %s)
            ORDER BY c.date ASC, c.time ASC
        """, (session.get('user_department'), session.get('user_year'), f"%{search_query}%", f"%{search_query}%"))
    else:
        cursor.execute("""
            SELECT c.*, u.name as teacher_name 
            FROM classes c
            JOIN users u ON c.teacher_id = u.id
            WHERE c.date >= CURDATE() AND c.department_id = %s AND c.year_of_study = %s
            ORDER BY c.date ASC, c.time ASC
        """, (session.get('user_department'), session.get('user_year')))
        
    classes = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('student_classes.html', classes=classes)

@app.route('/student/class/<int:id>/join')
def student_join_class(id):
    if 'user_id' not in session or session.get('user_role') != 'student':
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT meeting_link FROM classes WHERE id = %s", (id,))
    cls = cursor.fetchone()
    
    if cls:
        try:
            cursor.execute("""
                INSERT INTO class_attendance (class_id, student_id)
                VALUES (%s, %s)
            """, (id, session['user_id']))
            conn.commit()
        except Exception as err:
            pass # Ignore duplicate entries if they join multiple times
            
        cursor.close()
        conn.close()
        return redirect(cls['meeting_link'])
        
    cursor.close()
    conn.close()
    flash("Class not found", "error")
    return redirect(url_for('student_classes'))

@app.route('/teacher/class/<int:id>/attendance')
def teacher_attendance(id):
    if 'user_id' not in session or session.get('user_role') != 'teacher':
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM classes WHERE id = %s AND teacher_id = %s", (id, session['user_id']))
    cls = cursor.fetchone()
    
    if not cls:
        cursor.close()
        conn.close()
        flash("Class not found or access denied.", "error")
        return redirect(url_for('teacher_classes'))
        
    cursor.execute("""
        SELECT a.joined_at, u.name, u.email
        FROM class_attendance a
        JOIN users u ON a.student_id = u.id
        WHERE a.class_id = %s
        ORDER BY a.joined_at ASC
    """, (id,))
    attendees = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('teacher_attendance.html', cls=cls, attendees=attendees)

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
        cursor.execute("DELETE FROM live_presentations WHERE resource_id = %s", (id,))
        cursor.execute("DELETE FROM resources WHERE id = %s", (id,))
        conn.commit()
        flash("Resource deleted successfully.", "success")
        
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
        return jsonify({"error": "Unauthorized"}), 401
        
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE live_presentations SET is_active = 0 WHERE room_code = %s AND teacher_id = %s", (room_code, session['user_id']))
    conn.commit()
    cursor.close()
    conn.close()
    
    socketio.emit('presentation_ended', {'room': room_code}, to=room_code)
    return jsonify({"status": "success"})

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        new_password = request.form.get('new_password')
        
        try:
            if new_password:
                from werkzeug.security import generate_password_hash
                hashed_pw = generate_password_hash(new_password)
                cursor.execute("UPDATE users SET name=%s, email=%s, password_hash=%s WHERE id=%s", (name, email, hashed_pw, session['user_id']))
            else:
                cursor.execute("UPDATE users SET name=%s, email=%s WHERE id=%s", (name, email, session['user_id']))
            
            conn.commit()
            session['user_name'] = name
            flash("Profile updated successfully!", "success")
        except Exception as e:
            flash("Error updating profile. The email might already be in use.", "error")
            
        return redirect(url_for('profile'))
        
    cursor.execute("""
        SELECT u.*, c.name as college_name, d.name as department_name 
        FROM users u
        LEFT JOIN colleges c ON u.college_id = c.id
        LEFT JOIN departments d ON u.department_id = d.id
        WHERE u.id = %s
    """, (session['user_id'],))
    user_data = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    return render_template('profile.html', user=user_data)

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
