from datetime import datetime, timezone
from fastapi import APIRouter
from app.database import kb_collection
from app.services.llm_service import get_embedding, generate_chat_response
from app.services.snow_service import fetch_resolved_incidents

router = APIRouter(prefix="/api/knowledge", tags=["Knowledge Management"])


@router.get("/")
async def list_articles():
    articles = []
    async for doc in kb_collection.find({}, {"_id": 0, "embedding": 0}):
        articles.append(doc)
    return {"articles": articles}


@router.post("/generate-from-tickets")
async def generate_kb_from_servicenow():
    resolved = await fetch_resolved_incidents(limit=3)
    created_articles = []

    for inc in resolved:
        title = inc.get("short_description", "Resolved IT Issue")
        exists = await kb_collection.find_one({"title": title})
        if exists:
            continue

        raw_notes = f"Issue: {title}\nDescription: {inc.get('description', '')}\nResolution: {inc.get('close_notes', '')}"
        summary = generate_chat_response(
            "Convert this resolved IT ticket into a clean, reusable Knowledge Base article with Problem, Cause, and Resolution steps.",
            raw_notes,
        )
        article = {
            "title": title,
            "category": inc.get("category", "General").capitalize(),
            "content": summary,
            "embedding": get_embedding(f"{title}\n{summary}"),
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        await kb_collection.insert_one(article)
        created_articles.append({"title": title, "category": article["category"]})

    return {"generated_count": len(created_articles), "articles": created_articles}
