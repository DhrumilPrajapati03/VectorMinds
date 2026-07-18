import { RiskScore } from "@/lib/types";

const STYLES: Record<RiskScore, { label: string; classes: string; dot: string }> = {
  green: { label: "Low concern", classes: "bg-emerald-500/10 text-emerald-400 ring-emerald-500/30", dot: "bg-emerald-400" },
  yellow: { label: "Some concerns", classes: "bg-amber-500/10 text-amber-400 ring-amber-500/30", dot: "bg-amber-400" },
  red: { label: "Significant concerns", classes: "bg-rose-500/10 text-rose-400 ring-rose-500/30", dot: "bg-rose-400" },
};

export default function RiskBadge({
  score,
  size = "md",
}: {
  score: RiskScore;
  size?: "sm" | "md";
}) {
  const { label, classes, dot } = STYLES[score];
  const sizeClasses = size === "sm" ? "px-2 py-0.5 text-xs" : "px-3 py-1 text-sm";

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full font-medium ring-1 ring-inset ${classes} ${sizeClasses}`}
    >
      <span className={`h-1.5 w-1.5 rounded-full ${dot}`} />
      {label}
    </span>
  );
}
