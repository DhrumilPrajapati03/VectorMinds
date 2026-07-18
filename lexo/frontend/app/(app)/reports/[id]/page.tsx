import ActionItemList from "@/components/ActionItemList";
import Disclaimer from "@/components/Disclaimer";
import FlagCard from "@/components/FlagCard";
import MissingClauseList from "@/components/MissingClauseList";
import RiskBadge from "@/components/RiskBadge";
import { getReportById } from "@/lib/mock-data";

export default async function ReportPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const report = getReportById(id);
  const verifiedCount = report.flags.reduce(
    (count, flag) => count + flag.citations.filter((c) => c.verified).length,
    0,
  );
  const totalCitations = report.flags.reduce((count, flag) => count + flag.citations.length, 0);

  return (
    <div>
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold text-slate-900">{report.filename}</h1>
          <p className="text-sm capitalize text-slate-500">{report.docType} agreement</p>
        </div>
        <RiskBadge score={report.riskScore} />
      </div>

      <Disclaimer />

      <p className="mt-4 text-sm text-slate-500">
        {verifiedCount} of {totalCitations} citations verified against a real source.
      </p>

      <section className="mt-8">
        <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-slate-500">
          Flagged clauses
        </h2>
        <div className="space-y-3">
          {report.flags.map((flag, i) => (
            <FlagCard key={i} flag={flag} />
          ))}
        </div>
      </section>

      <section className="mt-8">
        <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-slate-500">
          Missing clauses
        </h2>
        <MissingClauseList items={report.missingClauses} />
      </section>

      <section className="mt-8">
        <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-slate-500">
          Action items
        </h2>
        <ActionItemList items={report.actionItems} />
      </section>
    </div>
  );
}
