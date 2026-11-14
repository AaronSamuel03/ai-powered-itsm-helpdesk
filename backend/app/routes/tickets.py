from datetime import datetime, timezone
from fastapi import APIRouter
from pydantic import BaseModel
from app.database import tickets_collection
from app.services.llm_service import classify_ticket
from app.services.snow_service import create_servicenow_incident

router = APIRouter(prefix="/api/tickets", tags=["Tickets"])


class TicketCreate(BaseModel):
    description: str
    user_email: str = "employee@company.com"


@router.get("/")
async def list_tickets():
    tickets = []
    async for doc in tickets_collection.find({}, {"_id": 0}).sort("created_at", -1):
        tickets.append(doc)
    return {"tickets": tickets}


@router.post("/")
async def create_ticket(req: TicketCreate):
    triage = classify_ticket(req.description)
    snow = await create_servicenow_incident(
        short_description=triage["short_description"],
        description=req.description,
        category=triage["category"],
        urgency=triage["urgency"],
    )
    doc = {
        "snow_number": snow.get("number", "INC-LOCAL"),
        "snow_sys_id": snow.get("sys_id", ""),
        "user_email": req.user_email,
        "short_description": triage["short_description"],
        "category": triage["category"],
        "urgency": triage["urgency"],
        "intent": triage["intent"],
        "status": "Open",
        "resolution_notes": "Awaiting Tier-2 assignment",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await tickets_collection.insert_one(doc)
    return {k: v for k, v in doc.items() if k != "_id"}
