import json
import re
import httpx
from sentence_transformers import SentenceTransformer
from app.config import settings

embed_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")


def get_embedding(text: str) -> list[float]:
    return embed_model.encode(text).tolist()


def generate_chat_response(system_prompt: str, user_prompt: str) -> str:
    url = "https://huggingface.co"
    headers = {
        "Authorization": f"Bearer {settings.HF_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": settings.HF_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "max_tokens": 500,
        "temperature": 0.2,
    }
    try:
        with httpx.Client(timeout=25.0) as client:
            resp = client.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"].strip()
    except Exception:
        if "Knowledge Base Context:" in user_prompt:
            context_part = user_prompt.split("Employee Question:")[0].replace("Knowledge Base Context:", "").strip()
            return f"Here are the troubleshooting steps from our Knowledge Base:\n\n{context_part}"
        return "Issue analyzed and routed for automated ITSM processing."


def classify_ticket(user_query: str) -> dict:
    q = user_query.lower()
    if "vpn" in q:
        return {"short_description": user_query[:80], "category": "Network", "urgency": "2", "intent": "vpn_reset"}
    if "password" in q or "locked" in q:
        return {"short_description": user_query[:80], "category": "Access", "urgency": "2", "intent": "password_reset"}
    if "cache" in q or "browser" in q or "slow" in q:
        return {"short_description": user_query[:80], "category": "Software", "urgency": "3", "intent": "clear_cache"}
    if any(w in q for w in ["monitor", "screen", "display", "laptop", "dock", "keyboard", "mouse", "hardware"]):
        return {"short_description": user_query[:80], "category": "Hardware", "urgency": "2", "intent": "general_support"}


    system_prompt = (
        "You are an ITSM triage AI. Extract structured ticket fields from the user issue. "
        "Respond ONLY with valid JSON containing keys: "
        '{"short_description": str, "category": "Network|Software|Hardware|Access", '
        '"urgency": "1|2|3", "intent": "vpn_reset|password_reset|clear_cache|software_request|general_support"}'
    )
    raw = generate_chat_response(system_prompt, user_query)
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass
    return {
        "short_description": user_query[:80],
        "category": "Software",
        "urgency": "2",
        "intent": "general_support",
    }
