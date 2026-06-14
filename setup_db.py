import mysql.connector
from mysql.connector import Error

def create_database():
    try:
        # Connect to MySQL server (no database specified yet)
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='NatSah#0608'
        )

        if connection.is_connected():
            cursor = connection.cursor()
            
            # Create Database
            cursor.execute("CREATE DATABASE IF NOT EXISTS educonnect_db")
            print("Database 'educonnect_db' created successfully.")
            
            # Switch to the new database
            cursor.execute("USE educonnect_db")
            
            # Create Users Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                role ENUM('teacher', 'student') NOT NULL,
                subject VARCHAR(100),
                institution VARCHAR(150),
                class_grade VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            print("Table 'users' created successfully.")

            # Create Notes/Resources Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS resources (
                id INT AUTO_INCREMENT PRIMARY KEY,
                teacher_id INT NOT NULL,
                title VARCHAR(150) NOT NULL,
                subject VARCHAR(100) NOT NULL,
                description TEXT,
                target_class VARCHAR(50),
                file_url VARCHAR(255) NOT NULL,
                file_type VARCHAR(50),
                file_size INT,
                downloads INT DEFAULT 0,
                tags VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (teacher_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """)
            print("Table 'resources' created successfully.")

            # Create Live Classes Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS classes (
                id INT AUTO_INCREMENT PRIMARY KEY,
                teacher_id INT NOT NULL,
                title VARCHAR(150) NOT NULL,
                subject VARCHAR(100) NOT NULL,
                date DATE NOT NULL,
                time TIME NOT NULL,
                duration INT DEFAULT 60,
                platform VARCHAR(50),
                meeting_link VARCHAR(255) NOT NULL,
                status VARCHAR(50) DEFAULT 'upcoming',
                target_class VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (teacher_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """)
            print("Table 'classes' created successfully.")

    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed.")

if __name__ == '__main__':
    create_database()
