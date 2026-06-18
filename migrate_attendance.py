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
            
            # Add last_active
            try:
                cursor.execute("ALTER TABLE users ADD COLUMN last_active TIMESTAMP NULL")
                print("Added last_active column to users.")
            except Error as e:
                print(f"Column might already exist. Ignored error: {e}")

            # Create class_attendance table
            try:
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS class_attendance (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    class_id INT NOT NULL,
                    student_id INT NOT NULL,
                    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (class_id) REFERENCES classes(id) ON DELETE CASCADE,
                    FOREIGN KEY (student_id) REFERENCES users(id) ON DELETE CASCADE,
                    UNIQUE KEY unique_attendance (class_id, student_id)
                )
                """)
                print("Created class_attendance table.")
            except Error as e:
                print(f"Error creating class_attendance table: {e}")

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
