from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.config import settings
from .api import auth, pilots, events, currency, training, scheduler, calendar

app = FastAPI(title="Squadron Scheduler API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(pilots.router)
app.include_router(events.router)
app.include_router(currency.router)
app.include_router(training.router)
app.include_router(scheduler.router)
app.include_router(calendar.router)


@app.get("/")
def root():
    return {"message": "Squadron Scheduler API", "version": "1.0.0"}


@app.get("/api/health")
def health_check():
    return {"status": "healthy"}
