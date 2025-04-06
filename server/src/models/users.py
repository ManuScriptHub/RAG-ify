from core.db import settings

class UserModel:
    def get_users(self):
        conn = settings.get_db_connection()  
        try:
            cur = conn.cursor()
            cur.execute('SELECT * FROM "Users";')
            
            result = cur.fetchall()
            return result
        except Exception as e:
            print(f"An error occurred in get_users: {e}")
            return []
        finally:
            if conn:
                conn.close()

    def get_user(self, user_id):
        conn = settings.get_db_connection()  
        try:
            cur = conn.cursor()
            query = 'SELECT * FROM "Users" WHERE "userId" = %s;'
            cur.execute(query, (user_id,))
            row = cur.fetchone()
            if row:
                columns = ["userId", "username", "email", "passwordHash", "createdAt", "updatedAt"]
                return dict(zip(columns, row))  
            return None 
        except Exception as e:
            print(f"An error occurred in get_user: {e}")
            return None 
        finally:
            if conn:
                conn.close()

    def create_user(self, username, email):
        conn = settings.get_db_connection()  
        pswhash = "fff" 
        try:
            cur = conn.cursor()
            query = '''
                INSERT INTO "Users" ("username", "email", "passwordHash")
                VALUES (%s, %s, %s)
                RETURNING "userId", "username", "email", "passwordHash", "createdAt", "updatedAt";
            '''
            cur.execute(query, (username, email, pswhash))
            row = cur.fetchone()
            conn.commit()
            if row:
                columns = ["userId", "username", "email", "passwordHash", "createdAt", "updatedAt"]
                return dict(zip(columns, row))  
            return None 
        except Exception as e:
            print(f"An error occurred in create_user: {e}")
            conn.rollback()  
            return {"error": str(e)}
        finally:
            if conn:
                conn.close()
            
    def update_user(self, user_id, username=None, email=None, password_hash=None):
        conn = settings.get_db_connection()
        try:
            cur = conn.cursor()
            set_clauses = []
            params = []
            if username != "":
                set_clauses.append('"username" = %s')
                params.append(username)
            if email != "":
                set_clauses.append('"email" = %s')
                params.append(email)
            if password_hash != "":
                set_clauses.append('"passwordHash" = %s')
                params.append(password_hash)
            if not set_clauses:
                return None
            set_clause_str = ", ".join(set_clauses) + ', "updatedAt" = CURRENT_TIMESTAMP'
            query = f'''
            UPDATE "Users"
            SET {set_clause_str}
            WHERE "userId" = %s
            RETURNING "userId", "username", "email", "passwordHash", "createdAt", "updatedAt";
            '''
            params.append(user_id)
            cur.execute(query, tuple(params))
            row = cur.fetchone()
            conn.commit()
            if row:
                columns = ["userId", "username", "email", "passwordHash", "createdAt", "updatedAt"]
                return dict(zip(columns, row))
            return None
        except Exception as e:
            conn.rollback()
            return {"error": str(e)}
        finally:
            conn.close()

    def delete_user(self, user_id):
        conn = settings.get_db_connection()  
        try:
            cur = conn.cursor()
            query = 'DELETE FROM "Users" WHERE "userId" = %s;'
            cur.execute(query, (user_id,))
            conn.commit()
            return {"message": "User deleted successfully."}
        except Exception as e:
            conn.rollback()  
            return {"error": str(e)}
        finally:
            if conn:
                conn.close()

                