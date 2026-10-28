function VerdictBadge({ verdict }) {
  const label = String(verdict || "UNVERIFIED").toUpperCase();
  return <span className={`verdict-badge verdict-badge-${label.toLowerCase()}`}>{label.replaceAll("_", " ")}</span>;
}

export default VerdictBadge;
