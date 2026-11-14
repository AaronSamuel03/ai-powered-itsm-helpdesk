# AI-Powered ITSM Helpdesk Platform

An end-to-end, AI-driven IT Service Management (ITSM) prototype built with **React.js**, **FastAPI**, **MongoDB Atlas Vector Search**, **Hugging Face open-source LLMs**, and **ServiceNow REST APIs**.

## Key Capabilities
1. **Intelligent Ticket Intake:** Uses an open-source Hugging Face LLM (`Qwen/Qwen2.5-7B-Instruct`) to classify incoming employee issues by category, urgency, and intent before logging structured incidents into ServiceNow.
2. **Auto-Resolution / Self-Heal Agents:** Automatically executes remediation playbooks (VPN session resets, password resets, DNS/SSO cache clears) and closes resolved incidents in ServiceNow.
3. **Knowledge Management Automation:** Converts resolved ServiceNow incident threads into structured Knowledge Base articles and indexes their 384-dimensional embeddings (`all-MiniLM-L6-v2`) in MongoDB Atlas.
4. **Self-Service Portal & AI Chatbot:** Provides a conversational React portal backed by Retrieval-Augmented Generation (RAG) with source citations and live ticket status badges.
5. **Software Provisioning Automation:** Validates employee role entitlements against an enterprise catalog and triggers automated ServiceNow fulfillment tickets.

## Tech Stack
- **Frontend:** React.js (Vite), Axios, Lucide Icons
- **Backend:** Python, FastAPI, Motor (Async MongoDB), HTTPX
- **Database & Vector Store:** MongoDB Atlas & Atlas Vector Search
- **AI & Embeddings:** Hugging Face Inference API (`Qwen2.5-7B-Instruct`) & `sentence-transformers/all-MiniLM-L6-v2`
- **ITSM Integration:** ServiceNow Table REST API

## Local Setup

### 1. Backend (FastAPI)
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env   # Add your MongoDB, Hugging Face, and ServiceNow credentials
python seed.py         # Seed sample KB articles & software catalog
uvicorn app.main:app --reload --port 8000
```

### 2. Frontend (React)
```bash
cd frontend
npm install
npm run dev
```
Open `http://localhost:5173` in your browser.
