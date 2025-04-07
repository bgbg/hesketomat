from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# from .api.routes import router
# from .models.database import create_tables
from hesketomat.backend.api.routes import router
from hesketomat.backend.models.database import create_tables

app = FastAPI(title="Hesketomat API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(router, prefix="/api")

# Create tables on startup
@app.on_event("startup")
async def startup_event():
    create_tables()


