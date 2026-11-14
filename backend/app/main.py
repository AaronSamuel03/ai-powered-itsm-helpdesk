from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import ping_db
from app.routes import chat, tickets, software, knowledge

app = FastAPI(title="AI-Powered ITSM Helpdesk API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router)
app.include_router(tickets.router)
app.include_router(software.router)
app.include_router(knowledge.router)


@app.get("/api/health")
async def health_check():
    db_ok = await ping_db()
    return {"status": "healthy", "mongodb": db_ok}
