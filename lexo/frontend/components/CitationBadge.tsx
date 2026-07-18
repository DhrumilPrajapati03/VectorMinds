import { Citation } from "@/lib/types";

export default function CitationBadge({ citation }: { citation: Citation }) {
  if (citation.verified) {
    return (
      <div className="flex items-start gap-2 rounded-md bg-sky-50 px-3 py-2 ring-1 ring-inset ring-sky-600/20">
        <span className="mt-0.5 inline-flex h-4 w-4 shrink-0 items-center justify-center rounded-full bg-sky-600 text-[10px] font-bold text-white">
          ✓
        </span>
        <div className="text-sm">
          <p className="font-medium text-sky-800">Verified source</p>
          <p className="text-slate-700">{citation.text}</p>
          {citation.sourceTitle && (
            <p className="mt-0.5 text-xs text-sky-700">{citation.sourceTitle}</p>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="flex items-start gap-2 rounded-md bg-slate-100 px-3 py-2 ring-1 ring-inset ring-slate-300">
      <span className="mt-0.5 inline-flex h-4 w-4 shrink-0 items-center justify-center rounded-full border border-slate-400 text-[10px] font-bold text-slate-500">
        ?
      </span>
      <div className="text-sm">
        <p className="font-medium text-slate-600">Unverified / general principle</p>
        <p className="text-slate-600">{citation.text}</p>
      </div>
    </div>
  );
}
