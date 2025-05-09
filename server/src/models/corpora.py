from core.db import settings
import logging
import psycopg2
import json

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class CorporaModel:
    def get_corpuses(self, where_conditions=None):
        conn = settings.get_db_connection()  
        try:
            if conn is None:
                logger.error("Database connection failed")
                return {"error": "Database connection failed", "status_code": 503}
                
            cur = conn.cursor()
            
            query = 'SELECT * FROM "Corpora"'
            params = []
            
            # Add WHERE clause if conditions are provided
            if where_conditions:
                if not isinstance(where_conditions, dict):
                    logger.error(f"Invalid where_conditions format: {where_conditions}")
                    return {"error": "Where conditions must be a dictionary", "status_code": 400}
                
                where_clauses = []
                for key, value in where_conditions.items():
                    # Ensure the column name is valid to prevent SQL injection
                    if key in ["corpusId", "userId", "corpusKey"]:
                        where_clauses.append(f'"{key}" = %s')
                        params.append(value)
                    else:
                        logger.warning(f"Ignoring invalid column name in where condition: {key}")
                
                if where_clauses:
                    query += " WHERE " + " AND ".join(where_clauses)
            
            query += ";"
            logger.info(f"Executing query: {query} with params: {params}")
            
            cur.execute(query, params)
            rows = cur.fetchall()
            columns = [desc[0] for desc in cur.description]  # Extract column names
            result = [dict(zip(columns, row)) for row in rows]  # Convert rows to dictionaries
            logger.info(f"get_corpuses result: {len(result)} records")  
            return {"results": result}  
        
        except psycopg2.OperationalError as e:
            logger.error(f"Database operational error in get_corpuses: {e}")
            return {"error": "Database connection error", "status_code": 503}
        except psycopg2.ProgrammingError as e:
            logger.error(f"SQL syntax error in get_corpuses: {e}")
            return {"error": "Invalid SQL query", "status_code": 500}
        except Exception as e:
            logger.error(f"An error occurred in get_corpuses: {e}")
            return {"error": f"Failed to retrieve corpora: {str(e)}", "status_code": 500}
        finally:
            if conn:
                conn.close()

    def get_corpus(self, corpusId):
        conn = settings.get_db_connection()  
        try:
            if conn is None:
                logger.error("Database connection failed")
                return {"error": "Database connection failed", "status_code": 503}
                
            if not corpusId:
                logger.error("Missing corpusId parameter")
                return {"error": "Corpus ID is required", "status_code": 400}
                
            cur = conn.cursor()
            query = """SELECT * FROM "Corpora" WHERE "corpusId" = %s;"""
            logger.info(f"Executing query: {query} with params: {corpusId}")
            
            cur.execute(query, (corpusId,))
            row = cur.fetchone()
            
            if row:
                columns = [desc[0] for desc in cur.description]  # Get column names from cursor description
                result = dict(zip(columns, row))
                logger.info(f"get_corpus result: {result}")  
                return {"results": result}
                
            logger.info(f"No corpus found for corpusId {corpusId}")
            return {"error": f"Corpus with ID {corpusId} not found", "status_code": 404}
            
        except psycopg2.OperationalError as e:
            logger.error(f"Database operational error in get_corpus: {e}")
            return {"error": "Database connection error", "status_code": 503}
        except psycopg2.ProgrammingError as e:
            logger.error(f"SQL syntax error in get_corpus: {e}")
            return {"error": "Invalid SQL query", "status_code": 500}
        except Exception as e:
            logger.error(f"An error occurred in get_corpus: {e}")
            return {"error": f"Failed to retrieve corpus: {str(e)}", "status_code": 500}
        finally:
            if conn:
                conn.close()

    def create_corpus(self, corpus_data_input):
        conn = settings.get_db_connection()  
        try:
            if conn is None:
                logger.error("Database connection failed")
                return {"error": "Database connection failed", "status_code": 503}
                
            if not corpus_data_input or not isinstance(corpus_data_input, dict):
                logger.error("Invalid corpus data format")
                return {"error": "Corpus data must be a valid dictionary", "status_code": 400}
                
            if "userId" not in corpus_data_input or not corpus_data_input["userId"]:
                logger.error("Missing required field: userId")
                return {"error": "User ID is required", "status_code": 400}
                
            if "corpusKey" not in corpus_data_input or not corpus_data_input["corpusKey"]:
                logger.error("Missing required field: corpusKey")
                return {"error": "Corpus key is required", "status_code": 400}
                
            cur = conn.cursor()

            # Check if corpus key already exists for this user
            cur.execute('SELECT COUNT(*) FROM "Corpora" WHERE "userId" = %s AND "corpusKey" = %s;', 
                       (corpus_data_input["userId"], corpus_data_input["corpusKey"]))
            if cur.fetchone()[0] > 0:
                logger.error(f"Corpus key already exists for this user: {corpus_data_input['corpusKey']}")
                return {"error": "Corpus key already exists for this user", "status_code": 409}  # Conflict

            columns = ', '.join([f'"{key}"' for key in corpus_data_input.keys()])
            placeholders = ', '.join(['%s'] * len(corpus_data_input))
            query = f'INSERT INTO "Corpora" ({columns}) VALUES ({placeholders}) RETURNING *;'
            
            logger.info(f"Executing query: {query} with values: {tuple(corpus_data_input.values())}")
            cur.execute(query, tuple(corpus_data_input.values()))
            row = cur.fetchone()
            conn.commit()
            
            if row:
                result_columns = [desc[0] for desc in cur.description]  # Get column names from cursor description
                result = dict(zip(result_columns, row))  # Map column names to row values
                logger.info(f"create_corpus result: {result}")  
                return {"results": result, "status_code": 201}  # Created
                
            logger.info("create_corpus returned no result")
            return {"error": "Failed to create corpus", "status_code": 500}
            
        except psycopg2.IntegrityError as e:
            logger.error(f"Integrity error in create_corpus: {e}")
            conn.rollback()
            return {"error": "Database integrity error. Corpus may already exist.", "status_code": 409}
        except psycopg2.OperationalError as e:
            logger.error(f"Database operational error in create_corpus: {e}")
            conn.rollback()
            return {"error": "Database connection error", "status_code": 503}
        except Exception as e:
            logger.error(f"An error occurred in create_corpus: {e}")
            conn.rollback()  
            return {"error": f"Failed to create corpus: {str(e)}", "status_code": 500}
        finally:
            if conn:
                conn.close()

    def update_corpus(self, corpus_data_input, corpusId):
        conn = settings.get_db_connection()
        try:
            if conn is None:
                logger.error("Database connection failed")
                return {"error": "Database connection failed", "status_code": 503}
                
            if not corpusId:
                logger.error("Missing corpusId for update")
                return {"error": "Corpus ID is required for update", "status_code": 400}

            if not corpus_data_input or not isinstance(corpus_data_input, dict):
                logger.error("Invalid corpus data format")
                return {"error": "Corpus data must be a valid dictionary", "status_code": 400}

            cur = conn.cursor()
            
            # Check if corpus exists
            cur.execute('SELECT COUNT(*) FROM "Corpora" WHERE "corpusId" = %s;', (corpusId,))
            if cur.fetchone()[0] == 0:
                logger.error(f"Corpus not found for update: {corpusId}")
                return {"error": f"Corpus with ID {corpusId} not found", "status_code": 404}

            # Check if corpus key already exists for this user (if corpusKey is being updated)
            if "corpusKey" in corpus_data_input and "userId" in corpus_data_input:
                cur.execute('SELECT COUNT(*) FROM "Corpora" WHERE "userId" = %s AND "corpusKey" = %s AND "corpusId" != %s;', 
                           (corpus_data_input["userId"], corpus_data_input["corpusKey"], corpusId))
                if cur.fetchone()[0] > 0:
                    logger.error(f"Corpus key already exists for this user: {corpus_data_input['corpusKey']}")
                    return {"error": "Corpus key already exists for this user", "status_code": 409}

            set_clause = ', '.join([f'"{key}" = %s' for key in corpus_data_input.keys()])
            query = f'UPDATE "Corpora" SET {set_clause} WHERE "corpusId" = %s RETURNING *;'
            params = tuple(corpus_data_input.values()) + (corpusId,)  # Combine values with corpusId
            
            logger.info(f"Executing query: {query} with params: {params}")
            cur.execute(query, params)
            conn.commit()
            row = cur.fetchone()

            if row:
                result_columns = [desc[0] for desc in cur.description]
                result = dict(zip(result_columns, row))
                logger.info(f"update_corpus result: {result}")
                return {"results": result}

            logger.error(f"Update failed for corpus: {corpusId}")
            return {"error": "Failed to update corpus", "status_code": 500}

        except psycopg2.IntegrityError as e:
            logger.error(f"Integrity error in update_corpus: {e}")
            conn.rollback()
            return {"error": "Database integrity error", "status_code": 409}
        except psycopg2.OperationalError as e:
            logger.error(f"Database operational error in update_corpus: {e}")
            conn.rollback()
            return {"error": "Database connection error", "status_code": 503}
        except Exception as e:
            logger.error(f"An error occurred in update_corpus: {e}")
            conn.rollback()
            return {"error": f"Failed to update corpus: {str(e)}", "status_code": 500}

        finally:
            if conn:
                conn.close()

    def delete_corpus(self, corpusId):
        conn = settings.get_db_connection()  
        try:
            if conn is None:
                logger.error("Database connection failed")
                return {"error": "Database connection failed", "status_code": 503}
                
            if not corpusId:
                logger.error("Missing corpusId for delete")
                return {"error": "Corpus ID is required for deletion", "status_code": 400}
                
            cur = conn.cursor()
            
            # Check if corpus exists
            cur.execute('SELECT COUNT(*) FROM "Corpora" WHERE "corpusId" = %s;', (corpusId,))
            if cur.fetchone()[0] == 0:
                logger.error(f"Corpus not found for deletion: {corpusId}")
                return {"error": f"Corpus with ID {corpusId} not found", "status_code": 404}
                
            # Check if there are documents associated with this corpus
            cur.execute('SELECT COUNT(*) FROM "Documents" WHERE "corpusId" = %s;', (corpusId,))
            doc_count = cur.fetchone()[0]
            if doc_count > 0:
                logger.warning(f"Corpus {corpusId} has {doc_count} associated documents that will be orphaned")
                # You could choose to return an error here instead of proceeding
                
            query = """DELETE FROM "Corpora" WHERE "corpusId" = %s;"""
            cur.execute(query, (corpusId,))
            
            if cur.rowcount == 0:
                logger.error(f"No rows affected when deleting corpus: {corpusId}")
                return {"error": "Failed to delete corpus", "status_code": 500}
                
            conn.commit()
            message = {"message": f"Corpus with corpusId {corpusId} deleted successfully."}
            logger.info(f"delete_corpus result: {message}") 
            return {"results": message}  
            
        except psycopg2.ForeignKeyViolation as e:
            logger.error(f"Foreign key violation in delete_corpus: {e}")
            conn.rollback()
            return {"error": "Cannot delete corpus because it is referenced by other records", "status_code": 409}
        except psycopg2.OperationalError as e:
            logger.error(f"Database operational error in delete_corpus: {e}")
            conn.rollback()
            return {"error": "Database connection error", "status_code": 503}
        except Exception as e:
            logger.error(f"An error occurred in delete_corpus: {e}")  
            conn.rollback()  
            return {"error": f"Failed to delete corpus: {str(e)}", "status_code": 500}
        finally:
            if conn:
                conn.close()
