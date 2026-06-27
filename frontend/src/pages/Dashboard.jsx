import { useEffect, useState } from "react";
import api from "../api/api";
import ReactMarkdown from "react-markdown";

// ── Design tokens ────────────────────────────────────────────
const NAVY   = "#1B3A6B";
const CERUL  = "#2D7DD2";
const CARBON = "#111827";
const ASH    = "#6B7280";
const SLATE  = "#E2E6ED";
const BG     = "#F7F8FA";

const statusMeta = {
  completed:  { bg: "#DCFCE7", text: "#15803D" },
  processing: { bg: "#FEF3C7", text: "#B45309" },
  failed:     { bg: "#FEE2E2", text: "#B91C1C" },
  pending:    { bg: "#F1F5F9", text: "#475569" },
};

function StatusChip({ label, count }) {
  const meta = statusMeta[label?.toLowerCase()] ?? statusMeta.pending;
  return (
    <span style={{
      display: "inline-flex", alignItems: "center", gap: 4,
      padding: "2px 8px", borderRadius: 4,
      background: meta.bg, color: meta.text,
      fontSize: 11, fontWeight: 600, letterSpacing: "0.03em",
      textTransform: "uppercase",
    }}>
      {label}
      {count != null && (
        <span style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: 10 }}>
          · {count}
        </span>
      )}
    </span>
  );
}

function SectionCard({ title, subtitle, children, style }) {
  return (
    <div style={{
      background: "#fff",
      border: `1px solid ${SLATE}`,
      borderRadius: 8,
      overflow: "hidden",
      ...style,
    }}>
      {(title || subtitle) && (
        <div style={{
          padding: "14px 20px",
          borderBottom: `1px solid ${SLATE}`,
          display: "flex", alignItems: "baseline", gap: 10,
        }}>
          {title && (
            <span style={{ fontSize: 13, fontWeight: 700, color: CARBON, letterSpacing: "-0.01em" }}>
              {title}
            </span>
          )}
          {subtitle && (
            <span style={{ fontSize: 12, color: ASH }}>
              {subtitle}
            </span>
          )}
        </div>
      )}
      <div style={{ padding: "16px 20px" }}>
        {children}
      </div>
    </div>
  );
}

function NavyButton({ onClick, children, disabled, variant = "primary", style }) {
  const isPrimary = variant === "primary";
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      style={{
        display: "inline-flex", alignItems: "center", gap: 6,
        padding: "8px 16px",
        background: disabled ? "#E2E6ED" : isPrimary ? NAVY : "transparent",
        color: disabled ? ASH : isPrimary ? "#fff" : NAVY,
        border: `1px solid ${disabled ? SLATE : isPrimary ? NAVY : NAVY}`,
        borderRadius: 5,
        fontSize: 13, fontWeight: 600, letterSpacing: "-0.01em",
        cursor: disabled ? "not-allowed" : "pointer",
        transition: "background 0.15s, color 0.15s",
        whiteSpace: "nowrap",
        ...style,
      }}
      onMouseEnter={e => {
        if (!disabled) {
          e.currentTarget.style.background = isPrimary ? "#142D55" : "#EEF3FB";
        }
      }}
      onMouseLeave={e => {
        if (!disabled) {
          e.currentTarget.style.background = isPrimary ? NAVY : "transparent";
        }
      }}
    >
      {children}
    </button>
  );
}

function MetricRow({ label, value, mono }) {
  return (
    <div style={{
      display: "flex", justifyContent: "space-between", alignItems: "center",
      padding: "7px 0", borderBottom: `1px solid ${BG}`,
    }}>
      <span style={{ fontSize: 12, color: ASH }}>{label}</span>
      <span style={{
        fontSize: 13, fontWeight: 600, color: CARBON,
        fontFamily: mono ? "'JetBrains Mono', monospace" : "inherit",
      }}>
        {value}
      </span>
    </div>
  );
}

