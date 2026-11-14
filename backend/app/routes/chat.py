from datetime import datetime, timezone
from fastapi import APIRouter
from pydantic import BaseModel
from app.services.rag_service import answer_with_rag
from app.services.llm_service import classify_ticket
from app.services.agent_service import attempt_self_heal
from app.services.snow_service import create_servicenow_incident, resolve_servicenow_incident
from app.database import tickets_collection

router = APIRouter(prefix="/api/chat", tags=["AI Chatbot"])


class ChatRequest(BaseModel):
    message: str
    user_email: str = "employee@company.com"


@router.post("/")
async def chat_endpoint(req: ChatRequest):
    rag_result = await answer_with_rag(req.message)
    if rag_result["found"]:
        return {
            "type": "rag_answer",
            "reply": rag_result["answer"],
            "sources": rag_result["sources"],
        }

    triage = classify_ticket(req.message)
    heal = attempt_self_heal(triage["intent"])

    snow_ticket = await create_servicenow_incident(
        short_description=triage["short_description"],
        description=req.message,
        category=triage["category"],
        urgency=triage["urgency"],
    )

    status = "Open"
    if heal["auto_resolved"] and snow_ticket.get("sys_id"):
        await resolve_servicenow_incident(snow_ticket["sys_id"], heal["remediation_steps"])
        status = "Resolved (Self-Healed)"

    ticket_doc = {
        "snow_number": snow_ticket.get("number", "INC-LOCAL"),
        "snow_sys_id": snow_ticket.get("sys_id", ""),
        "user_email": req.user_email,
        "short_description": triage["short_description"],
        "category": triage["category"],
        "urgency": triage["urgency"],
        "intent": triage["intent"],
        "status": status,
        "resolution_notes": heal["remediation_steps"],
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await tickets_collection.insert_one(ticket_doc)

    reply = (
        f"I created ServiceNow ticket **{ticket_doc['snow_number']}** "
        f"(Category: {triage['category']}, Urgency: {triage['urgency']}).\n\n"
        f"**Agent Action:** {heal['remediation_steps']}"
    )
    return {
        "type": "ticket_action",
        "reply": reply,
        "ticket": {k: v for k, v in ticket_doc.items() if k != "_id"},
    }
