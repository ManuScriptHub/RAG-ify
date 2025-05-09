from core.db import settings
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class DocumentChunkModel:
    def get_document_chunks(self, where_conditions=None):
        conn = settings.get_db_connection()  
        try:
            cur = conn.cursor()
            
            query = 'SELECT * FROM "DocumentChunks"'
            params = []
            
            # Add WHERE clause if conditions are provided
            if where_conditions and isinstance(where_conditions, dict) and where_conditions:
                where_clauses = []
                for key, value in where_conditions.items():
                    # Ensure the column name is valid to prevent SQL injection
                    if key in ["chunkId", "documentId", "chunkIndex", "chunkText", "metaData"]:
                        where_clauses.append(f'"{key}" = %s')
                        params.append(value)
                
                if where_clauses:
                    query += " WHERE " + " AND ".join(where_clauses)
            
            query += ";"
            logger.info(f"Executing query: {query} with params: {params}")
            
            cur.execute(query, params)
            rows = cur.fetchall()
            logger.info(f"get_document_chunks result: {len(rows)} records")
            
            # Format the response to match other endpoints
            formatted_results = []
            if rows:
                columns = [desc[0] for desc in cur.description]  # Extract column names
                for row in rows:
                    formatted_results.append(dict(zip(columns, row)))  # Convert each row to dictionary
            
            return {"results": formatted_results}
        except Exception as e:
            logger.error(f"An error occurred in get_document_chunks: {e}")
            return {"results": [], "error": str(e)}
        finally:
            if conn:
                conn.close()

    def get_document_chunk(self, chunk_id):
        conn = settings.get_db_connection()  
        try:
            cur = conn.cursor()
            query = 'SELECT * FROM "DocumentChunks" WHERE "chunkId" = %s;'
            cur.execute(query, (chunk_id,))
            row = cur.fetchone()
            if row:
                columns = [desc[0] for desc in cur.description]  # Extract column names
                result = dict(zip(columns, row))  # Convert row to dictionary
                return {"results": result}  
            return {"results": None} 
        except Exception as e:
            logger.error(f"An error occurred in get_document_chunk: {e}")
            return {"results": {"error": str(e)}} 
        finally:
            if conn:
                conn.close()

    def create_document_chunk(self, chunk_input_data):
        """
        Creates a new document chunk and returns the created chunk.
        """
        conn = settings.get_db_connection()
        try:
            cur = conn.cursor()
            columns = ', '.join([f'"{key}"' for key in chunk_input_data.keys()])
            placeholders = ', '.join(['%s'] * len(chunk_input_data))
            query = f'INSERT INTO "DocumentChunks" ({columns}) VALUES ({placeholders}) RETURNING *;'
            cur.execute(query, tuple(chunk_input_data.values()))
            row = cur.fetchone()
            conn.commit()
            if row:
                columns = [desc[0] for desc in cur.description]  # Extract column names
                result = dict(zip(columns, row))  # Convert row to dictionary
                logger.info(f"create_document_chunk result: {result}")
                return {"results": result}  
            return {"results": None}  
        except Exception as e:
            logger.error(f"An error occurred in create_document_chunk: {e}")
            conn.rollback()
            return {"results": {"error": str(e)}}  
        finally:
            if conn:
                conn.close()

    

    def update_document_chunk(self, chunk_id, chunk_input_data):
        """
        Updates a document chunk with the given updates dictionary.
        """
        conn = settings.get_db_connection()
        try:
            cur = conn.cursor()

            if not chunk_id:
                return {"error": "Missing chunk_id for update."}

            set_clause = ', '.join([f'"{key}" = %s' for key in chunk_input_data.keys()])
            query = f'UPDATE "DocumentChunks" SET {set_clause} WHERE "chunkId" = %s RETURNING *;'
            params = tuple(chunk_input_data.values()) + (chunk_id,)  
            cur.execute(query, params)
            conn.commit()  
            row = cur.fetchone()

            if row:
                result_columns = [desc[0] for desc in cur.description]
                result = dict(zip(result_columns, row))
                logger.info(f"update_document_chunk result: {result}")
                return {"results": result} 

            return {"results": None} 

        except Exception as e:
            logger.error(f"An error occurred in update_document_chunk: {e}")
            conn.rollback() 
            return {"results": {"error": str(e)}} 

        finally:
            if conn:
                conn.close()


    def delete_document_chunk(self, chunk_id):
        """
        Deletes a document chunk by its ID.
        """
        conn = settings.get_db_connection()
        try:
            cur = conn.cursor()
            query = 'DELETE FROM "DocumentChunks" WHERE "chunkId" = %s;'
            cur.execute(query, (chunk_id,))
            conn.commit()
            return cur.rowcount > 0  # Returns True if a row was deleted
        except Exception as e:
            print(f"An error occurred in delete_document: {e}")
            return False
        finally:
            if conn:
                conn.close()    

    def search_document_chunk(self, question_embedding, top_k):
        conn = settings.get_db_connection()
        try:
            cur = conn.cursor()
            query = '''
            SELECT * FROM "DocumentChunks"
            WHERE "embeddingData" <=> %s::vector < 1
            ORDER BY "embeddingData" <=> %s::vector
            LIMIT %s;
        '''

            cur.execute(query, (question_embedding, question_embedding, top_k))
            rows = cur.fetchall()
            print("success:",rows)
            result = []
            if rows:
                columns = [desc[0] for desc in cur.description]  # Extract column names
                for row in rows:
                    result.append(dict(zip(columns, row)))  # Convert each row to dictionary
            return result
        except Exception as e:
            print(f"An error occurred in search_document_chunk: {e}")
            return {"results": "no data found"}
        finally:
            if conn:
                conn.close()
