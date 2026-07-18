import { MissingClause } from "@/lib/types";

export default function MissingClauseList({ items }: { items: MissingClause[] }) {
  if (items.length === 0) return null;

  return (
    <div className="space-y-2">
      {items.map((item, i) => (
        <div
          key={i}
          className="rounded-lg border border-dashed border-slate-300 bg-slate-50 p-4"
        >
          <p className="font-medium text-slate-900">{item.name}</p>
          <p className="mt-1 text-sm text-slate-600">{item.recommendation}</p>
        </div>
      ))}
    </div>
  );
}
