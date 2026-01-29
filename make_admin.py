from database import get_connection

username = "Dipesh"

conn = get_connection()
cursor = conn.cursor()

cursor.execute("UPDATE users SET role = 'admin' WHERE username = ?", (username,))
conn.commit()
conn.close()

print("You are now ADMIN")
