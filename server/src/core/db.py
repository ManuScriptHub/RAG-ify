import os
import psycopg2
from psycopg2.extras import DictCursor
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # DB_NAME: str = os.getenv("DB_NAME")
    # DB_HOST: str = os.getenv("DB_HOST")
    # DB_PASS: str = os.getenv("DB_PASS")
    # DB_PORT: str = os.getenv("DB_PORT")
    # DB_USER: str = os.getenv("DB_USER")
# DB_HOST=localhost
# DB_PORT=5432
# DB_NAME=RAG-ify
# DB_USER=postgres
# DB_PASS=radhe
    
    
    DB_NAME: str = "RAG-ify"
    DB_HOST: str = "localhost"
    DB_PASS: str = "radhe"
    DB_PORT: str = 5432
    DB_USER: str = "postgres"
    

    def get_db_connection(self):
        try:
            conn = psycopg2.connect(
                host=self.DB_HOST,
                database=self.DB_NAME,
                user=self.DB_USER,
                password=self.DB_PASS,
                port=self.DB_PORT,
                cursor_factory=DictCursor
            )
            return conn
        except Exception as e:
            print("Failed to connect:", e)
            return None


settings = Settings()
