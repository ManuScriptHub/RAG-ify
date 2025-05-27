from fastapi import FastAPI
from api.routes import router as api_router
from scalar_fastapi import get_scalar_api_reference

app = FastAPI(title="RAG-ify", openapi_url="/openapi.json", debug=False)

app.include_router(api_router, prefix="/api/v1")

router = app.router

@router.get("/scalar", include_in_schema=False)
async def scalar_html():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title=app.title,
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
