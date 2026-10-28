import { Check, Circle, LoaderCircle, X } from "lucide-react";
import { motion } from "framer-motion";

const STAGES = [
  ["claim_analysis", "Claim read"],
  ["retrieval", "Sources found"],
  ["agent_reasoning", "Evidence weighed"],
  ["verdict", "Verdict"],
];

const Icon = ({ status }) => {
  if (status === "completed") return <Check size={13} />;
  if (status === "failed") return <X size={13} />;
  if (status === "running") return <LoaderCircle size={13} className="spin-soft" />;
  return <Circle size={10} />;
};

export default function PipelineProgress({ stages = {}, pipelineMessage = "" }) {
  return (
    <div className="timeline">
      <div className="timeline-line" />
      {STAGES.map(([key, label]) => {
        const status = stages[key] || "pending";
        return (
          <div key={key} className={`timeline-step timeline-${status}`}>
            <div className="timeline-marker"><Icon status={status} /></div>
            <span>{label}</span>
          </div>
        );
      })}
      {pipelineMessage && <motion.p className="timeline-message" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>{pipelineMessage}</motion.p>}
    </div>
  );
}
