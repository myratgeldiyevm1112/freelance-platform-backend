from fastapi import FastAPI

app = FastAPI(
    title="Freelance Platform API",
    description="A clean freelance marketplace REST API",
    version="0.1.0",
)


@app.get("/health")
async def health_check():
    return {"status": "ok"}