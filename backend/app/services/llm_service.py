import json
import re
from huggingface_hub import InferenceClient
from sentence_transformers import SentenceTransformer
from app.config import settings

embed_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
hf_client = InferenceClient(model=settings.HF_MODEL, token=settings.HF_TOKEN)


def get_embedding(text: str) -> list[float]:
    return embed_model.encode(text).tolist()


def generate_chat_response(system_prompt: str, user_prompt: str) -> str:
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]
    response = hf_client.chat_completion(messages=messages, max_tokens=500, temperature=0.2)
    return response.choices[0].message.content.strip()


def classify_ticket(user_query: str) -> dict:
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
