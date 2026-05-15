from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import auth, tasks, ai, analytics

app = FastAPI(
    title="SmartBacklog API",
    description="Assistant IA Management Backend",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(tasks.router)
app.include_router(ai.router)
app.include_router(analytics.router)

@app.get("/")
def root():
    return {"app": "SmartBacklog API", "version": "2.0.0", "status": "running", "docs": "/docs"}

@app.get("/health")
def health():
    return {"status": "ok"}
