from core.db import settings

class DocumentChunkModel:
    def get_document_chunks(self):
        conn = settings.get_db_connection()  
        try:
            cur = conn.cursor()
            cur.execute('SELECT * FROM "DocumentChunks";')
            
            result = cur.fetchall()
            return result
        except Exception as e:
            print(f"An error occurred in get_documents: {e}")
            return []
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
                columns = [
                    "chunkId", "documentId", "chunkIndex", "chunkText", 
                    "metaData", "createdAt", "updatedAt"
                ]
                return dict(zip(columns, row))  
            return None 
        except Exception as e:
            print(f"An error occurred in get_document: {e}")
            return None 
        finally:
            if conn:
                conn.close()

    def create_document_chunk(self, chunk_data):
        """
        Creates a new document chunk and returns its ID.
        """
        conn = settings.get_db_connection()
        try:
            cur = conn.cursor()
            query = '''INSERT INTO "DocumentChunks" ("documentId", "chunkIndex", "chunkText", "metaData") 
                       VALUES (%s, %s, %s, %s) RETURNING "chunkId";'''
            cur.execute(query, (chunk_data['documentId'], chunk_data['chunkIndex'], chunk_data['chunkText'], chunk_data['metaData']))
            chunk_id = cur.fetchone()[0]
            conn.commit()
            return chunk_id
        except Exception as e:
            print(f"An error occurred in create_document_chunk: {e}")
            return None
        finally:
            if conn:
                conn.close()

    

    def update_document_chunk(self, chunk_id, updates):
        """
        Updates a document with the given updates dictionary.
        """
        conn = settings.get_db_connection()
        try:
            cur = conn.cursor()
            set_clause = ', '.join([f'"{key}" = %s' for key in updates.keys()])
            query = f'''UPDATE "DocumentChunks" SET {set_clause} WHERE "chunkId" = %s;'''
            cur.execute(query, (*updates.values(), chunk_id))
            conn.commit()
            return cur.rowcount > 0  # Returns True if a row was updated
        except Exception as e:
            print(f"An error occurred in update_document: {e}")
            return False
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
            WHERE "embeddingData" <=> %s::vector < 0.50
            ORDER BY "embeddingData" <=> %s::vector
            LIMIT %s;
        '''

            cur.execute(query, (question_embedding, question_embedding, top_k))
            rows = cur.fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            print(f"An error occurred in search_document_chunk: {e}")
            return False
        finally:
            if conn:
                conn.close()
        