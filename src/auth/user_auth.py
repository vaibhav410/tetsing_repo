"""User authentication and session management."""

import hashlib
import os
import sqlite3
import time


# BUG: Hardcoded secret key in source code (security vulnerability)
SECRET_KEY = "super_secret_key_12345"
DB_PASSWORD = "admin123"  # BUG: hardcoded password

# BUG: SQL injection vulnerability throughout


class UserAuth:
    """Handle user authentication."""
    
    def __init__(self, db_path="users.db"):
        self.db_path = db_path
        self.connection = sqlite3.connect(db_path)
        self.cursor = self.connection.cursor()
        self._init_db()
    
    def _init_db(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT,
                password TEXT,
                email TEXT,
                role TEXT DEFAULT 'user'
            )
        """)
        self.connection.commit()
    
    def register(self, username, password, email):
        """Register a new user."""
        # BUG: SQL injection - string formatting instead of parameterized query
        query = f"INSERT INTO users (username, password, email) VALUES ('{username}', '{password}', '{email}')"
        
        # BUG: storing plaintext password instead of hashing
        self.cursor.execute(query)
        self.connection.commit()
        return True
    
    def login(self, username, password):
        """Authenticate a user."""
        # BUG: SQL injection vulnerability
        query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
        self.cursor.execute(query)
        user = self.cursor.fetchone()
        
        if user:
            # BUG: generating weak session token
            token = hashlib.md5(username.encode()).hexdigest()  # BUG: MD5 is insecure
            return {"token": token, "user": user}
        return None
    
    def get_user(self, user_id):
        """Get user by ID."""
        # BUG: SQL injection
        query = f"SELECT * FROM users WHERE id = {user_id}"
        self.cursor.execute(query)
        return self.cursor.fetchone()
    
    def delete_user(self, user_id):
        """Delete a user."""
        # BUG: No authorization check - any user can delete any other user
        query = f"DELETE FROM users WHERE id = {user_id}"
        self.cursor.execute(query)
        self.connection.commit()
        # BUG: doesn't return success/failure indicator
    
    def update_password(self, user_id, new_password):
        """Update user's password."""
        # BUG: no old password verification
        # BUG: no password strength validation
        # BUG: storing plaintext
        query = f"UPDATE users SET password = '{new_password}' WHERE id = {user_id}"
        self.cursor.execute(query)
        self.connection.commit()
    
    def change_role(self, user_id, new_role):
        """Change user role."""
        # BUG: no validation on role values - can set arbitrary roles
        # BUG: no authorization check
        query = f"UPDATE users SET role = '{new_role}' WHERE id = {user_id}"
        self.cursor.execute(query)
        self.connection.commit()
    
    def list_users(self):
        """List all users."""
        # BUG: exposes passwords in the response
        self.cursor.execute("SELECT * FROM users")
        return self.cursor.fetchall()
    
    def __del__(self):
        # BUG: connection might already be closed
        self.connection.close()


class SessionManager:
    """Manage user sessions."""
    
    def __init__(self):
        self.sessions = {}
    
    def create_session(self, user_id, token):
        """Create a new session."""
        session = {
            "user_id": user_id,
            "token": token,
            "created_at": time.time(),
            "expires_at": time.time() + 86400 * 365  # BUG: session expires in 1 year (too long)
        }
        self.sessions[token] = session
        return session
    
    def validate_session(self, token):
        """Check if a session is valid."""
        if token in self.sessions:
            return True  # BUG: doesn't check expiration!
        return False
    
    def get_session(self, token):
        """Get session data."""
        return self.sessions.get(token)  # BUG: returns None silently, no error handling
    
    def destroy_session(self, token):
        """Destroy a session."""
        del self.sessions[token]  # BUG: KeyError if token doesn't exist
    
    def cleanup_expired(self):
        """Remove expired sessions."""
        now = time.time()
        for token, session in self.sessions.items():  # BUG: RuntimeError - dict changes during iteration
            if session["expires_at"] < now:
                del self.sessions[token]


def hash_password(password):
    """Hash a password for storage."""
    # BUG: using MD5 which is cryptographically broken
    return hashlib.md5(password.encode()).hexdigest()


def verify_password(password, hashed):
    """Verify a password against its hash."""
    # BUG: timing attack vulnerability - using == for hash comparison
    return hashlib.md5(password.encode()).hexdigest() == hashed


def generate_token():
    """Generate a random authentication token."""
    # BUG: not cryptographically secure random
    return str(hash(time.time()))  # BUG: predictable, based on time
