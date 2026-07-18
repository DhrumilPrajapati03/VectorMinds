export default function ActionItemList({ items }: { items: string[] }) {
  if (items.length === 0) return null;

  return (
    <ol className="space-y-2">
      {items.map((item, i) => (
        <li key={i} className="flex items-start gap-3 text-sm text-slate-700">
          <span className="mt-0.5 inline-flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-slate-900 text-xs font-medium text-white">
            {i + 1}
          </span>
          {item}
        </li>
      ))}
    </ol>
  );
}
