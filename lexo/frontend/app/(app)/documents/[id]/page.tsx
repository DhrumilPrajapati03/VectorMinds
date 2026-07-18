"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import ProcessingStepper from "@/components/ProcessingStepper";
import { getDocumentById } from "@/lib/mock-data";
import { ProcessingStage } from "@/lib/types";

const STAGE_ORDER: ProcessingStage[] = ["extracting", "analyzing", "grounding"];

export default function DocumentStatusPage() {
  const params = useParams<{ id: string }>();
  const doc = getDocumentById(params.id);

  // TODO: replace with polling GET /api/documents/{id} once backend exists (FRONTEND_SPEC.md §6.5)
  const [stageIndex, setStageIndex] = useState(0);
  const [done, setDone] = useState(false);

  useEffect(() => {
    if (stageIndex >= STAGE_ORDER.length - 1) {
      const finish = setTimeout(() => setDone(true), 1200);
      return () => clearTimeout(finish);
    }
    const advance = setTimeout(() => setStageIndex((i) => i + 1), 1200);
    return () => clearTimeout(advance);
  }, [stageIndex]);

  return (
    <div>
      <h1 className="mb-1 text-xl font-semibold text-slate-900">{doc.filename}</h1>
      <p className="mb-8 text-sm capitalize text-slate-500">{doc.docType} agreement</p>

      <div className="rounded-xl border border-slate-200 bg-white p-8">
        <ProcessingStepper current={STAGE_ORDER[stageIndex]} />
        <p className="mt-6 text-center text-sm text-slate-500">
          {done ? "Analysis complete." : "This usually takes 1–2 minutes. Feel free to leave this page."}
        </p>

        {done && (
          <div className="mt-4 flex justify-center">
            <Link
              href={`/reports/${doc.id}`}
              className="rounded-md bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-800"
            >
              View report
            </Link>
          </div>
        )}
      </div>
    </div>
  );
}
