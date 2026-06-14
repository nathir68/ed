# CLS Listener (EduConnect)

This project is a comprehensive educational platform that connects teachers and students, allowing them to share resources and conduct live interactive classes.

The application is built primarily using **Python (Flask)** for the backend, **MySQL** for the database, and **HTML/CSS/JS (Jinja2 templates)** for the frontend. It also includes WebRTC for live presentations and a separate React application codebase in the `src` folder.

## Project Structure and Components

Here is a breakdown of how each part of the codebase works:

### 1. Backend Core (`app.py`)
This is the main entry point of the Flask application. It handles all the core functionalities:
- **Routing:** Defines all the URL endpoints for the application (e.g., `/`, `/login`, `/teacher/dashboard`, `/student/dashboard`).
- **Authentication:** Manages user registration and login using `werkzeug.security` for password hashing and Flask `session` for managing user state.
- **Role-based Access:** Distinguishes between 'teacher' and 'student' roles, directing them to their respective dashboards and restricting access to certain routes.
- **Resource Management:** Handles file uploads (notes, documents) by teachers and allows students to view/download them. Files are stored in the `static/uploads` directory.
- **Live Classes & WebRTC Signaling:** Uses `Flask-SocketIO` to manage real-time communication. It handles WebRTC signaling (offers, answers, ICE candidates) to establish peer-to-peer connections for live video/audio meetings between teachers and students. It also manages room joining and chat messages.

### 2. Database Management (`setup_db.py` & `database.py`)
These files manage the MySQL database connection and schema.
- **`setup_db.py`**: A standalone script used to initialize the database. When run, it creates the `educonnect_db` database and sets up the necessary tables:
  - `users`: Stores user credentials, roles, and profile information.
  - `resources`: Stores metadata about uploaded files (title, file path, teacher ID).
  - `classes`: Stores scheduled live classes.
  - It also includes references to `live_presentations` for active sessions.
- **`database.py`**: A helper module that provides a `get_db_connection()` function used throughout `app.py` to establish a connection to the MySQL database.

### 3. Frontend Templates (`templates/` directory)
This directory contains all the HTML views rendered by Flask using the Jinja2 templating engine.
- **Base Layout (`base.html`)**: The master template containing the common layout (header, navigation, footer, CSS/JS links). Other pages extend this base layout.
- **Authentication Pages (`login.html`, `signup.html`)**: Forms for users to log in or register.
- **Dashboards (`teacher_dashboard.html`, `student_dashboard.html`)**: The main hubs for users after logging in, showing statistics, upcoming classes, and recent notes.
- **Resource Pages (`teacher_upload.html`, `student_notes.html`, `resource_view.html`)**: Interfaces for uploading and viewing study materials.
- **Live Meeting Pages (`meeting_room.html`, `presentation_dashboard.html`, `presentation_student.html`)**: The interfaces for the live WebRTC classes. They include video elements and chat interfaces.

### 4. Static Assets (`static/` directory)
This folder typically serves files directly to the browser without modification.
- **Uploads (`static/uploads/`)**: This is where the application saves files uploaded by teachers.
- It likely also contains custom CSS stylesheets, client-side JavaScript files, and images used in the HTML templates.

### 5. React Frontend (`src/` directory)
While the main application is served via Flask templates, there is a separate React application located in the `src/` directory.
- **`main.jsx` & `App.jsx`**: The entry points of the React application.
- **`firebase/`**: Contains Firebase configuration, suggesting this React app might use Firebase for authentication or database services.
- **`context/`, `utils/`, `assets/`**: Standard React folder structures for state management, helper functions, and static assets.
- This React app appears to be either a modern rewrite in progress, a separate specific feature module, or a practice app included in the same repository.

## How to Run the Application

1. **Set up the Database:**
   Ensure you have MySQL installed and running. Edit the credentials in `database.py` and `setup_db.py` if necessary. Run the setup script to create the database and tables:
   ```bash
   python setup_db.py
   ```

2. **Install Dependencies:**
   Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Flask App:**
   Start the main application:
   ```bash
   python app.py
   ```
   The application will be accessible at `http://localhost:5000`.
