import { ProcessingStage } from "@/lib/types";

const STAGES: { key: ProcessingStage; label: string }[] = [
  { key: "extracting", label: "Extracting" },
  { key: "analyzing", label: "Analyzing" },
  { key: "grounding", label: "Grounding" },
];

export default function ProcessingStepper({ current }: { current: ProcessingStage }) {
  const currentIndex = STAGES.findIndex((s) => s.key === current);

  return (
    <div className="flex items-center">
      {STAGES.map((stage, i) => {
        const isComplete = i < currentIndex;
        const isCurrent = i === currentIndex;
        return (
          <div key={stage.key} className="flex flex-1 items-center last:flex-none">
            <div className="flex flex-col items-center gap-2">
              <div
                className={`flex h-8 w-8 items-center justify-center rounded-full text-sm font-medium ${
                  isComplete
                    ? "bg-slate-900 text-white"
                    : isCurrent
                      ? "bg-sky-600 text-white animate-pulse"
                      : "bg-slate-100 text-slate-400"
                }`}
              >
                {isComplete ? "✓" : i + 1}
              </div>
              <span
                className={`text-xs font-medium ${isCurrent ? "text-sky-700" : "text-slate-500"}`}
              >
                {stage.label}
              </span>
            </div>
            {i < STAGES.length - 1 && (
              <div className={`mx-2 h-0.5 flex-1 ${isComplete ? "bg-slate-900" : "bg-slate-200"}`} />
            )}
          </div>
        );
      })}
    </div>
  );
}
