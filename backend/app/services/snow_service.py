import httpx
from app.config import settings


def _auth():
    return (settings.SNOW_USER, settings.SNOW_PASSWORD)


async def create_servicenow_incident(short_description: str, description: str, category: str, urgency: str) -> dict:
    url = f"{settings.SNOW_INSTANCE}/api/now/table/incident"
    payload = {
        "short_description": short_description,
        "description": description,
        "category": category.lower(),
        "urgency": urgency,
    }
    async with httpx.AsyncClient(timeout=20.0) as client:
        resp = await client.post(url, auth=_auth(), json=payload, headers={"Accept": "application/json"})
        resp.raise_for_status()
        result = resp.json().get("result", {})
        return {
            "sys_id": result.get("sys_id"),
            "number": result.get("number"),
            "state": result.get("state"),
        }


async def resolve_servicenow_incident(sys_id: str, close_notes: str) -> bool:
    url = f"{settings.SNOW_INSTANCE}/api/now/table/incident/{sys_id}"
    payload = {
        "state": "6",
        "close_code": "Solved (Permanently)",
        "close_notes": close_notes,
    }
    async with httpx.AsyncClient(timeout=20.0) as client:
        resp = await client.patch(url, auth=_auth(), json=payload, headers={"Accept": "application/json"})
        return resp.status_code == 200


async def fetch_resolved_incidents(limit: int = 5) -> list[dict]:
    url = f"{settings.SNOW_INSTANCE}/api/now/table/incident"
    params = {"sysparm_query": "state=6", "sysparm_limit": limit}
    async with httpx.AsyncClient(timeout=20.0) as client:
        resp = await client.get(url, auth=_auth(), params=params, headers={"Accept": "application/json"})
        resp.raise_for_status()
        return resp.json().get("result", [])
