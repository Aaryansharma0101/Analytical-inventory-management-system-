import bcrypt 
from database import get_connection

def register_user(username, email, password):
    conn = get_connection()
    cursor = conn.cursor()

    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    try:
        cursor.execute("""
            INSERT INTO users (username, email, password_hash)
            VALUES (?, ?, ?)
        """, (username, email, hashed))

        conn.commit()
        return True, "User registered successfully"

    except:
        return False, "Username or Email already exists"

    finally:
        conn.close()


def login_user(identifier, password):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM users 
        WHERE username = ? OR email = ?
    """, (identifier, identifier))

    user = cursor.fetchone()
    conn.close()

    if not user:
        return False, "User not found", None

    if bcrypt.checkpw(password.encode(), user["password_hash"]):
        return True, "Login successful", dict(user)

    return False, "Wrong password", None
