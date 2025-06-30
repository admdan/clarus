from .db import get_db_connection
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from itsdangerous import URLSafeTimedSerializer

class User(UserMixin):
    def __init__(self, id, username, email, role='basic'):
        self.id = id #Flask-Login uses this as user_id
        self.username = username
        self.email = email
        self.role = role

# Used during registration to insert new user into the database
def insert_user(username, email, password, role='basic'):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    hashed_pw = generate_password_hash(password, method='pbkdf2:sha256')

    try:
        cursor.execute('''
                       INSERT INTO users (username, email, password_hash, role)
                           VALUES (%s, %s, %s, %s)''',
                       (username, email, hashed_pw, role)
        )
        conn.commit()
    except Exception as e:
        print(f"[ERROR] Failed to insert user: {e}") #Debug line
    finally:
        cursor.close()
        conn.close()

# Used during login to validate the password
def verify_user(username, password):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute('''SELECT * 
                      FROM users 
                      WHERE username = %s''',
                   (username,))
    user = cursor.fetchone()

    cursor.close()
    conn.close()

    # If a user is found, compare the stored hash with the entered password
    if user and check_password_hash(user['password_hash'], password):
        return True
    return False

# Used by Flask-Login to load a user from session using their ID
def get_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('''SELECT * 
                      FROM users
                      WHERE id = %s''',
                   (user_id,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if user:
        return User(id=user['id'], username=user['username'], email=user['email'], role=user.get('role', 'basic'))
    return None

# Used for login authentication (typically using username + password)
def get_user_by_username(username):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('''SELECT * 
                      FROM users 
                      WHERE username = %s''',
                   (username,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if user:
        return User(id=user['id'], username=user['username'], email=user['email'], role=user.get('role', 'basic'))
    return None

def get_user_by_email(email):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('''SELECT *
                      FROM users 
                      WHERE email = %s''',
                   (email,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user

# Used for generating reset token for password reset
def generate_reset_token(email, secret_key, salt):
    serializer = URLSafeTimedSerializer(secret_key)
    return serializer.dumps(email, salt=salt)


# Used for verification of the reset token
def verify_reset_token(token, secret_key, salt, expiration=3600):
    serializer = URLSafeTimedSerializer(secret_key)
    try:
        email = serializer.loads(token, salt=salt, max_age=expiration)
    except:
        return None
    return email