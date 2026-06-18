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
            
            # 1. Notifications table
            try:
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS notifications (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    message TEXT NOT NULL,
                    link VARCHAR(255),
                    is_read BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
                """)
                print("Created notifications table.")
            except Error as e:
                print(f"Error creating notifications table: {e}")

            # 2. Add verification fields to users
            try:
                cursor.execute("ALTER TABLE users ADD COLUMN is_verified BOOLEAN DEFAULT FALSE")
                print("Added is_verified column.")
            except Error as e:
                # Column might already exist
                pass
                
            try:
                cursor.execute("ALTER TABLE users ADD COLUMN verification_token VARCHAR(100)")
                print("Added verification_token column.")
            except Error as e:
                pass
                
            # Verify all existing users so they don't get locked out
            try:
                cursor.execute("UPDATE users SET is_verified = TRUE WHERE is_verified = FALSE")
                print("Verified existing users.")
            except Error as e:
                pass

            # 3. Password resets table
            try:
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS password_resets (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    email VARCHAR(100) NOT NULL,
                    otp VARCHAR(10) NOT NULL,
                    expires_at TIMESTAMP NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """)
                print("Created password_resets table.")
            except Error as e:
                print(f"Error creating password_resets table: {e}")

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
