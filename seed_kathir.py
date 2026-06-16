import mysql.connector
from mysql.connector import Error

def seed_database():
    kathir_data = {
        "name": "Kathir College of Engineering",
        "departments": [
            "Computer Science and Engineering",
            "Artificial Intelligence and Data Science",
            "Mechanical Engineering",
            "Electronics and Communication Engineering",
            "Electrical and Electronics Engineering",
            "Civil Engineering"
        ]
    }

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
                cursor.execute("INSERT INTO colleges (name) VALUES (%s)", (kathir_data['name'],))
                college_id = cursor.lastrowid
                print(f"Added College: {kathir_data['name']}")
            except Error as e:
                # If it already exists, fetch the ID
                cursor.execute("SELECT id FROM colleges WHERE name = %s", (kathir_data['name'],))
                result = cursor.fetchone()
                if result:
                    college_id = result[0]
                    print(f"College already exists: {kathir_data['name']}")
                else:
                    print(f"Error inserting college {kathir_data['name']}: {e}")
                    return

            # Insert departments for this college
            for dept in kathir_data['departments']:
                try:
                    cursor.execute("INSERT INTO departments (college_id, name) VALUES (%s, %s)", (college_id, dept))
                    print(f"  -> Added Department: {dept}")
                except Error as e:
                    print(f"  -> Error inserting department {dept}: {e}")

            connection.commit()
            print("Database seeding completed successfully.")

    except Error as e:
        print(f"Database error: {e}")
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == '__main__':
    seed_database()
