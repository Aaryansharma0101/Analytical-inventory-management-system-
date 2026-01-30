import bcrypt 
from database import get_connection

def register_user(username, email, password):
    conn = get_connection()
    cursor = conn.cursor()

    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    try:
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]

        # First registered user becomes ADMIN
        role = "admin" if user_count == 0 else "user"

        cursor.execute("""
            INSERT INTO users (username, email, password_hash, role)
            VALUES (?, ?, ?, ?)
        """, (username, email, hashed, role))
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
