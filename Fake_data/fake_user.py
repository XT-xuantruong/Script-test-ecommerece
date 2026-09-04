import bcrypt
import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    user="12345",
    password="12345",
    port=3306,
    database="ecommerce_api"
)
cursor = conn.cursor()

password = bcrypt.hashpw("password123".encode(), bcrypt.gensalt()).decode()
for i in range(10000):
    print(i)
    username = "User" + str(i + 1)
    email = "user" + str(i + 1) + "@example.com"
    cursor.execute(
        "INSERT INTO users (email, full_name, password, role_id, avatar, phone, address, created_at) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())",
        (email, username, password, 3, "", "", "")
    )
conn.commit()
cursor.close()
conn.close()
