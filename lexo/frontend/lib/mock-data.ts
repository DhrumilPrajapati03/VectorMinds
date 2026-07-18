// Static placeholder data so the UI can be viewed before the backend pipeline
// (upload/analyze/reports) is wired up. Replace with real `apiFetch` calls
// once those endpoints exist. TODO: remove once backend is live.
import { DocumentSummary, Report } from "./types";

export const mockDocuments: DocumentSummary[] = [
  {
    id: "doc-1",
    filename: "Andheri_Flat_Lease.pdf",
    docType: "rental",
    status: "analyzed",
    riskScore: "red",
    createdAt: "2026-07-15T10:20:00Z",
  },
  {
    id: "doc-2",
    filename: "Offer_Letter_Infosys.pdf",
    docType: "employment",
    status: "analyzed",
    riskScore: "yellow",
    createdAt: "2026-07-14T09:05:00Z",
  },
  {
    id: "doc-3",
    filename: "PG_Agreement_Koramangala.docx",
    docType: "rental",
    status: "processing",
    createdAt: "2026-07-16T18:40:00Z",
  },
  {
    id: "doc-4",
    filename: "Consulting_Contract_Draft.pdf",
    docType: "employment",
    status: "analyzed",
    riskScore: "green",
    createdAt: "2026-07-10T14:00:00Z",
  },
];

export const mockReport: Report = {
  id: "report-1",
  documentId: "doc-1",
  filename: "Andheri_Flat_Lease.pdf",
  docType: "rental",
  riskScore: "red",
  flags: [
    {
      clause: "Clause 4 — Security Deposit",
      issue:
        "The deposit is set at 10 months' rent, well above the typical 2–3 month range, with no clear timeline for return after move-out.",
      severity: "high",
      citations: [
        {
          text: "Model Tenancy Act caps security deposits at 2 months' rent for residential lets.",
          verified: true,
          sourceTitle: "Model Tenancy Act, 2021 — Section 8",
          sourceUrl: "https://example.gov.in/model-tenancy-act",
        },
      ],
    },
    {
      clause: "Clause 9 — Lock-in Period",
      issue:
        "An 11-month lock-in with no exit option forfeits the entire deposit if the tenant leaves early for any reason, including unsafe conditions.",
      severity: "high",
      citations: [
        {
          text: "General principle: lock-in clauses should not override a tenant's right to exit for landlord-caused breaches.",
          verified: false,
        },
      ],
    },
    {
      clause: "Clause 12 — Maintenance",
      issue:
        "All maintenance, including structural repairs, is assigned to the tenant, which is unusual for a long-term lease.",
      severity: "medium",
      citations: [
        {
          text: "Structural repair obligations typically remain with the landlord/owner under standard rental practice.",
          verified: false,
        },
      ],
    },
  ],
  missingClauses: [
    {
      name: "Notice period for rent increase",
      recommendation:
        "Add a clause requiring at least 1–2 months' written notice before any rent revision.",
    },
    {
      name: "Deposit return timeline",
      recommendation:
        "Specify a concrete number of days (e.g. 30) for the deposit to be returned after move-out, minus documented deductions.",
    },
  ],
  actionItems: [
    "Ask the landlord to reduce the security deposit to 2–3 months' rent before signing.",
    "Request a written deposit-return timeline to be added to the agreement.",
    "Negotiate an exit clause for early termination due to landlord-caused issues.",
  ],
};

export function getDocumentById(id: string): DocumentSummary {
  return (
    mockDocuments.find((doc) => doc.id === id) ?? {
      id,
      filename: "Untitled_Document.pdf",
      docType: "rental",
      status: "processing",
      createdAt: new Date().toISOString(),
    }
  );
}

export function getReportById(id: string): Report {
  return { ...mockReport, id };
}
