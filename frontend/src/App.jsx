import { useState, useEffect } from "react";
import axios from "axios";
import { Bot, Ticket, Package, BookOpen, Send, Sparkles, RefreshCw } from "lucide-react";

const API = "http://localhost:8000/api";

export default function App() {
  const [tab, setTab] = useState("chat");
  const [messages, setMessages] = useState([
    {
      sender: "bot",
      text: "Hello! I am your AI ITSM Assistant. Ask me any IT troubleshooting question, or describe an issue (like VPN lockouts or password resets) for instant auto-resolution and ServiceNow ticket tracking.",
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const [tickets, setTickets] = useState([]);
  const [ticketDesc, setTicketDesc] = useState("");
  const [catalog, setCatalog] = useState([]);
  const [role, setRole] = useState("Developer");
  const [articles, setArticles] = useState([]);
  const [statusMsg, setStatusMsg] = useState("");

  useEffect(() => {
    if (tab === "tickets") fetchTickets();
    if (tab === "software") fetchCatalog();
    if (tab === "knowledge") fetchKnowledge();
  }, [tab]);

  const fetchTickets = async () => {
    const res = await axios.get(`${API}/tickets/`);
    setTickets(res.data.tickets || []);
  };

  const fetchCatalog = async () => {
    const res = await axios.get(`${API}/software/`);
    setCatalog(res.data.catalog || []);
  };

  const fetchKnowledge = async () => {
    const res = await axios.get(`${API}/knowledge/`);
    setArticles(res.data.articles || []);
  };

  const sendChat = async (e) => {
    e.preventDefault();
    if (!input.trim() || loading) return;
    const userText = input;
    setMessages((prev) => [...prev, { sender: "user", text: userText }]);
    setInput("");
    setLoading(true);
    try {
      const res = await axios.post(`${API}/chat/`, { message: userText });
      setMessages((prev) => [
        ...prev,
        {
          sender: "bot",
          text: res.data.reply,
          sources: res.data.sources,
          ticket: res.data.ticket,
        },
      ]);
    } catch {
      setMessages((prev) => [
        ...prev,
        { sender: "bot", text: "Error reaching backend server. Ensure FastAPI is running on port 8000." },
      ]);
    }
    setLoading(false);
  };

  const submitManualTicket = async (e) => {
    e.preventDefault();
    if (!ticketDesc.trim()) return;
    setLoading(true);
    await axios.post(`${API}/tickets/`, { description: ticketDesc });
    setTicketDesc("");
    await fetchTickets();
    setLoading(false);
  };

  const requestSoftware = async (appId) => {
    setStatusMsg("");
    try {
      const res = await axios.post(`${API}/software/provision`, { app_id: appId, user_role: role });
      setStatusMsg(`✅ ${res.data.message} (Ticket: ${res.data.ticket.snow_number})`);
    } catch (err) {
      setStatusMsg(`❌ ${err.response?.data?.detail || "Provisioning failed"}`);
    }
  };

  const generateKB = async () => {
    setLoading(true);
    setStatusMsg("");
    const res = await axios.post(`${API}/knowledge/generate-from-tickets`);
    setStatusMsg(`Generated ${res.data.generated_count} new KB article(s) from resolved ServiceNow incidents.`);
    await fetchKnowledge();
    setLoading(false);
  };

  return (
    <div className="layout">
      <aside className="sidebar">
        <div className="brand">
          <Bot size={24} />
          <span>NexusIT AI Desk</span>
        </div>
        <button className={`nav-btn ${tab === "chat" ? "active" : ""}`} onClick={() => setTab("chat")}>
          <Bot size={18} /> AI Self-Service Portal
        </button>
        <button className={`nav-btn ${tab === "tickets" ? "active" : ""}`} onClick={() => setTab("tickets")}>
          <Ticket size={18} /> ServiceNow Tickets
        </button>
        <button className={`nav-btn ${tab === "software" ? "active" : ""}`} onClick={() => setTab("software")}>
          <Package size={18} /> Software Provisioning
        </button>
        <button className={`nav-btn ${tab === "knowledge" ? "active" : ""}`} onClick={() => setTab("knowledge")}>
          <BookOpen size={18} /> Knowledge Base AI
        </button>
      </aside>

      <main className="main-content">
        {tab === "chat" && (
          <>
            <div className="header">
              <h1>AI Helpdesk & Self-Heal Assistant</h1>
              <p>Powered by RAG Vector Search, Hugging Face LLM, and Automated Remediation Agents</p>
            </div>
            <div className="card">
              <div className="chat-box">
                {messages.map((m, idx) => (
                  <div key={idx} className={`msg ${m.sender}`}>
                    <div>{m.text}</div>
                    {m.sources && m.sources.length > 0 && (
                      <div>
                        {m.sources.map((s, i) => (
                          <span key={i} className="badge badge-rag">KB: {s}</span>
                        ))}
                      </div>
                    )}
                    {m.ticket && (
                      <div>
                        <span className={`badge ${m.ticket.status.includes("Resolved") ? "badge-heal" : "badge-open"}`}>
                          {m.ticket.snow_number} • {m.ticket.status}
                        </span>
                      </div>
                    )}
                  </div>
                ))}
                {loading && <div className="msg bot">Analyzing request & checking Knowledge Base...</div>}
              </div>
              <form className="input-row" onSubmit={sendChat}>
                <input
                  placeholder="Ask e.g. 'How do I connect to corporate VPN?' or 'My VPN is stuck, please reset it'"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                />
                <button className="btn" type="submit" disabled={loading}>
                  <Send size={16} /> Send
                </button>
              </form>
            </div>
          </>
        )}

        {tab === "tickets" && (
          <>
            <div className="header">
              <h1>Intelligent Ticket Intake & ServiceNow Sync</h1>
              <p>AI classifies category & urgency automatically and logs incidents into ServiceNow</p>
            </div>
            <div className="card">
              <form className="input-row" onSubmit={submitManualTicket}>
                <input
                  placeholder="Describe an IT issue to auto-triage and log in ServiceNow..."
                  value={ticketDesc}
                  onChange={(e) => setTicketDesc(e.target.value)}
                />
                <button className="btn" type="submit" disabled={loading}>
                  Create Triaged Ticket
                </button>
              </form>
            </div>
            <div className="card">
              <table>
                <thead>
                  <tr>
                    <th>ServiceNow #</th>
                    <th>Summary</th>
                    <th>Category</th>
                    <th>Urgency</th>
                    <th>Status</th>
                    <th>Agent / Resolution Notes</th>
                  </tr>
                </thead>
                <tbody>
                  {tickets.map((t, i) => (
                    <tr key={i}>
                      <td><strong>{t.snow_number}</strong></td>
                      <td>{t.short_description}</td>
                      <td>{t.category}</td>
                      <td>P{t.urgency}</td>
                      <td>
                        <span className={`badge ${t.status.includes("Resolved") || t.status.includes("Provisioned") ? "badge-heal" : "badge-open"}`}>
                          {t.status}
                        </span>
                      </td>
                      <td>{t.resolution_notes}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </>
        )}

        {tab === "software" && (
          <>
            <div className="header">
              <h1>Automated Software Provisioning</h1>
              <p>Role-based entitlement verification with instant ServiceNow fulfillment</p>
            </div>
            <div className="card" style={{ display: "flex", alignItems: "center", gap: "12px" }}>
              <strong>Simulated Employee Role:</strong>
              <select style={{ maxWidth: "240px" }} value={role} onChange={(e) => setRole(e.target.value)}>
                <option value="Developer">Developer</option>
                <option value="Designer">Designer</option>
                <option value="HR">HR</option>
                <option value="IT Admin">IT Admin</option>
              </select>
              {statusMsg && <span>{statusMsg}</span>}
            </div>
            <div className="grid-2">
              {catalog.map((app) => (
                <div className="card" key={app.app_id}>
                  <h3>{app.name}</h3>
                  <p style={{ color: "#64748b", fontSize: "0.85rem", margin: "4px 0 10px" }}>Vendor: {app.vendor}</p>
                  <p style={{ fontSize: "0.9rem", marginBottom: "12px" }}>{app.description}</p>
                  <p style={{ fontSize: "0.8rem", color: "#475569", marginBottom: "14px" }}>
                    Allowed Roles: {app.allowed_roles.join(", ")}
                  </p>
                  <button className="btn" onClick={() => requestSoftware(app.app_id)}>
                    Auto-Provision App
                  </button>
                </div>
              ))}
            </div>
          </>
        )}

        {tab === "knowledge" && (
          <>
            <div className="header" style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <div>
                <h1>Knowledge Management Automation</h1>
                <p>Enterprise RAG repository synced with MongoDB Atlas Vector Search</p>
              </div>
              <button className="btn" onClick={generateKB} disabled={loading}>
                {loading ? <RefreshCw size={16} /> : <Sparkles size={16} />}
                Auto-Generate KB from Resolved Tickets
              </button>
            </div>
            {statusMsg && <div className="card">{statusMsg}</div>}
            <div className="grid-2">
              {articles.map((art, idx) => (
                <div className="card" key={idx}>
                  <span className="badge badge-rag">{art.category}</span>
                  <h3 style={{ margin: "10px 0" }}>{art.title}</h3>
                  <p style={{ whiteSpace: "pre-wrap", fontSize: "0.9rem", color: "#334155" }}>{art.content}</p>
                </div>
              ))}
            </div>
          </>
        )}
      </main>
    </div>
  );
}
