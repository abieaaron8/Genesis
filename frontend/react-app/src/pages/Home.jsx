import { AnimatePresence, motion } from "framer-motion";
import { ArrowUpRight, Clock3, Download, FileText, Menu, RotateCcw, Search, Sparkles, X } from "lucide-react";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useLocation } from "react-router-dom";

import AgentCard from "../components/AgentCard";
import ConfidenceGauge from "../components/ConfidenceGauge";
import EvidenceCard from "../components/EvidenceCard";
import PipelineProgress from "../components/PipelineProgress";
import SkeletonCard from "../components/SkeletonCard";
import VerdictBadge from "../components/VerdictBadge";
import { exportPdf, getHistory, getHistoryDetails, verifyClaim } from "../services/api";

const STAGES = ["claim_analysis", "retrieval", "agent_reasoning", "verdict"];

const sanitizeStages = (stages = {}) => Object.fromEntries(
  STAGES.map((key) => [key, ["pending", "running", "completed", "failed"].includes(stages?.[key]) ? stages[key] : "pending"]),
);

const normalizeVerificationResult = (payload) => {
  const safe = payload && typeof payload === "object" ? payload : {};
  const prosecutor = safe.prosecutor || safe.prosecutor_analysis || {};
  const defender = safe.defender || safe.defender_analysis || {};
  return {
    ...safe,
    success: Boolean(safe.success),
    claim: safe.claim || "",
    evidence: Array.isArray(safe.evidence) ? safe.evidence : [],
    prosecutor: { ...prosecutor, arguments: Array.isArray(prosecutor.arguments) ? prosecutor.arguments : [] },
    defender: { ...defender, arguments: Array.isArray(defender.arguments) ? defender.arguments : [] },
    prosecutor_evidence: Array.isArray(safe.prosecutor_evidence) ? safe.prosecutor_evidence : [],
    defender_evidence: Array.isArray(safe.defender_evidence) ? safe.defender_evidence : [],
    verdict: safe.verdict || "INSUFFICIENT_DATA",
    confidence: Number(safe.confidence || 0),
    reasoning: safe.reasoning || "No reasoning generated.",
    reasoning_points: Array.isArray(safe.reasoning_points) ? safe.reasoning_points : [],
    stages: sanitizeStages(safe.stages),
    model_prediction: safe.model_prediction || null,
    evidence_summary: safe.evidence_summary || {},
  };
};

const readCache = () => {
  try {
    const parsed = JSON.parse(localStorage.getItem("veritas-results-cache") || "{}");
    const now = Date.now();
    return Object.fromEntries(Object.entries(parsed).filter(([, value]) => now - Number(value?.__savedAt || 0) < 15 * 60 * 1000));
  } catch {
    return {};
  }
};

const saveCache = (claim, payload) => {
  const cache = readCache();
  localStorage.setItem("veritas-results-cache", JSON.stringify({ ...cache, [claim]: { ...payload, __savedAt: Date.now() } }));
  localStorage.setItem("veritas-last-claim", claim);
};

const pipelineMessage = (stages) => {
  if (stages?.verdict === "completed") return "Verdict ready";
  if (stages?.agent_reasoning === "running") return "Comparing arguments against the evidence";
  if (stages?.retrieval === "running") return "Finding and ranking relevant sources";
  if (stages?.claim_analysis === "running") return "Reading the claim";
  return "Working through the claim";
};

