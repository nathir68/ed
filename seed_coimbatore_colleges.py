import mysql.connector
from mysql.connector import Error

def seed_database():
    colleges_data = [
        {
            "name": "PSG College of Technology (Engineering)",
            "departments": [
                "Computer Science and Engineering",
                "Information Technology",
                "Mechanical Engineering",
                "Electronics and Communication Engineering",
                "Civil Engineering",
                "Electrical and Electronics Engineering"
            ]
        },
        {
            "name": "Coimbatore Institute of Technology (Engineering)",
            "departments": [
                "Computer Science and Engineering",
                "Mechanical Engineering",
                "Electronics and Communication Engineering",
                "Civil Engineering"
            ]
        },
        {
            "name": "Kumaraguru College of Technology (Engineering)",
            "departments": [
                "Computer Science and Engineering",
                "Artificial Intelligence and Data Science",
                "Information Technology",
                "Mechanical Engineering",
                "Aeronautical Engineering"
            ]
        },
        {
            "name": "PSG College of Arts and Science",
            "departments": [
                "B.Sc Computer Science",
                "B.Com (Commerce)",
                "BBA (Business Administration)",
                "B.A English Literature",
                "B.Sc Mathematics"
            ]
        },
        {
            "name": "Sri Krishna Arts and Science College",
            "departments": [
                "B.Sc Information Technology",
                "BCA (Computer Applications)",
                "B.Com (Commerce)",
                "BBA (Business Administration)"
            ]
        },
        {
            "name": "Dr. G.R. Damodaran College of Science",
            "departments": [
                "B.Sc Computer Science",
                "B.Com (Commerce)",
                "Management Studies",
                "Visual Communication"
            ]
        }
    ]

    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='NatSah#0608',
            database='educonnect_db'
        )

        if connection.is_connected():
            cursor = connection.cursor()
            
            for college in colleges_data:
                # Insert college
                try:
                    cursor.execute("INSERT INTO colleges (name) VALUES (%s)", (college['name'],))
                    college_id = cursor.lastrowid
                    print(f"Added College: {college['name']}")
                except Error as e:
                    # If it already exists, fetch the ID
                    cursor.execute("SELECT id FROM colleges WHERE name = %s", (college['name'],))
                    result = cursor.fetchone()
                    if result:
                        college_id = result[0]
                        print(f"College already exists: {college['name']}")
                    else:
                        print(f"Error inserting college {college['name']}: {e}")
                        continue

                # Insert departments for this college
                for dept in college['departments']:
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
