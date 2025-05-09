from core.db import settings
import logging
import psycopg2

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class UserModel:
    def get_users(self, where_conditions=None):
        conn = settings.get_db_connection()  
        try:
            if conn is None:
                logger.error("Database connection failed")
                return {"error": "Database connection failed", "status_code": 503}
                
            cur = conn.cursor()
            
            query = 'SELECT * FROM "Users"'
            params = []
            print(where_conditions)
            # Add WHERE clause if conditions are provided
            if where_conditions:
                if not isinstance(where_conditions, dict):
                    logger.error(f"Invalid where_conditions format: {where_conditions}")
                    return {"error": "Where conditions must be a dictionary", "status_code": 400}
                
                where_clauses = []
                for key, value in where_conditions.items():
                    # Ensure the column name is valid to prevent SQL injection
                    if key in ["userId", "username", "email"]:
                        where_clauses.append(f'"{key}" = %s')
                        params.append(value)
                    else:
                        logger.warning(f"Ignoring invalid column name in where condition: {key}")
                
                if where_clauses:
                    query += " WHERE " + " AND ".join(where_clauses)
            
            query += ";"
            logger.info(f"Executing query: {query} with params: {params}")
            
            cur.execute(query, params)
            result = cur.fetchall()
            logger.info(f"get_users result: {len(result)} records")
            return {"results": [dict(zip([desc[0] for desc in cur.description], row)) for row in result]}
        except psycopg2.OperationalError as e:
            logger.error(f"Database operational error in get_users: {e}")
            return {"error": "Database connection error", "status_code": 503}
        except psycopg2.ProgrammingError as e:
            logger.error(f"SQL syntax error in get_users: {e}")
            return {"error": "Invalid SQL query", "status_code": 500}
        except Exception as e:
            logger.error(f"An error occurred in get_users: {e}")
            return {"error": f"Failed to retrieve users: {str(e)}", "status_code": 500}
        finally:
            if conn:
                conn.close()

    def get_user(self, userId):
        conn = settings.get_db_connection()  
        try:
            if conn is None:
                logger.error("Database connection failed")
                return {"error": "Database connection failed", "status_code": 503}
                
            if not userId:
                logger.error("Missing userId parameter")
                return {"error": "User ID is required", "status_code": 400}
                
            cur = conn.cursor()
            query = 'SELECT * FROM "Users" WHERE "userId" = %s;'
            cur.execute(query, (userId,))
            row = cur.fetchone()
            
            if row:
                columns = ["userId", "username", "email", "passwordHash", "createdAt", "updatedAt"]
                result = dict(zip(columns, row))
                logger.info(f"get_user result for userId {userId}: {result}")
                return {"results": result}
                
            logger.info(f"No user found for userId {userId}")
            return {"error": f"User with ID {userId} not found", "status_code": 404}
            
        except psycopg2.OperationalError as e:
            logger.error(f"Database operational error in get_user: {e}")
            return {"error": "Database connection error", "status_code": 503}
        except psycopg2.ProgrammingError as e:
            logger.error(f"SQL syntax error in get_user: {e}")
            return {"error": "Invalid SQL query", "status_code": 500}
        except Exception as e:
            logger.error(f"An error occurred in get_user: {e}")
            return {"error": f"Failed to retrieve user: {str(e)}", "status_code": 500}
        finally:
            if conn:
                conn.close()

    def create_user(self, user_data):
        conn = settings.get_db_connection()  
        try:
            if conn is None:
                logger.error("Database connection failed")
                return {"error": "Database connection failed", "status_code": 503}
                
            if not user_data or not isinstance(user_data, dict):
                logger.error("Invalid user data format")
                return {"error": "User data must be a valid dictionary", "status_code": 400}
                
            if "username" not in user_data or not user_data["username"]:
                logger.error("Missing required field: username")
                return {"error": "Username is required", "status_code": 400}
                
            if "passwordHash" not in user_data or not user_data["passwordHash"]:
                logger.error("Missing required field: passwordHash")
                return {"error": "Password hash is required", "status_code": 400}
                
            cur = conn.cursor()

            # Ensure email has a default value if not provided
            if "email" not in user_data or not user_data["email"]:
                user_data["email"] = "default@example.com"  # Set a default email

            # Check if username already exists
            cur.execute('SELECT COUNT(*) FROM "Users" WHERE "username" = %s;', (user_data["username"],))
            if cur.fetchone()[0] > 0:
                logger.error(f"Username already exists: {user_data['username']}")
                return {"error": "Username already exists", "status_code": 409}  # Conflict

            columns = ', '.join([f'"{key}"' for key in user_data.keys()])
            placeholders = ', '.join(['%s'] * len(user_data))
            query = f'INSERT INTO "Users" ({columns}) VALUES ({placeholders}) RETURNING *;'
            
            cur.execute(query, tuple(user_data.values()))
            conn.commit()
            row = cur.fetchone()
            
            if row:
                result_columns = [desc[0] for desc in cur.description]  # Get column names from cursor description
                result = dict(zip(result_columns, row))  # Map column names to row values
                logger.info(f"create_user result: {result}")
                return {"results": result, "status_code": 201}  # Created
                
            logger.info("create_user returned no result")
            return {"error": "Failed to create user", "status_code": 500}
            
        except psycopg2.IntegrityError as e:
            logger.error(f"Integrity error in create_user: {e}")
            conn.rollback()
            return {"error": "Database integrity error. User may already exist.", "status_code": 409}
        except psycopg2.OperationalError as e:
            logger.error(f"Database operational error in create_user: {e}")
            conn.rollback()
            return {"error": "Database connection error", "status_code": 503}
        except Exception as e:
            logger.error(f"An error occurred in create_user: {e}")
            conn.rollback()
            return {"error": f"Failed to create user: {str(e)}", "status_code": 500}
        finally:
            if conn:
                conn.close()
            
    def update_user(self, user_data_input, userId):
        conn = settings.get_db_connection()
        try:
            if conn is None:
                logger.error("Database connection failed")
                return {"error": "Database connection failed", "status_code": 503}
                
            if not userId:
                logger.error("Missing userId for update")
                return {"error": "User ID is required for update", "status_code": 400}

            if not user_data_input or not isinstance(user_data_input, dict):
                logger.error("Invalid user data format")
                return {"error": "User data must be a valid dictionary", "status_code": 400}

            cur = conn.cursor()
            
            # Check if user exists
            cur.execute('SELECT COUNT(*) FROM "Users" WHERE "userId" = %s;', (userId,))
            if cur.fetchone()[0] == 0:
                logger.error(f"User not found for update: {userId}")
                return {"error": f"User with ID {userId} not found", "status_code": 404}

            # Exclude None values from the update query
            user_data_input = {key: value for key, value in user_data_input.items() if value is not None}

            if not user_data_input:
                logger.error("No valid fields provided for update")
                return {"error": "No valid fields provided for update", "status_code": 400}

            # Check if username already exists (if username is being updated)
            if "username" in user_data_input:
                cur.execute('SELECT COUNT(*) FROM "Users" WHERE "username" = %s AND "userId" != %s;', 
                           (user_data_input["username"], userId))
                if cur.fetchone()[0] > 0:
                    logger.error(f"Username already exists: {user_data_input['username']}")
                    return {"error": "Username already exists", "status_code": 409}  # Conflict

            set_clause = ', '.join([f'"{key}" = %s' for key in user_data_input.keys()])
            query = f'UPDATE "Users" SET {set_clause} WHERE "userId" = %s RETURNING *;'
            params = tuple(user_data_input.values()) + (userId,)  # Combine values with userId
            
            cur.execute(query, params)
            conn.commit()
            row = cur.fetchone()

            if row:
                result_columns = [desc[0] for desc in cur.description]
                result = dict(zip(result_columns, row))
                logger.info(f"update_user result: {result}")
                return {"results": result}

            logger.error(f"Update failed for user: {userId}")
            return {"error": "Failed to update user", "status_code": 500}

        except psycopg2.IntegrityError as e:
            logger.error(f"Integrity error in update_user: {e}")
            conn.rollback()
            return {"error": "Database integrity error", "status_code": 409}
        except psycopg2.OperationalError as e:
            logger.error(f"Database operational error in update_user: {e}")
            conn.rollback()
            return {"error": "Database connection error", "status_code": 503}
        except Exception as e:
            logger.error(f"An error occurred in update_user: {e}")
            conn.rollback()
            return {"error": f"Failed to update user: {str(e)}", "status_code": 500}

        finally:
            if conn:
                conn.close()

    def delete_user(self, userId):
        conn = settings.get_db_connection()  
        try:
            if conn is None:
                logger.error("Database connection failed")
                return {"error": "Database connection failed", "status_code": 503}
                
            if not userId:
                logger.error("Missing userId for delete")
                return {"error": "User ID is required for deletion", "status_code": 400}
                
            cur = conn.cursor()
            
            # Check if user exists
            cur.execute('SELECT COUNT(*) FROM "Users" WHERE "userId" = %s;', (userId,))
            if cur.fetchone()[0] == 0:
                logger.error(f"User not found for deletion: {userId}")
                return {"error": f"User with ID {userId} not found", "status_code": 404}
                
            query = 'DELETE FROM "Users" WHERE "userId" = %s;'
            cur.execute(query, (userId,))
            
            if cur.rowcount == 0:
                logger.error(f"No rows affected when deleting user: {userId}")
                return {"error": "Failed to delete user", "status_code": 500}
                
            conn.commit()
            logger.info(f"delete_user result: User with userId {userId} deleted successfully.")
            return {"results": {"message": "User deleted successfully."}}
            
        except psycopg2.ForeignKeyViolation as e:
            logger.error(f"Foreign key violation in delete_user: {e}")
            conn.rollback()
            return {"error": "Cannot delete user because it is referenced by other records", "status_code": 409}
        except psycopg2.OperationalError as e:
            logger.error(f"Database operational error in delete_user: {e}")
            conn.rollback()
            return {"error": "Database connection error", "status_code": 503}
        except Exception as e:
            logger.error(f"An error occurred in delete_user: {e}")
            conn.rollback()  
            return {"error": f"Failed to delete user: {str(e)}", "status_code": 500}
        finally:
            if conn:
                conn.close()
