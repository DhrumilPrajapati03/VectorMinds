"use client";

import { useRef, useState } from "react";

export default function UploadDropzone({
  onFileSelected,
}: {
  onFileSelected?: (file: File) => void;
}) {
  const [isDragging, setIsDragging] = useState(false);
  const [fileName, setFileName] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  function handleFile(file: File | undefined) {
    if (!file) return;
    setFileName(file.name);
    onFileSelected?.(file);
  }

  return (
    <div
      onDragOver={(e) => {
        e.preventDefault();
        setIsDragging(true);
      }}
      onDragLeave={() => setIsDragging(false)}
      onDrop={(e) => {
        e.preventDefault();
        setIsDragging(false);
        handleFile(e.dataTransfer.files?.[0]);
      }}
      className={`flex flex-col items-center justify-center gap-3 rounded-xl border-2 border-dashed p-10 text-center transition ${
        isDragging ? "border-sky-500 bg-sky-50" : "border-slate-300 bg-white"
      }`}
    >
      <div className="flex h-12 w-12 items-center justify-center rounded-full bg-slate-100 text-xl">
        📄
      </div>
      {fileName ? (
        <p className="text-sm font-medium text-slate-900">{fileName}</p>
      ) : (
        <p className="text-sm text-slate-600">Drag a PDF or DOCX here</p>
      )}
      <label htmlFor="file-upload" className="sr-only">
        Choose a file to upload
      </label>
      <input
        id="file-upload"
        ref={inputRef}
        type="file"
        accept=".pdf,.docx"
        className="sr-only"
        onChange={(e) => handleFile(e.target.files?.[0])}
      />
      <button
        type="button"
        onClick={() => inputRef.current?.click()}
        className="rounded-md border border-slate-300 bg-white px-3 py-1.5 text-sm font-medium text-slate-700 hover:bg-slate-50"
      >
        Browse files
      </button>
    </div>
  );
}
