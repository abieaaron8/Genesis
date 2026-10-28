import { motion } from "framer-motion";

function ConfidenceGauge({ confidence = 0 }) {
  const value = Math.max(0, Math.min(100, Number(confidence) <= 1 ? Number(confidence) * 100 : Number(confidence)));
  const color = value >= 70 ? "var(--true)" : value >= 40 ? "var(--misleading)" : "var(--false)";
  return (
    <div className="confidence-gauge" aria-label={`Confidence ${Math.round(value)} percent`}>
      <div className="confidence-ring" style={{ "--gauge-value": `${value * 3.6}deg`, "--gauge-color": color }}>
        <div className="confidence-ring-inner"><strong>{Math.round(value)}%</strong><span>confidence</span></div>
      </div>
      <motion.div className="confidence-progress" initial={{ width: 0 }} animate={{ width: `${value}%` }} style={{ background: color }} />
    </div>
  );
}

export default ConfidenceGauge;