// ── Main Component ────────────────────────────────────────────
export default function Dashboard() {
  const [file, setFile]                       = useState(null);
  const [docType, setDocType]                 = useState("");
  const [documents, setDocuments]             = useState([]);
  const [selectedDocument, setSelectedDocument] = useState(null);
  const [selectedDocuments, setSelectedDocuments] = useState([]);
  const [sessionStats, setSessionStats]       = useState(null);
  const [sessions, setSessions]               = useState([]);
  const [selectedSession, setSelectedSession] = useState(null);
  const [newSessionTitle, setNewSessionTitle] = useState("");
  const [question, setQuestion]               = useState("");
  const [answer, setAnswer]                   = useState("");
  const [summary, setSummary]                 = useState("");
  const [dragOver, setDragOver]               = useState(false);

  const loadDocuments = async () => {
    try { const res = await api.get("/document"); setDocuments(res.data); }
    catch (err) { console.error(err); }
  };

  const createSession = async () => {
    try {
      const userId = document.cookie.split("; ").find(r => r.startsWith("user_id="))?.split("=")[1];
      if (!userId) { alert("User ID cookie not found"); return; }
      const res = await api.post("/upload_session", { user_id: userId, title: newSessionTitle });
      await loadSessions();
      setSelectedSession(res.data.session_id);
      setNewSessionTitle("");
    } catch (err) { console.error(err); alert("Failed to create session"); }
  };

  const loadSessions = async () => {
    try { const res = await api.get("/upload_session"); setSessions(res.data); }
    catch (err) { console.error(err); }
  };

  const loadDocumentsBySession = async (sessionId) => {
    try { const res = await api.get(`/document/session/${sessionId}`); setDocuments(res.data); }
    catch (err) { console.error(err); }
  };

  const fetchSummary = async (doc_id) => {
    try {

      const res = await api.get(
        `/document_summary/document/${doc_id}`
      );

      setSummary(
        res.data.content
      );

    } catch (err) {

      console.error(err);

      if (
        err.response?.status === 404
      ) {

        setSummary(
          "⚙️ Summary generation in progress. Please wait a few moments and try again."
        );

        pollSummary(doc_id);

      } else if (
        err.response?.status === 500
      ) {

        setSummary(
          "❌ Failed to load the summary due to a server error."
        );

      } else {

        setSummary(
          "❌ Unable to fetch the summary. Please try again later."
        );

      }

    }
  };

  const retrySummary = async (docId) => {
    try {

      await api.post(
        `/document/${docId}/retry-summary`
      );

      setSummary(
        "⚙️ Summary generation restarted..."
      );

      pollSummary(docId);

    } catch (err) {

      console.error(err);

      alert(
        "Failed to restart summary generation."
      );

    }
  };

  const loadSessionStats = async (sessionId) => {
    try { const res = await api.get(`/upload_session/${sessionId}/stats`); setSessionStats(res.data); }
    catch (err) { console.error(err); }
  };

  const pollSummary = (doc_id) => {
    let attempts = 0;
    const interval = setInterval(async () => {
      attempts++;
      try {
        const res = await api.get(`/document_summary/document/${doc_id}`);
        setSummary(res.data.content);
        clearInterval(interval);
      } catch (err) {
        console.log("Polling:", err.response?.status);
        if (attempts >= 120) { setSummary("Summary generation timed out."); clearInterval(interval); }
      }
    }, 5000);
  };

  useEffect(() => { loadSessions(); }, []);

  const uploadDocument = async () => {
    if (!selectedSession) { alert("Please select a session first"); return; }
    try {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("doc_type", docType);
      formData.append("session_id", selectedSession);
      const res = await api.post("/document", formData);
      alert("Upload successful");
      loadDocumentsBySession(selectedSession);
    } catch (err) { console.error(err); alert("Upload failed"); }
  };

  const askQuestion = async () => {
    try {

      let res;

      if (selectedDocuments.length === 1) {

        res = await api.post(
          "/query",
          {
            query: question,
            document_id:
              selectedDocuments[0]
          }
        );

      } else if (
        selectedDocuments.length >= 2
      ) {

        res = await api.post(
          "/comparison",
          {
            question: question,
            document_ids: selectedDocuments
          }
        );

      } else if (
        selectedSession
      ) {

        res = await api.post(
          "/query/session",
          {
            query: question,
            session_id:
              selectedSession
          }
        );

      } else {

        alert(
          "Select a session first"
        );

        return;
      }

      setAnswer(
        res.data.answer ??
        res.data.comparison
      );

    } catch (err) {

      console.error(err);

      alert(
        "Request failed"
      );

    }
  };

  const handleSessionClick = (session) => {
    if (selectedSession === session.session_id) {
      setSelectedSession(null); setDocuments([]); setSelectedDocument(null);
      setSelectedDocuments([]); setSummary(""); setSessionStats(null);
    } else {
      setSelectedSession(session.session_id); setSelectedDocument(null);
      setSummary(""); setSelectedDocuments([]);
      loadDocumentsBySession(session.session_id);
      loadSessionStats(session.session_id);
    }
  };

  // ── Render ────────────────────────────────────────────────
  return (
    <>
      {/* Google Fonts */}
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');
        *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: 'Inter', system-ui, sans-serif; background: ${BG}; color: ${CARBON}; }
        ::-webkit-scrollbar { width: 6px; height: 6px; }
        ::-webkit-scrollbar-track { background: ${BG}; }
        ::-webkit-scrollbar-thumb { background: ${SLATE}; border-radius: 3px; }
        table { border-collapse: collapse; width: 100%; }
        th { text-align: left; font-size: 11px; font-weight: 700; color: ${ASH};
             letter-spacing: 0.06em; text-transform: uppercase;
             padding: 8px 12px; background: ${BG}; border-bottom: 1px solid ${SLATE}; }
        td { padding: 10px 12px; font-size: 13px; color: ${CARBON};
             border-bottom: 1px solid ${BG}; }
        tr:last-child td { border-bottom: none; }
        tr:hover td { background: #F7F9FF; }
        textarea, input[type="text"] {
          font-family: 'Inter', sans-serif;
          font-size: 13px;
          border: 1px solid ${SLATE};
          border-radius: 5px;
          padding: 9px 12px;
          width: 100%;
          color: ${CARBON};
          background: #fff;
          outline: none;
          transition: border-color 0.15s;
        }
        textarea:focus, input[type="text"]:focus { border-color: ${CERUL}; box-shadow: 0 0 0 3px rgba(45,125,210,0.12); }
        .markdown-body p { font-size: 13px; line-height: 1.7; color: #374151; margin-bottom: 8px; }
        .markdown-body h1, .markdown-body h2, .markdown-body h3 {
          font-size: 14px; font-weight: 700; color: ${CARBON}; margin: 14px 0 6px;
        }
        .markdown-body ul, .markdown-body ol { padding-left: 18px; }
        .markdown-body li { font-size: 13px; line-height: 1.7; color: #374151; }
      `}</style>

      {/* ── Top Header ── */}
      <header style={{
        background: NAVY, color: "#fff",
        padding: "0 32px", height: 54,
        display: "flex", alignItems: "center", justifyContent: "space-between",
        position: "sticky", top: 0, zIndex: 100,
        borderBottom: "1px solid rgba(255,255,255,0.08)",
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          {/* Logo mark */}
          <div style={{
            width: 28, height: 28, borderRadius: 6,
            background: CERUL,
            display: "flex", alignItems: "center", justifyContent: "center",
          }}>
            <svg width="15" height="15" viewBox="0 0 15 15" fill="none">
              <rect x="2" y="2" width="5" height="6" rx="1" fill="white" opacity="0.9"/>
              <rect x="8" y="2" width="5" height="3" rx="1" fill="white" opacity="0.6"/>
              <rect x="2" y="10" width="11" height="2" rx="1" fill="white" opacity="0.7"/>
              <rect x="8" y="6" width="5" height="3" rx="1" fill="white" opacity="0.4"/>
            </svg>
          </div>
          <span style={{ fontSize: 15, fontWeight: 700, letterSpacing: "-0.02em" }}>
            DocIntelli
          </span>
          <span style={{
            fontSize: 10, fontWeight: 600, color: "rgba(255,255,255,0.45)",
            letterSpacing: "0.08em", textTransform: "uppercase", marginLeft: 4,
          }}>
            Document Intelligence Platform
          </span>
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: 20 }}>
          <span style={{ fontSize: 12, color: "rgba(255,255,255,0.55)" }}>
            {new Date().toLocaleDateString("en-GB", { day: "numeric", month: "short", year: "numeric" })}
          </span>
          <div style={{
            width: 30, height: 30, borderRadius: "50%",
            background: "rgba(255,255,255,0.12)",
            display: "flex", alignItems: "center", justifyContent: "center",
            fontSize: 12, fontWeight: 700, color: "rgba(255,255,255,0.8)",
            cursor: "pointer",
          }}>
            U
          </div>
        </div>
      </header>

      {/* ── Main 3-column layout ── */}
      <div style={{
        display: "grid",
        gridTemplateColumns: "260px 1fr 360px",
        gap: 0,
        minHeight: "calc(100vh - 54px)",
        alignItems: "start",
      }}>

        {/* ══ LEFT SIDEBAR — Sessions ══ */}
        <aside style={{
          background: "#fff",
          borderRight: `1px solid ${SLATE}`,
          minHeight: "calc(100vh - 54px)",
          padding: "20px 16px",
          display: "flex", flexDirection: "column", gap: 16,
        }}>
          {/* New session input */}
          <div>
            <p style={{ fontSize: 11, fontWeight: 700, color: ASH, letterSpacing: "0.07em", textTransform: "uppercase", marginBottom: 8 }}>
              New Session
            </p>
            <div style={{ display: "flex", gap: 6 }}>
              <input
                type="text"
                placeholder="Session name"
                value={newSessionTitle}
                onChange={e => setNewSessionTitle(e.target.value)}
                onKeyDown={e => e.key === "Enter" && createSession()}
                style={{ flex: 1, fontSize: 12, padding: "7px 10px" }}
              />
              <NavyButton onClick={createSession} style={{ padding: "7px 12px", fontSize: 12 }}>
                +
              </NavyButton>
            </div>
          </div>

          <div style={{ height: 1, background: SLATE }} />

          {/* Sessions list */}
          <div>
            <p style={{ fontSize: 11, fontWeight: 700, color: ASH, letterSpacing: "0.07em", textTransform: "uppercase", marginBottom: 8 }}>
              Sessions
            </p>
            <div style={{ display: "flex", flexDirection: "column", gap: 3 }}>
              {sessions.length === 0 && (
                <p style={{ fontSize: 12, color: ASH, padding: "8px 0" }}>No sessions yet.</p>
              )}
              {sessions.map(session => {
                const active = selectedSession === session.session_id;
                return (
                  <div
                    key={session.session_id}
                    onClick={() => handleSessionClick(session)}
                    style={{
                      padding: "9px 12px",
                      borderRadius: 6,
                      cursor: "pointer",
                      background: active ? "#EEF3FB" : "transparent",
                      borderLeft: `3px solid ${active ? CERUL : "transparent"}`,
                      transition: "background 0.12s",
                    }}
                    onMouseEnter={e => { if (!active) e.currentTarget.style.background = BG; }}
                    onMouseLeave={e => { if (!active) e.currentTarget.style.background = "transparent"; }}
                  >
                    <div style={{ fontSize: 13, fontWeight: active ? 600 : 400, color: active ? NAVY : CARBON }}>
                      {session.title}
                    </div>
                    {session.status && (
                      <div style={{ marginTop: 4 }}>
                        <StatusChip label={session.status} />
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>

          {/* Session stats */}
          {sessionStats && (
            <>
              <div style={{ height: 1, background: SLATE }} />
              <div>
                <p style={{ fontSize: 11, fontWeight: 700, color: ASH, letterSpacing: "0.07em", textTransform: "uppercase", marginBottom: 10 }}>
                  Session Stats
                </p>
                <MetricRow label="Total Documents" value={sessionStats.total_documents} mono />
                <MetricRow label="Completed" value={sessionStats.completed} mono />
                <MetricRow label="Processing" value={sessionStats.processing} mono />
                <MetricRow label="Failed" value={sessionStats.failed} mono />
                <MetricRow label="Pending" value={sessionStats.pending} mono />
              </div>
            </>
          )}
        </aside>

        {/* ══ CENTRE — Upload + Documents ══ */}
        <main style={{ padding: 24, display: "flex", flexDirection: "column", gap: 20 }}>

          {/* Upload card */}
          <SectionCard title="Upload Document" subtitle="PDF or XLSX">
            {/* Drop zone */}
            <div
              onDragOver={e => { e.preventDefault(); setDragOver(true); }}
              onDragLeave={() => setDragOver(false)}
              onDrop={e => { e.preventDefault(); setDragOver(false); setFile(e.dataTransfer.files[0]); }}
              style={{
                border: `2px dashed ${dragOver ? CERUL : SLATE}`,
                borderRadius: 6,
                padding: "28px 20px",
                textAlign: "center",
                background: dragOver ? "#EEF3FB" : BG,
                transition: "all 0.15s",
                marginBottom: 14,
                position: "relative",
              }}
            >
              {/* Upload icon */}
              <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke={ASH} strokeWidth="1.5"
                   style={{ margin: "0 auto 8px", display: "block" }}>
                <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4M17 8l-5-5-5 5M12 3v12"/>
              </svg>
              <p style={{ fontSize: 13, color: ASH, marginBottom: 4 }}>
                Drag & drop file here, or{" "}
                <label style={{ color: CERUL, fontWeight: 600, cursor: "pointer" }}>
                  browse
                  <input type="file" style={{ display: "none" }} onChange={e => setFile(e.target.files[0])} />
                </label>
              </p>
              <p style={{ fontSize: 11, color: "#9CA3AF" }}>PDF and XLSX supported</p>
              {file && (
                <div style={{
                  marginTop: 12, padding: "6px 12px", background: "#EEF3FB",
                  borderRadius: 4, display: "inline-flex", alignItems: "center", gap: 6,
                  fontSize: 12, color: NAVY, fontWeight: 500,
                }}>
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8zM14 2v6h6"/>
                  </svg>
                  {file.name}
                </div>
              )}
            </div>

            <div style={{ display: "flex", gap: 10, alignItems: "flex-end" }}>
              <div style={{ flex: 1 }}>
                <label style={{ fontSize: 11, fontWeight: 600, color: ASH, textTransform: "uppercase", letterSpacing: "0.06em", display: "block", marginBottom: 5 }}>
                  Document Type
                </label>
                <input
                  type="text"
                  placeholder="e.g. Annual Report, Balance Sheet"
                  value={docType}
                  onChange={e => setDocType(e.target.value)}
                />
              </div>
              <NavyButton
                onClick={uploadDocument}
                disabled={!file || !selectedSession}
                style={{ height: 38, paddingTop: 0, paddingBottom: 0 }}
              >
                Upload
              </NavyButton>
            </div>

            {!selectedSession && (
              <p style={{ fontSize: 12, color: "#B45309", marginTop: 8, display: "flex", alignItems: "center", gap: 5 }}>
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
                </svg>
                Select a session from the sidebar before uploading.
              </p>
            )}
          </SectionCard>

          {/* Documents table */}
          <SectionCard
            title="Documents"
            subtitle={selectedSession ? `${documents.length} file${documents.length !== 1 ? "s" : ""}` : "No session selected"}
          >
            {!selectedSession ? (
              <p style={{ fontSize: 13, color: ASH }}>Select a session from the sidebar to view its documents.</p>
            ) : documents.length === 0 ? (
              <p style={{ fontSize: 13, color: ASH }}>No documents uploaded to this session yet.</p>
            ) : (
              <>
                <div style={{ display: "flex", justifyContent: "flex-end", marginBottom: 10 }}>
                  <NavyButton
                    variant="outline"
                    onClick={() => loadDocumentsBySession(selectedSession)}
                    style={{ fontSize: 12, padding: "6px 12px" }}
                  >
                    ↻ Refresh
                  </NavyButton>
                </div>
                <div style={{ maxHeight: 380, overflowY: "auto", border: `1px solid ${SLATE}`, borderRadius: 6 }}>
                  <table>
                    <thead>
                      <tr>
                        <th>File Name</th>
                        <th>Uploaded</th>
                        <th style={{ textAlign: "right" }}>Action</th>
                      </tr>
                    </thead>
                    <tbody>
                      {documents.map(doc => {
                        const isSelected = selectedDocuments.includes(doc.doc_id);
                        return (
                          <tr key={doc.doc_id} style={{ background: isSelected ? "#EEF3FB" : undefined }}>
                            <td>
                              <div style={{ display: "flex", alignItems: "center", gap: 7 }}>
                                {isSelected && (
                                  <span style={{ color: CERUL, fontSize: 12 }}>✓</span>
                                )}
                                <span style={{ fontWeight: isSelected ? 600 : 400, color: isSelected ? NAVY : CARBON }}>
                                  {doc.file_name}
                                </span>
                              </div>
                            </td>
                            <td style={{ fontFamily: "'JetBrains Mono', monospace", fontSize: 12, color: ASH }}>
                              {new Date(doc.upload_time).toLocaleDateString("en-GB")}
                            </td>
                            <td style={{ textAlign: "right" }}>
                              <button
                                onClick={() => {
                                  setSelectedDocument(doc);
                                  if (selectedDocuments.includes(doc.doc_id)) {
                                    setSelectedDocuments(selectedDocuments.filter(id => id !== doc.doc_id));
                                  } else {
                                    setSelectedDocuments([...selectedDocuments, doc.doc_id]);
                                  }
                                  fetchSummary(doc.doc_id);
                                }}
                                style={{
                                  fontSize: 12, fontWeight: 600,
                                  padding: "5px 12px", borderRadius: 4,
                                  cursor: "pointer",
                                  background: isSelected ? NAVY : "transparent",
                                  color: isSelected ? "#fff" : NAVY,
                                  border: `1px solid ${isSelected ? NAVY : SLATE}`,
                                  transition: "all 0.12s",
                                }}
                              >
                                {isSelected ? "Selected" : "Select"}
                              </button>
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              </>
            )}
          </SectionCard>
        </main>

        {/* ══ RIGHT PANEL — Query + Summary ══ */}
        <aside style={{
          borderLeft: `1px solid ${SLATE}`,
          background: "#fff",
          minHeight: "calc(100vh - 54px)",
          padding: "20px 20px",
          display: "flex", flexDirection: "column", gap: 20,
        }}>

          {/* Query section */}
          <div>
            <p style={{ fontSize: 11, fontWeight: 700, color: ASH, letterSpacing: "0.07em", textTransform: "uppercase", marginBottom: 12 }}>
              Query
            </p>

            {/* Selected docs pill list */}
            <div style={{ marginBottom: 12 }}>
              {selectedDocuments.length === 0 ? (
                <p style={{ fontSize: 12, color: ASH }}>No documents selected.</p>
              ) : (
                <div style={{ display: "flex", flexWrap: "wrap", gap: 5 }}>
                  {documents
                    .filter(d => selectedDocuments.includes(d.doc_id))
                    .map(d => (
                      <span key={d.doc_id} style={{
                        fontSize: 11, padding: "3px 9px", borderRadius: 4,
                        background: "#EEF3FB", color: NAVY, fontWeight: 500,
                        border: `1px solid #BFDBFE`,
                        maxWidth: 180, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap",
                      }}>
                        {d.file_name}
                      </span>
                    ))}
                </div>
              )}

              {selectedDocuments.length > 0 && (
                <p style={{ fontSize: 11, color: CERUL, marginTop: 6, fontWeight: 500 }}>
                  {selectedDocuments.length === 1 ? "Single document query" : `Cross-document comparison (${selectedDocuments.length} docs)`}
                </p>
              )}
            </div>

            <textarea
              placeholder="Ask a question about the selected document(s)…"
              value={question}
              onChange={e => setQuestion(e.target.value)}
              style={{ resize: "vertical", minHeight: 90, marginBottom: 10 }}
              onKeyDown={e => { if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) askQuestion(); }}
            />

            <NavyButton
              onClick={askQuestion}
              disabled={selectedDocuments.length === 0}
              style={{ width: "100%", justifyContent: "center" }}
            >
              {selectedDocuments.length >= 2 ? "Compare & Answer" : "Ask"}
            </NavyButton>

            {answer && (
              <div style={{
                marginTop: 14,
                padding: "12px 14px",
                background: BG,
                border: `1px solid ${SLATE}`,
                borderRadius: 6,
              }}>
                <p style={{ fontSize: 11, fontWeight: 700, color: ASH, letterSpacing: "0.07em", textTransform: "uppercase", marginBottom: 8 }}>
                  Answer
                </p>
                <p style={{ fontSize: 13, lineHeight: 1.7, color: CARBON }}>{answer}</p>
              </div>
            )}
          </div>

          <div style={{ height: 1, background: SLATE }} />

          {/* Summary section */}
          <div style={{ flex: 1 }}>
            <p style={{ fontSize: 11, fontWeight: 700, color: ASH, letterSpacing: "0.07em", textTransform: "uppercase", marginBottom: 8 }}>
              Document Summary
            </p>

            {selectedDocument && (
              <p style={{ fontSize: 12, color: NAVY, fontWeight: 500, marginBottom: 10, display: "flex", alignItems: "center", gap: 5 }}>
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8zM14 2v6h6"/>
                </svg>
                {selectedDocument.file_name}
              </p>
            )}

            <div className="markdown-body" style={{
              fontSize: 13, lineHeight: 1.75, color: "#374151",
              maxHeight: 480, overflowY: "auto",
            }}>
              <ReactMarkdown>
                {selectedDocument ? summary : "Select a document to view its AI-generated summary."}
              </ReactMarkdown>
            </div>

            {selectedDocument && (

                <NavyButton
                  style={{
                    marginTop: 12,
                    width: "100%",
                    justifyContent: "center",
                  }}
                  onClick={() =>
                    retrySummary(selectedDocument.doc_id)
                  }
                >
                  Retry Summary
                </NavyButton>

              )}
          </div>
        </aside>
      </div>
    </>
  );
}
