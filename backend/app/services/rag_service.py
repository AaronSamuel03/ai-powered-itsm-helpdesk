from app.database import kb_collection
from app.services.llm_service import get_embedding, generate_chat_response


async def search_knowledge_base(query: str, limit: int = 3) -> list[dict]:
    query_vector = get_embedding(query)
    pipeline = [
        {
            "$vectorSearch": {
                "index": "vector_index",
                "path": "embedding",
                "queryVector": query_vector,
                "numCandidates": 20,
                "limit": limit,
            }
        },
        {
            "$project": {
                "_id": 0,
                "title": 1,
                "content": 1,
                "category": 1,
                "score": {"$meta": "vectorSearchScore"},
            }
        },
    ]
    results = []
    async for doc in kb_collection.aggregate(pipeline):
        if doc.get("score", 0) >= 0.65:
            results.append(doc)
    return results


async def answer_with_rag(user_query: str) -> dict:
    docs = await search_knowledge_base(user_query)
    if not docs:
        return {"found": False, "answer": "", "sources": []}

    context = "\n\n".join([f"Title: {d['title']}\n{d['content']}" for d in docs])
    system_prompt = (
        "You are an enterprise IT Helpdesk assistant. Answer the user's question clearly "
        "using ONLY the provided Knowledge Base context. Keep steps concise and actionable."
    )
    user_prompt = f"Knowledge Base Context:\n{context}\n\nEmployee Question: {user_query}"
    answer = generate_chat_response(system_prompt, user_prompt)
    return {
        "found": True,
        "answer": answer,
        "sources": [d["title"] for d in docs],
    }
