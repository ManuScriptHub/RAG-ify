import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PROJECT_NAME: str = "My FastAPI Project"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./test.db")
    # API_KEY: str = os.getenv("X-API-KEY", "")
    API_KEY: str = "x_and_x"
    # VOYAGE_API_KEY: str = os.getenv("VOYAGE_API_KEY","")
    VOYAGE_API_KEY: str =  "pa-EX4UzuMG41P5EHGTdbSQyCM4LNaqrtkXtCX7gqNWXKe"


settings = Settings()
