import { Flag } from "@/lib/types";
import CitationBadge from "./CitationBadge";

const SEVERITY_STYLES: Record<Flag["severity"], string> = {
  low: "bg-slate-100 text-slate-600",
  medium: "bg-amber-100 text-amber-700",
  high: "bg-rose-100 text-rose-700",
};

export default function FlagCard({ flag }: { flag: Flag }) {
  return (
    <div className="rounded-lg border border-slate-200 bg-white p-4">
      <div className="flex items-start justify-between gap-3">
        <h3 className="font-medium text-slate-900">{flag.clause}</h3>
        <span
          className={`shrink-0 rounded-full px-2 py-0.5 text-xs font-medium capitalize ${SEVERITY_STYLES[flag.severity]}`}
        >
          {flag.severity}
        </span>
      </div>
      <p className="mt-1.5 text-sm leading-relaxed text-slate-700">{flag.issue}</p>
      <div className="mt-3 space-y-2">
        {flag.citations.map((citation, i) => (
          <CitationBadge key={i} citation={citation} />
        ))}
      </div>
    </div>
  );
}
