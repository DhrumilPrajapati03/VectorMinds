"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import UploadDropzone from "@/components/UploadDropzone";
import { DocType } from "@/lib/types";

export default function UploadPage() {
  const router = useRouter();
  const [docType, setDocType] = useState<DocType>("rental");
  const [file, setFile] = useState<File | null>(null);
  const [uploaded, setUploaded] = useState(false);
  const [starting, setStarting] = useState(false);

  function handleUpload() {
    // TODO: wire to POST /api/upload once backend upload exists
    setUploaded(true);
  }

  function handleStartAnalysis() {
    setStarting(true);
    // TODO: wire to POST /api/analyze/{document_id}
    setTimeout(() => router.push("/documents/doc-new"), 400);
  }

  return (
    <div>
      <h1 className="mb-6 text-xl font-semibold text-slate-900">Upload a document</h1>

      <div className="rounded-xl border border-slate-200 bg-white p-6">
        <label className="mb-2 block text-sm font-medium text-slate-700">Document type</label>
        <div className="mb-6 inline-flex rounded-md border border-slate-300 p-1">
          {(["rental", "employment"] as DocType[]).map((type) => (
            <button
              key={type}
              type="button"
              onClick={() => setDocType(type)}
              className={`rounded-md px-4 py-1.5 text-sm font-medium capitalize transition ${
                docType === type ? "bg-slate-900 text-white" : "text-slate-600 hover:bg-slate-100"
              }`}
            >
              {type}
            </button>
          ))}
        </div>

        <UploadDropzone onFileSelected={setFile} />

        {file && !uploaded && (
          <button
            type="button"
            onClick={handleUpload}
            className="mt-4 w-full rounded-md bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-800"
          >
            Upload
          </button>
        )}

        {uploaded && (
          <div className="mt-4 rounded-md bg-emerald-50 p-4 ring-1 ring-inset ring-emerald-600/20">
            <p className="text-sm font-medium text-emerald-800">
              &ldquo;{file?.name}&rdquo; uploaded successfully.
            </p>
            <button
              type="button"
              onClick={handleStartAnalysis}
              disabled={starting}
              className="mt-3 rounded-md bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-800 disabled:opacity-50"
            >
              {starting ? "Starting..." : "Start analysis"}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
