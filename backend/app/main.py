import logging
import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.app.config import settings
from backend.app.api.router import api_router

# Configure structured logging (ensuring secrets/PII are excluded)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("home_credit_lap_agent")

app = FastAPI(
    title="Home Credit LAP Voice Agent Qualification Engine",
    description="Deterministic qualification, conversational state management, and voice integration API for Loan Against Property (LAP).",
    version="1.0.0",
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.ENVIRONMENT == "development" else settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    # Mask authorization headers or private query params in logs
    path = request.url.path
    method = request.method
    try:
        response = await call_next(request)
        process_time = (time.time() - start_time) * 1000
        logger.info(f"{method} {path} completed with status {response.status_code} in {process_time:.2f}ms")
        return response
    except Exception as e:
        logger.error(f"Error processing {method} {path}: {str(e)}")
        return JSONResponse(status_code=500, content={"detail": "Internal server error."})


app.include_router(api_router)


@app.get("/")
def root():
    return {
        "service": "Home Credit LAP Voice Agent Backend",
        "docs": "/docs",
        "health": "/api/health",
        "simulator": "/api/simulator/scenarios",
    }
