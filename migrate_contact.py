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
            
            try:
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS contact_messages (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    email VARCHAR(100) NOT NULL,
                    message TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """)
                print("Created contact_messages table.")
            except Error as e:
                print(f"Error creating contact_messages table: {e}")

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
