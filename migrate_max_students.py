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
                cursor.execute("ALTER TABLE classes ADD COLUMN max_students INT DEFAULT 0")
                print("Added max_students column successfully.")
            except Error as e:
                print(f"Column might already exist. Ignored error: {e}")

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
