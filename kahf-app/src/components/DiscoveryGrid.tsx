import type { DiscoveryResult } from "@/lib/api";
import { DiscoveryCard } from "./DiscoveryCard";

interface DiscoveryGridProps {
  results: DiscoveryResult[];
}

export function DiscoveryGrid({ results }: DiscoveryGridProps) {
  if (results.length === 0) {
    return (
      <div className="tape-poster border-2 border-kahf-tobago bg-kahf-vanilla px-8 py-20 text-center">
        <p className="font-arabic text-4xl text-kahf-rose" lang="ar" dir="rtl">
          لا شيء
        </p>
        <h2 className="headline-display mt-3 text-2xl text-kahf-tobago">
          No high-confidence matches
        </h2>
        <p className="mx-auto mt-4 max-w-md font-sans text-sm leading-relaxed text-kahf-tobago/65">
          Nothing passed our 85% threshold. That can be good news — or try
          reference photos with more varied angles.
        </p>
      </div>
    );
  }

  return (
    <section>
      <p className="mb-8 font-sans text-sm font-semibold text-kahf-tobago/60">
        {results.length} result{results.length === 1 ? "" : "s"} passed verification
      </p>

      <div className="columns-1 gap-6 sm:columns-2 xl:columns-3 [&>article]:mb-6 [&>article]:break-inside-avoid">
        {results.map((result) => (
          <DiscoveryCard key={result.id} result={result} />
        ))}
      </div>
    </section>
  );
}
