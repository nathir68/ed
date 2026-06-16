import mysql.connector
from mysql.connector import Error

def migrate_database():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='NatSah#0608',
            database='educonnect_db'
        )

        if connection.is_connected():
            cursor = connection.cursor()
            
            queries = [
                "CREATE TABLE IF NOT EXISTS colleges (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(150) UNIQUE NOT NULL, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)",
                "CREATE TABLE IF NOT EXISTS departments (id INT AUTO_INCREMENT PRIMARY KEY, college_id INT NOT NULL, name VARCHAR(150) NOT NULL, FOREIGN KEY (college_id) REFERENCES colleges(id) ON DELETE CASCADE)",
                "ALTER TABLE users MODIFY COLUMN role ENUM('teacher', 'student', 'admin', 'college_admin', 'superadmin') NOT NULL",
                "ALTER TABLE users ADD COLUMN college_id INT",
                "ALTER TABLE users ADD COLUMN department_id INT",
                "ALTER TABLE users ADD FOREIGN KEY (college_id) REFERENCES colleges(id) ON DELETE SET NULL",
                "ALTER TABLE users ADD FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE SET NULL",
                "ALTER TABLE users CHANGE class_grade year_of_study VARCHAR(50)",
                
                "ALTER TABLE resources ADD COLUMN department_id INT",
                "ALTER TABLE resources ADD COLUMN year_of_study VARCHAR(50)",
                "ALTER TABLE resources ADD FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE SET NULL",
                
                "ALTER TABLE classes ADD COLUMN department_id INT",
                "ALTER TABLE classes ADD COLUMN year_of_study VARCHAR(50)",
                "ALTER TABLE classes ADD FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE SET NULL",
                
                "UPDATE users SET role = 'superadmin' WHERE email = 'admin@educonnect.com'",
                
                # Insert a dummy college and department so we have something to test with
                "INSERT IGNORE INTO colleges (id, name) VALUES (1, 'Engineering College')",
                "INSERT IGNORE INTO departments (id, college_id, name) VALUES (1, 1, 'Computer Science')",
                "INSERT IGNORE INTO departments (id, college_id, name) VALUES (2, 1, 'Mechanical Engineering')"
            ]
            
            for query in queries:
                try:
                    cursor.execute(query)
                    print(f"Executed successfully.")
                except Error as e:
                    print(f"Ignored error (likely already applied): {e}")

            connection.commit()
            print("Migration completed.")

    except Error as e:
        print(f"Database error: {e}")
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == '__main__':
    migrate_database()
