import asyncio
from datetime import datetime, timezone
from app.database import kb_collection, software_collection
from app.services.llm_service import get_embedding

KB_ARTICLES = [
    {
        "title": "How to Connect to Corporate VPN (GlobalProtect)",
        "category": "Network",
        "content": (
            "1. Open GlobalProtect from the system tray.\n"
            "2. Enter portal address: ://company.com and click Connect.\n"
            "3. Sign in with your corporate SSO email and approve the MFA push notification.\n"
            "4. If connection hangs, click Settings -> Refresh Connection."
        ),
    },
    {
        "title": "Configure Company Email on Mobile (Outlook)",
        "category": "Access",
        "content": (
            "1. Install Microsoft Outlook from the App Store or Google Play.\n"
            "2. Tap Add Account and enter your @company.com email.\n"
            "3. Complete Microsoft Authenticator verification.\n"
            "4. Allow device policy sync to access mail and calendar."
        ),
    },
    {
        "title": "Fix Slow Wi-Fi or DNS Resolution Issues on Windows",
        "category": "Network",
        "content": (
            "1. Disconnect from Corp-Guest and connect to Corp-Secure Wi-Fi.\n"
            "2. Open Command Prompt and run: ipconfig /flushdns.\n"
            "3. Toggle Wi-Fi off and back on, then re-test internal intranet access."
        ),
    },
    {
        "title": "Requesting Admin Rights or Software Installation",
        "category": "Software",
        "content": (
            "Standard developer tools like VS Code, Docker Desktop, and Slack are pre-approved "
            "for Engineering roles and can be auto-provisioned instantly from the Self-Service Software Catalog."
        ),
    },
]

SOFTWARE_ITEMS = [
    {
        "app_id": "vscode",
        "name": "Visual Studio Code",
        "vendor": "Microsoft",
        "description": "Lightweight source code editor with Git and Python/JS extensions.",
        "allowed_roles": ["Developer", "Data Scientist", "IT Admin"],
    },
    {
        "app_id": "docker",
        "name": "Docker Desktop",
        "vendor": "Docker Inc.",
        "description": "Container runtime environment for local microservices development.",
        "allowed_roles": ["Developer", "IT Admin"],
    },
    {
        "app_id": "slack",
        "name": "Slack Enterprise",
        "vendor": "Salesforce",
        "description": "Team messaging, incident war-rooms, and IT bot notifications.",
        "allowed_roles": ["Developer", "Data Scientist", "IT Admin", "HR", "Finance"],
    },
    {
        "app_id": "figma",
        "name": "Figma Professional",
        "vendor": "Figma",
        "description": "Collaborative UI/UX design and prototyping workspace.",
        "allowed_roles": ["Developer", "Designer", "Product Manager"],
    },
]


async def seed():
    print("Seeding Knowledge Base with vector embeddings...")
    await kb_collection.delete_many({})
    for item in KB_ARTICLES:
        doc = {
            **item,
            "embedding": get_embedding(f"{item['title']}\n{item['content']}"),
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        await kb_collection.insert_one(doc)

    print("Seeding Software Catalog...")
    await software_collection.delete_many({})
    await software_collection.insert_many(SOFTWARE_ITEMS)
    print("Database seeded successfully!")


if __name__ == "__main__":
    asyncio.run(seed())
