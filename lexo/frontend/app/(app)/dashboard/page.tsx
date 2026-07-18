import Link from "next/link";
import DocumentCard from "@/components/DocumentCard";
import { mockDocuments } from "@/lib/mock-data";

export default function DashboardPage() {
  const documents = mockDocuments;

  return (
    <div>
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="font-serif text-2xl font-medium text-zinc-100">Your documents</h1>
          <p className="mt-1 text-sm text-zinc-500">Every agreement you&apos;ve uploaded and its risk report.</p>
        </div>
        <Link
          href="/upload"
          className="rounded-md bg-indigo-500 px-4 py-2 text-sm font-medium text-white transition hover:bg-indigo-400"
        >
          Upload new document
        </Link>
      </div>

      {documents.length === 0 ? (
        <div className="rounded-xl border border-dashed border-zinc-800 bg-zinc-900/50 p-12 text-center">
          <p className="text-zinc-400">No documents yet.</p>
          <Link href="/upload" className="mt-3 inline-block font-medium text-indigo-400 hover:text-indigo-300">
            Upload your first document
          </Link>
        </div>
      ) : (
        <div className="space-y-3">
          {documents.map((doc) => (
            <DocumentCard key={doc.id} doc={doc} />
          ))}
        </div>
      )}
    </div>
  );
}
