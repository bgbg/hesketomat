import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from backend.api.routes import router
from backend.api.projects import router as projects_router
from backend.api.interviews import router as interviews_router
from backend.models.database import create_tables
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),  # Log to console
        logging.FileHandler("backend.log"),  # Log to file
    ],
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Hesketomat API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Add logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000
    logger.info(
        f"Method: {request.method} Path: {request.url.path} "
        f"Status: {response.status_code} Duration: {process_time:.2f}ms"
    )
    return response


# Include routers
app.include_router(router, prefix="/api")
app.include_router(projects_router, prefix="/api", tags=["Projects"])
app.include_router(interviews_router, prefix="/api", tags=["Interviews"])


# Create tables on startup
@app.on_event("startup")
async def startup_event():
    logger.info("Starting up Hesketomat API")
    create_tables()
    logger.info("Database tables created")
