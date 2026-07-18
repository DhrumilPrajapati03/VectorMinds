import Link from "next/link";
import { DocumentSummary } from "@/lib/types";
import RiskBadge from "./RiskBadge";

const STATUS_LABEL: Record<DocumentSummary["status"], string> = {
  uploaded: "Uploaded",
  processing: "Processing",
  analyzed: "Analyzed",
};

export default function DocumentCard({ doc }: { doc: DocumentSummary }) {
  const href = doc.status === "analyzed" ? `/reports/${doc.id}` : `/documents/${doc.id}`;
  const createdLabel = new Date(doc.createdAt).toLocaleDateString("en-IN", {
    day: "numeric",
    month: "short",
    year: "numeric",
  });

  return (
    <div className="flex items-center justify-between gap-4 rounded-lg border border-zinc-800 bg-zinc-900 p-4 transition hover:border-zinc-700">
      <Link href={href} className="flex min-w-0 flex-1 items-center gap-4">
        <div className="min-w-0">
          <p className="truncate font-medium text-zinc-100">{doc.filename}</p>
          <div className="mt-1.5 flex items-center gap-2 text-xs text-zinc-500">
            <span className="rounded-full bg-zinc-800 px-2 py-0.5 capitalize text-zinc-300">{doc.docType}</span>
            <span>{STATUS_LABEL[doc.status]}</span>
            <span>·</span>
            <span>{createdLabel}</span>
          </div>
        </div>
      </Link>
      <div className="flex shrink-0 items-center gap-3">
        {doc.riskScore && <RiskBadge score={doc.riskScore} size="sm" />}
        <button
          type="button"
          className="rounded-md px-2 py-1 text-sm text-zinc-500 transition hover:bg-rose-950/40 hover:text-rose-400"
          aria-label={`Delete ${doc.filename}`}
        >
          Delete
        </button>
      </div>
    </div>
  );
}
