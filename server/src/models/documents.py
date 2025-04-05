from core.db import settings

class DocumentsModel:
    def get_documents(self):
        conn = settings.get_db_connection()  
        try:
            cur = conn.cursor()
            cur.execute('SELECT * FROM "Documents";')
            
            result = cur.fetchall()
            return result
        except Exception as e:
            print(f"An error occurred in get_documents: {e}")
            return []
        finally:
            if conn:
                conn.close()

    def get_document(self, document_id):
        conn = settings.get_db_connection()  
        try:
            cur = conn.cursor()
            query = 'SELECT * FROM "Documents" WHERE "documentId" = %s;'
            cur.execute(query, (document_id,))
            row = cur.fetchone()
            if row:
                columns = [
                    "documentId", "userId", "corpusId", "docType", "docName", 
                    "sourceUrl", "createdAt", "updatedAt", "tags", "rawText"
                ]
                return dict(zip(columns, row))  
            return None 
        except Exception as e:
            print(f"An error occurred in get_document: {e}")
            return None 
        finally:
            if conn:
                conn.close()

    def update_document(self, document_id, updates):
        """
        Updates a document with the given updates dictionary.
        """
        conn = settings.get_db_connection()
        try:
            cur = conn.cursor()
            set_clause = ', '.join([f'"{key}" = %s' for key in updates.keys()])
            query = f'UPDATE "Documents" SET {set_clause} WHERE "documentId" = %s;'
            cur.execute(query, (*updates.values(), document_id))
            conn.commit()
            return cur.rowcount > 0  # Returns True if a row was updated
        except Exception as e:
            print(f"An error occurred in update_document: {e}")
            return False
        finally:
            if conn:
                conn.close()

    def delete_document(self, document_id):
        """
        Deletes a document by its ID.
        """
        conn = settings.get_db_connection()
        try:
            cur = conn.cursor()
            query = 'DELETE FROM "Documents" WHERE "documentId" = %s;'
            cur.execute(query, (document_id,))
            conn.commit()
            return cur.rowcount > 0  # Returns True if a row was deleted
        except Exception as e:
            print(f"An error occurred in delete_document: {e}")
            return False
        finally:
            if conn:
                conn.close()

    def create_document(self, document_data):
        """
        Inserts a new document into the database.
        """
        conn = settings.get_db_connection()
        try:
            cur = conn.cursor()
            columns = ', '.join([f'"{key}"' for key in document_data.keys()])
            placeholders = ', '.join(['%s'] * len(document_data))
            query = f'INSERT INTO "Documents" ({columns}) VALUES ({placeholders}) RETURNING "documentId";'
            cur.execute(query, tuple(document_data.values()))
            conn.commit()
            return cur.fetchone()[0]  # Returns the ID of the newly created document
        except Exception as e:
            print(f"An error occurred in create_document: {e}")
            return None
        finally:
            if conn:
                conn.close()