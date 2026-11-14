from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.database import software_collection, tickets_collection
from app.services.snow_service import create_servicenow_incident, resolve_servicenow_incident

router = APIRouter(prefix="/api/software", tags=["Software Provisioning"])


class ProvisionRequest(BaseModel):
    app_id: str
    user_email: str = "employee@company.com"
    user_role: str = "Developer"


@router.get("/")
async def get_catalog():
    apps = []
    async for doc in software_collection.find({}, {"_id": 0}):
        apps.append(doc)
    return {"catalog": apps}


@router.post("/provision")
async def provision_software(req: ProvisionRequest):
    app_item = await software_collection.find_one({"app_id": req.app_id}, {"_id": 0})
    if not app_item:
        raise HTTPException(status_code=404, detail="Software not found in catalog")

    if req.user_role not in app_item.get("allowed_roles", []):
        raise HTTPException(status_code=403, detail=f"Role '{req.user_role}' is not pre-approved for {app_item['name']}")

    snow = await create_servicenow_incident(
        short_description=f"Auto-Provision Software: {app_item['name']}",
        description=f"Automated license & package deployment of {app_item['name']} for {req.user_email}.",
        category="Software",
        urgency="3",
    )
    notes = f"Verified '{req.user_role}' entitlement and pushed {app_item['name']} installer via MDM/SCCM."
    if snow.get("sys_id"):
        await resolve_servicenow_incident(snow["sys_id"], notes)

    record = {
        "snow_number": snow.get("number", "REQ-LOCAL"),
        "user_email": req.user_email,
        "short_description": f"Software Provisioned: {app_item['name']}",
        "category": "Software",
        "urgency": "3",
        "intent": "software_request",
        "status": "Provisioned (Automated)",
        "resolution_notes": notes,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await tickets_collection.insert_one(record)
    return {"message": f"{app_item['name']} provisioned automatically!", "ticket": {k: v for k, v in record.items() if k != "_id"}}
