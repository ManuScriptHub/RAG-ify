from fastapi import FastAPI
from api.routes import router as api_router

app = FastAPI(title="🚀 My FastAPI Project")

app.include_router(api_router, prefix="/api/v1")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)