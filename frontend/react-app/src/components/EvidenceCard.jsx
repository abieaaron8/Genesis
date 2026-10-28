import { ArrowUpRight, CalendarDays } from "lucide-react";

function EvidenceCard({ article }) {
  const credibility = Math.max(0, Math.min(1, Number(article?.credibility_score ?? article?.credibility ?? 0.5) > 1 ? Number(article?.credibility_score ?? article?.credibility ?? 0.5) / 100 : Number(article?.credibility_score ?? article?.credibility ?? 0.5)));
  const stance = String(article?.stance || "").toUpperCase();
  const published = article?.published_date || article?.date || article?.published_at;
  return (
    <article className="evidence-item">
      <div className="evidence-item-top">
        <div>
          <span className="source-name">{article?.source || article?.evidence_source || "Unknown source"}</span>
          <h3>{article?.title || "Untitled source"}</h3>
        </div>
        {stance && <span className={`stance-label stance-${stance.toLowerCase()}`}>{stance === "SUPPORTS" ? "Supports" : stance === "CONTRADICTS" ? "Contradicts" : "Neutral"}</span>}
      </div>
      <p>{article?.content || article?.full_content || "No source summary available."}</p>
      <div className="evidence-item-meta">
        <span><span className="credibility-dot" style={{ background: credibility >= 0.7 ? "var(--true)" : credibility >= 0.4 ? "var(--misleading)" : "var(--false)" }} /> {Math.round(credibility * 100)}% source credibility</span>
        {published && <span><CalendarDays size={13} /> {new Date(published).toLocaleDateString()}</span>}
        {article?.recency_score != null && <span>{Math.round(Number(article.recency_score) * 100)}% recent</span>}
        {article?.url && <a href={article.url} target="_blank" rel="noreferrer">Read source <ArrowUpRight size={13} /></a>}
      </div>
    </article>
  );
}

export default EvidenceCard;
