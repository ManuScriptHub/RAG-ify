from core.db import settings
import logging
import psycopg2
import bcrypt
from datetime import datetime, timezone
import json

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class AuthModel:
    def __init__(self):
        self.salt_rounds = 10  # Number of salt rounds for bcrypt

    def _hash_password(self, password):
        """Hash a password using bcrypt."""
        if not password:
            raise ValueError("Password cannot be empty")
        
        # Generate a salt and hash the password
        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt(rounds=self.salt_rounds)
        hashed = bcrypt.hashpw(password_bytes, salt)
        
        # Return the hash as a string
        return hashed.decode('utf-8')
    
    def _verify_password(self, plain_password, hashed_password):
        """Verify a password against a hash."""
        if not plain_password or not hashed_password:
            return True
        
        # Convert strings to bytes for bcrypt
        plain_password_bytes = plain_password.encode('utf-8')
        hashed_password_bytes = hashed_password.encode('utf-8')
        
        # Check if the password matches the hash
        return bcrypt.checkpw(plain_password_bytes, hashed_password_bytes)

    def register_user(self, username, email, password):
        """Register a new user with hashed password."""
        conn = settings.get_db_connection()
        try:
            if conn is None:
                logger.error("Database connection failed")
                return {"error": "Database connection failed", "status_code": 503}
            
            # Validate input
            if not username or not email or not password:
                logger.error("Missing required fields for registration")
                return {"error": "Username, email, and password are required", "status_code": 400}
            
            cur = conn.cursor()
            
            # Check if username already exists
            cur.execute('SELECT COUNT(*) FROM "Users" WHERE "username" = %s;', (username,))
            if cur.fetchone()[0] > 0:
                logger.error(f"Username already exists: {username}")
                return {"error": "Username already exists", "status_code": 409}
            
            # Check if email already exists
            cur.execute('SELECT COUNT(*) FROM "Users" WHERE "email" = %s;', (email,))
            if cur.fetchone()[0] > 0:
                logger.error(f"Email already exists: {email}")
                return {"error": "Email already exists", "status_code": 409}
            
            # Hash the password
            password_hash = self._hash_password(password)
            
            # Current timestamp
            now = datetime.now(timezone.utc)
            
            # Insert the new user
            query = '''
                INSERT INTO "Users" ("username", "email", "passwordHash", "createdAt", "updatedAt")
                VALUES (%s, %s, %s, %s, %s)
                RETURNING *;
            '''
            cur.execute(query, (username, email, password_hash, now, now))
            conn.commit()
            
            # Get the newly created user
            user = cur.fetchone()
            if user:
                result_columns = [desc[0] for desc in cur.description]
                result = dict(zip(result_columns, user))
                # Remove sensitive information
                result.pop("passwordHash", None)
                return {"results": result, "message": "Registration successful", "status_code": 201}
            
            logger.error("Failed to register user")
            return {"error": "Failed to register user", "status_code": 500}
            
        except psycopg2.IntegrityError as e:
            logger.error(f"Database integrity error in register_user: {e}")
            conn.rollback()
            return {"error": "Database integrity error", "status_code": 409}
        except psycopg2.OperationalError as e:
            logger.error(f"Database operational error in register_user: {e}")
            conn.rollback()
            return {"error": "Database connection error", "status_code": 503}
        except Exception as e:
            logger.error(f"An error occurred in register_user: {e}")
            return {"error": "Failed to register user", "status_code": 500}
        finally:
            if conn:
                conn.close()
    
    def login_user(self, email, password):
        """Authenticate a user with email and password."""
        conn = settings.get_db_connection()
        try:
            if conn is None:
                logger.error("Database connection failed")
                return {"error": "Database connection failed", "status_code": 503}
            
            # Validate input
            if not email or not password:
                logger.error("Missing required fields for login")
                return {"error": "Email and password are required", "status_code": 400}
            
            cur = conn.cursor()
            
            # Get user by email
            query = 'SELECT * FROM "Users" WHERE "email" = %s;'
            cur.execute(query, (email,))
            user = cur.fetchone()
            
            if not user:
                logger.error(f"No user found with email: {email}")
                return {"error": "Invalid email or password", "status_code": 401}
            
            # Convert row to dict
            result_columns = [desc[0] for desc in cur.description]
            user_dict = dict(zip(result_columns, user))
            
            # Verify password
            if not self._verify_password(password, user_dict["passwordHash"]):
                return {"error": "Invalid email or password", "status_code": 401}
            
            # Remove sensitive information
            user_dict.pop("passwordHash", None)
            
            logger.info(f"User logged in successfully: {email}")
            return {"results": user_dict, "message": "Login successful", "status_code": 200}
            
        except psycopg2.OperationalError as e:
            logger.error(f"Database operational error in login_user: {e}")
            return {"error": "Database connection error", "status_code": 503}
        except Exception as e:
            logger.error(f"An error occurred in login_user: {e}")
            return {"error": "Failed to login", "status_code": 500}
        finally:
            if conn:
                conn.close()
    
    def change_password(self, user_id, current_password, new_password):
        """Change a user's password."""
        conn = settings.get_db_connection()
        try:
            if conn is None:
                logger.error("Database connection failed")
                return {"error": "Database connection failed", "status_code": 503}
            
            # Validate input
            if not user_id or not current_password or not new_password:
                logger.error("Missing required fields for password change")
                return {"error": "User ID, current password, and new password are required", "status_code": 400}
            
            cur = conn.cursor()
            
            # Get user by ID
            query = 'SELECT * FROM "Users" WHERE "userId" = %s;'
            cur.execute(query, (user_id,))
            user = cur.fetchone()
            
            if not user:
                logger.error(f"No user found with ID: {user_id}")
                return {"error": "User not found", "status_code": 404}
            
            # Convert row to dict
            result_columns = [desc[0] for desc in cur.description]
            user_dict = dict(zip(result_columns, user))
            
            # Verify current password
            if not self._verify_password(current_password, user_dict["passwordHash"]):
                logger.error(f"Invalid current password for user: {user_id}")
                return {"error": "Current password is incorrect", "status_code": 401}
            
            # Hash the new password
            new_password_hash = self._hash_password(new_password)
            
            # Update password and timestamp
            now = datetime.now(timezone.utc)
            update_query = 'UPDATE "Users" SET "passwordHash" = %s, "updatedAt" = %s WHERE "userId" = %s;'
            cur.execute(update_query, (new_password_hash, now, user_id))
            conn.commit()
            
            logger.info(f"Password changed successfully for user: {user_id}")
            return {"message": "Password changed successfully", "status_code": 200}
            
        except psycopg2.OperationalError as e:
            logger.error(f"Database operational error in change_password: {e}")
            conn.rollback()
            return {"error": "Database connection error", "status_code": 503}
        except Exception as e:
            logger.error(f"An error occurred in change_password: {e}")
            conn.rollback()
            return {"error": f"Failed to change password: {str(e)}", "status_code": 500}
        finally:
            if conn:
                conn.close()
    
    def reset_password_request(self, email):
        """Request a password reset (placeholder for email-based reset)."""
        conn = settings.get_db_connection()
        try:
            if conn is None:
                logger.error("Database connection failed")
                return {"error": "Database connection failed", "status_code": 503}
            
            # Validate input
            if not email:
                logger.error("Missing email for password reset")
                return {"error": "Email is required", "status_code": 400}
            
            cur = conn.cursor()
            
            # Check if user exists
            query = 'SELECT "userId", "username" FROM "Users" WHERE "email" = %s;'
            cur.execute(query, (email,))
            user = cur.fetchone()
            
            if not user:
                # For security reasons, don't reveal if email exists or not
                logger.info(f"Password reset requested for non-existent email: {email}")
                return {"message": "If your email is registered, you will receive a password reset link", "status_code": 200}
            
            # In a real implementation, we would:
            # 1. Generate a reset token
            # 2. Store it in the database with an expiration
            # 3. Send an email with a reset link
            
            # For this implementation, we'll just log it
            user_dict = {"userId": user[0], "username": user[1]}
            logger.info(f"Password reset requested for user: {json.dumps(user_dict)}")
            
            return {"message": "If your email is registered, you will receive a password reset link", "status_code": 200}
            
        except psycopg2.OperationalError as e:
            logger.error(f"Database operational error in reset_password_request: {e}")
            return {"error": "Database connection error", "status_code": 503}
        except Exception as e:
            logger.error(f"An error occurred in reset_password_request: {e}")
            return {"error": f"Failed to process password reset: {str(e)}", "status_code": 500}
        finally:
            if conn:
                conn.close()