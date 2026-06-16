import mysql.connector
from mysql.connector import Error
from werkzeug.security import generate_password_hash

def create_admin():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='NatSah#0608',
            database='educonnect_db'
        )

        if connection.is_connected():
            cursor = connection.cursor()
            
            # Alter the users table to allow 'admin' role
            try:
                cursor.execute("ALTER TABLE users MODIFY COLUMN role ENUM('teacher', 'student', 'admin') NOT NULL")
                print("Table 'users' altered successfully.")
            except Error as e:
                print(f"Note: Could not alter table (might already be altered): {e}")

            # Check if admin already exists
            cursor.execute("SELECT id FROM users WHERE email = 'admin@educonnect.com'")
            if cursor.fetchone():
                print("Admin user already exists.")
            else:
                # Insert default admin user
                hashed_password = generate_password_hash('admin123')
                cursor.execute("""
                    INSERT INTO users (name, email, password_hash, role)
                    VALUES (%s, %s, %s, %s)
                """, ('System Admin', 'admin@educonnect.com', hashed_password, 'admin'))
                connection.commit()
                print("Default admin user created successfully (Email: admin@educonnect.com, Password: admin123).")

    except Error as e:
        print(f"Error: {e}")
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed.")

if __name__ == '__main__':
    create_admin()
