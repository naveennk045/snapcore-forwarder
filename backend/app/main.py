from fastapi import FastAPI
from app.routers import accounts
from app.database import engine, Base

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Social Media Content Forwarder",
    description="Manage accounts and forward content between social media platforms",
    version="1.0.0"
)

# Include all routers
app.include_router(accounts.router)                          # /accounts

@app.get("/")
def root():
    return {
        "message": "Social Media Content Forwarder API",
        "docs": "/docs",
        "services": {
            "accounts": "/accounts",
            "instagram_to_youtube": "/instagram-to-youtube",
            "youtube_to_instagram": "/youtube-to-instagram"
        }
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}
