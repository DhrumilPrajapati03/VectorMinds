export type DocType = "rental" | "employment";
export type DocumentStatus = "uploaded" | "processing" | "analyzed";
export type RiskScore = "green" | "yellow" | "red";
export type Severity = "low" | "medium" | "high";
export type ProcessingStage = "extracting" | "analyzing" | "grounding";

export type DocumentSummary = {
  id: string;
  filename: string;
  docType: DocType;
  status: DocumentStatus;
  riskScore?: RiskScore;
  createdAt: string;
};

// TODO: align with backend once `citation: str` becomes nested `citations[]` (SYSTEM_DESIGN.md §5)
export type Citation = {
  text: string;
  verified: boolean;
  sourceTitle?: string;
  sourceUrl?: string;
};

export type Flag = {
  clause: string;
  issue: string;
  severity: Severity;
  citations: Citation[];
};

export type MissingClause = {
  name: string;
  recommendation: string;
};

export type Report = {
  id: string;
  documentId: string;
  filename: string;
  docType: DocType;
  riskScore: RiskScore;
  flags: Flag[];
  missingClauses: MissingClause[];
  actionItems: string[];
};
