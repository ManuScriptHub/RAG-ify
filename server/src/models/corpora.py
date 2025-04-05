from core.db import settings

class CorporaModel:
    def get_corpuses(self):
        conn = settings.get_db_connection()  
        try:
            cur = conn.cursor()
            cur.execute('SELECT * FROM "Corpora";')
            
            result = cur.fetchall()
            return result
        except Exception as e:
            print(f"An error occurred in get_corpuses: {e}")
            return []
        finally:
            if conn:
                conn.close()

    def get_corpus(self, corpus_id):
        conn = settings.get_db_connection()  
        try:
            cur = conn.cursor()
            query = """SELECT * FROM "Corpora" WHERE "corpusId" = %s;"""
            print(query)
            cur.execute(query, (corpus_id,))
            row = cur.fetchone()
            if row:
                columns = ["userId",  "corpusKey", "corpusId", "createdAt", "updatedAt"]
                return dict(zip(columns, row))  
            return None 
        except Exception as e:
            print(f"An error occurred in get_corpus: {e}")
            return None 
        finally:
            if conn:
                conn.close()

    def create_corpus(self, user_id, corpus_key):
        conn = settings.get_db_connection()  
        try:
            cur = conn.cursor()
            query = """
                INSERT INTO "Corpora" ("userId", "corpusKey")
                VALUES (%s, %s)
                RETURNING "userId", "corpusKey", "corpusId", "createdAt", "updatedAt";
            """
            cur.execute(query, (user_id, corpus_key))
            row = cur.fetchone()
            conn.commit()
            if row:
                columns = ["userId",  "corpusKey", "corpusId", "createdAt", "updatedAt"]
                return dict(zip(columns, row))  
            return None 
        except Exception as e:
            print(f"An error occurred in create_corpus: {e}")
            conn.rollback()  
            return {"error": str(e)}
        finally:
            if conn:
                conn.close()

    def update_corpus(self, user_id, corpus_key):
        conn = settings.get_db_connection()
        try:
            cur = conn.cursor()
            query = '''
            UPDATE "Corpora"
            SET "corpusKey" = %s
            WHERE "userId" = %s
            RETURNING "corpusId", "corpusKey", "userId", "createdAt", "updatedAt";
            '''
            cur.execute(query, (corpus_key, user_id))
            row = cur.fetchone()
            conn.commit()

            if row:
                columns = ["corpusId", "corpusKey", "userId", "createdAt", "updatedAt"]
                return dict(zip(columns, row))
            return None
        except Exception as e:
            conn.rollback()
            return {"error": str(e)}
        finally:
            conn.close()

    def delete_corpus(self, corpus_id):
        conn = settings.get_db_connection()  
        try:
            cur = conn.cursor()
            query = """DELETE FROM "Corpora" WHERE "corpusId" = %s;"""
            cur.execute(query, (corpus_id,))
            conn.commit()
            return {"message": f"Corpus with corpus_id {corpus_id} deleted successfully."}
        except Exception as e:
            conn.rollback()  
            return {"error": str(e)}
        finally:
            if conn:
                conn.close()
