from app.db import get_db_connection


try:
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT 1")
    print("Database connection successful!")
except Exception as e:
    print(f"Database connection failed: {e}")



from app.db import get_db_connection

# Test verileri
first_name = "Test"
last_name = "User"
email = "test112@example.com"
username = "testuser12312"
password = "hashed_password"
gender = "Male"
country = "Country"
city = "City"
role = "user"

# Veritabanına bağlantı
connection = get_db_connection()
cursor = connection.cursor()

try:
    # Kayıt ekleme işlemi
    cursor.execute(
        """
        INSERT INTO users (first_name, last_name, email, username, password, gender, country, city, role)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (first_name, last_name, email, username, password, gender, country, city, role)
    )
    connection.commit()
    print("Record inserted successfully!")
except Exception as e:
    print(f"Error occurred: {e}")
finally:
    connection.close()