function Home() {
  const location = useLocation();
  const [claim, setClaim] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [status, setStatus] = useState("");
  const [recentClaims, setRecentClaims] = useState([]);
  const [pdfLoading, setPdfLoading] = useState(false);
  const [railOpen, setRailOpen] = useState(() => localStorage.getItem("genesis-rail-open") !== "false");
  const handledNavigation = useRef("");

  const toggleRail = () => {
    setRailOpen((open) => {
      const next = !open;
      localStorage.setItem("genesis-rail-open", String(next));
      return next;
    });
  };

  const persist = useCallback((claimText, payload) => {
    if (claimText && payload) saveCache(claimText, payload);
  }, []);

  const runVerification = useCallback(async (value, { useCache = true } = {}) => {
    const text = value.trim();
    if (!text) return;
    setClaim(text);
    setError("");
    setLoading(true);
    setResult(null);
    setStatus("Starting verification");
    if (useCache && readCache()[text]) setStatus("Refreshing with the latest evidence");
    try {
      const data = normalizeVerificationResult(await verifyClaim(text));
      setResult(data);
      setStatus(pipelineMessage(data.stages));
      persist(text, data);
    } catch (err) {
      const cached = readCache()[text];
      if (cached) {
        setResult(normalizeVerificationResult(cached));
        setStatus("Showing a recent verification snapshot");
      } else {
        const timedOut = err?.code === "ECONNABORTED" || err?.code === "ETIMEDOUT";
        setError(
          timedOut
            ? "Verification timed out while waiting for evidence providers. Please try again."
            : err?.response?.data?.detail || err.message || "Verification could not be completed.",
        );
      }
    } finally {
      setLoading(false);
    }
  }, [persist]);

  useEffect(() => {
    const historyId = location.state?.historyId;
    const navigationKey = historyId ? `history-${historyId}` : location.state?.claim;
    if (!navigationKey || handledNavigation.current === navigationKey) return;
    handledNavigation.current = navigationKey;
    if (historyId) {
      setLoading(true);
      getHistoryDetails(historyId)
        .then((details) => {
          setClaim(details?.claim || location.state?.claim || "");
          setResult(details ? normalizeVerificationResult(details) : null);
          setStatus("Loaded from history");
        })
        .catch((err) => setError(err?.response?.data?.detail || "History entry could not be loaded."))
        .finally(() => setLoading(false));
    } else {
      runVerification(location.state.claim);
    }
  }, [location.state, runVerification]);

  useEffect(() => {
    getHistory()
      .then((rows) => setRecentClaims((rows || []).filter((row) => row?.claim_text).slice(0, 5)))
      .catch(() => setRecentClaims([]));
  }, [result]);

  const canSubmit = claim.trim().length > 2 && !loading;
  const stages = result?.stages || {};
  const supporting = result?.evidence_summary?.supporting_count ?? result?.support_count ?? 0;
  const contradicting = result?.evidence_summary?.contradicting_count ?? result?.contradict_count ?? 0;
  const relatedSources = useMemo(() => (result?.evidence || []).slice(0, 4), [result]);

  const handleDownloadPdf = async () => {
    const id = result?.history_id || result?.short_id;
    if (!id || pdfLoading) return;
    setPdfLoading(true);
    try {
      const blob = await exportPdf(id);
      const url = window.URL.createObjectURL(blob);
      const anchor = document.createElement("a");
      anchor.href = url;
      anchor.download = `genesis-verification-${new Date().toISOString().slice(0, 10)}.pdf`;
      anchor.click();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      setError(err?.response?.data?.detail || err.message || "The report could not be downloaded.");
    } finally {
      setPdfLoading(false);
    }
  };

  const clear = () => {
    setClaim("");
    setResult(null);
    setError("");
    setStatus("");
  };

  return (
    <main className={`investigation-page ${railOpen ? "" : "rail-closed"}`}>
      {railOpen && (
      <aside className="workspace-rail" aria-label="Workspace">
        <div className="rail-section">
          <span className="eyebrow">Workspace</span>
          <div className="rail-title"><span className="brand-mark">G</span><span>Genesis</span></div>
        </div>
        <div className="rail-section rail-nav">
          <span className="eyebrow">Investigate</span>
          <div className="rail-current"><Search size={16} /> New verification</div>
        </div>
        <div className="rail-section rail-history">
          <div className="rail-section-heading"><span className="eyebrow">Recent</span><span className="rail-count">{recentClaims.length}</span></div>
          {recentClaims.length === 0 ? <p className="rail-empty">Your recent checks will appear here.</p> : recentClaims.map((item) => (
            <button key={item.id} className="rail-history-item" onClick={() => runVerification(item.claim_text)}>
              <span>{item.claim_text}</span>
              <ArrowUpRight size={14} aria-hidden="true" />
            </button>
          ))}
        </div>
        <div className="rail-footer">
          <span className="status-dot" /> Evidence workspace
        </div>
      </aside>
      )}

      <section className="investigation-main">
        <header className="workspace-header">
          <div>
            <button type="button" className="rail-toggle" onClick={toggleRail} aria-label={railOpen ? "Close workspace history" : "Open workspace history"} title={railOpen ? "Close workspace history" : "Open workspace history"}>
              {railOpen ? <X size={17} /> : <Menu size={18} />}
            </button>
          </div>
        </header>

        <section className="claim-composer">
          <div className="composer-label"><FileText size={17} /> Article or claim</div>
          <textarea
            value={claim}
            onChange={(event) => setClaim(event.target.value)}
            onKeyDown={(event) => { if ((event.metaKey || event.ctrlKey) && event.key === "Enter") runVerification(claim); }}
            placeholder="Paste the claim you want to examine…"
            aria-label="Claim to verify"
          />
          <div className="composer-footer">
            <span className="composer-hint">Use a complete sentence for a sharper result.</span>
            <div className="composer-actions">
              <button type="button" className="text-button" onClick={clear} disabled={!claim && !result}>Clear</button>
              <button type="button" className="primary-button" onClick={() => runVerification(claim)} disabled={!canSubmit}>
                {loading ? "Checking…" : "Verify claim"} <span aria-hidden="true">↗</span>
              </button>
            </div>
          </div>
        </section>

        <AnimatePresence mode="wait">
          {error && <motion.div className="notice error-notice" initial={{ opacity: 0, y: -8 }} animate={{ opacity: 1, y: 0 }}><X size={16} /> {error}</motion.div>}
        </AnimatePresence>

        {loading && (
          <section className="loading-workspace" aria-live="polite">
            <PipelineProgress stages={{ claim_analysis: "running", retrieval: "pending", agent_reasoning: "pending", verdict: "pending" }} pipelineMessage={status} />
            <div className="loading-grid"><SkeletonCard /><SkeletonCard /></div>
          </section>
        )}

        {result && !loading && (
          <motion.div className="verification-layout" initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.3 }}>
            <div className="verification-center">
              <section className="article-heading">
                <span className="eyebrow">Claim under review</span>
                <p className="claim-display">{result.claim || claim}</p>
                <div className="claim-meta-line">
                  {result.domain && <span>{result.domain}</span>}
                  {result.claim_type && <span>{result.claim_type.replaceAll("_", " ")}</span>}
                  <span>{result.evidence.length} sources reviewed</span>
                </div>
              </section>

              <section className="timeline-section">
                <div className="section-heading"><span className="eyebrow">Investigation</span><span className="section-status"><span className="status-dot" /> {status || "Complete"}</span></div>
                <PipelineProgress stages={stages} pipelineMessage="" />
              </section>

              <section className="reasoning-section">
                <div className="section-heading"><span className="eyebrow">Judge’s note</span></div>
                <p className="judge-note">{result.reasoning}</p>
                {result.reasoning_points.length > 0 && <ul className="reasoning-list">{result.reasoning_points.map((point, index) => <li key={`${point}-${index}`}>{point}</li>)}</ul>}
              </section>

              <section className="evidence-section">
                <div className="section-heading"><span className="eyebrow">Evidence</span><span className="section-count">{result.evidence.length}</span></div>
                {result.evidence.length === 0 ? <div className="empty-evidence">No relevant evidence was returned for this claim.</div> : <div className="evidence-list">{result.evidence.map((article, index) => <EvidenceCard key={article.id || article.url || index} article={article} />)}</div>}
              </section>

              <section className="arguments-grid">
                <AgentCard role="prosecutor" result={result.prosecutor} emptyMessage="No contradictory argument was generated." />
                <AgentCard role="defender" result={result.defender} emptyMessage="No supporting argument was generated." />
              </section>
            </div>

            <aside className="verification-rail">
              <section className={`verdict-panel verdict-${String(result.verdict).toLowerCase()}`}>
                <div className="panel-kicker"><span className="eyebrow">Final verdict</span><Sparkles size={15} /></div>
                <VerdictBadge verdict={result.verdict} />
                <p>{result.evidence_summary?.summary || result.reasoning}</p>
                <div className="verdict-split"><span><strong>{supporting}</strong> supporting</span><span><strong>{contradicting}</strong> contradicting</span></div>
              </section>

              <section className="side-panel">
                <div className="panel-heading"><span className="eyebrow">Confidence</span></div>
                <ConfidenceGauge confidence={result.confidence} />
              </section>

              <section className="side-panel">
                <div className="panel-heading"><span className="eyebrow">Model signal</span><span className="model-label">DistilBERT</span></div>
                {result.model_prediction ? <div className="model-signal"><strong>{result.model_prediction.label || result.model_prediction.prediction}</strong><span>{Math.round(Number(result.model_prediction.confidence || 0) * 100)}% confidence</span></div> : <p className="muted-copy">Classifier output was unavailable for this check.</p>}
              </section>

              <section className="side-panel">
                <div className="panel-heading"><span className="eyebrow">Related sources</span><span className="section-count">{relatedSources.length}</span></div>
                <div className="related-sources">{relatedSources.map((source, index) => <a key={source.url || index} href={source.url || "#"} target="_blank" rel="noreferrer"><span>{source.source || "Source"}</span><ArrowUpRight size={14} /></a>)}</div>
              </section>

              <button type="button" className="report-button" onClick={handleDownloadPdf} disabled={pdfLoading || !(result.history_id || result.short_id)}><Download size={15} /> {pdfLoading ? "Preparing report…" : "Download report"}</button>
              <button type="button" className="rerun-button" onClick={() => runVerification(claim, { useCache: false })}><RotateCcw size={14} /> Run again</button>
            </aside>
          </motion.div>
        )}

        {!loading && !result && !error && (
          <section className="empty-workspace">
            <Clock3 size={18} />
            <p>Paste a claim above to begin a source-backed verification.</p>
          </section>
        )}
      </section>
    </main>
  );
}

export default Home;
