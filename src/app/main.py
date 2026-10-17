from fastapi import FastAPI

app = FastAPI(
    title="Footfall Analytics API",
    version="0.1.0",
    description="Retail visitor analytics platform",
)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "healthy"}
