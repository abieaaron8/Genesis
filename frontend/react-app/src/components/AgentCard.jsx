function AgentCard({ role, result, emptyMessage }) {
  const isProsecutor = role === "prosecutor";
  const entries = Array.isArray(result?.arguments) ? result.arguments : [];
  return (
    <section className={`argument-card argument-${role}`}>
      <div className="argument-heading"><span className="eyebrow">{isProsecutor ? "Contradicting view" : "Supporting view"}</span><span>{result?.evidence_count ?? entries.length} source{(result?.evidence_count ?? entries.length) === 1 ? "" : "s"}</span></div>
      {entries.length === 0 ? <p className="muted-copy">{emptyMessage}</p> : <ul>{entries.map((entry, index) => {
        const text = typeof entry === "string" ? entry : entry.summary || entry.text || "";
        const source = typeof entry === "string" ? "" : entry.source || entry.title || "";
        return <li key={`${source}-${index}`}>{source && <strong>{source}</strong>}<span>{text}</span></li>;
      })}</ul>}
    </section>
  );
}

export default AgentCard;
