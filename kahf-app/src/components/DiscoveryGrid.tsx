import type { DiscoveryResult } from "@/lib/api";
import { DiscoveryCard } from "./DiscoveryCard";

interface DiscoveryGridProps {
  results: DiscoveryResult[];
}

export function DiscoveryGrid({ results }: DiscoveryGridProps) {
  if (results.length === 0) {
    return (
      <div className="tape-poster rounded-sm border border-kahf-coffee/10 bg-kahf-almond/50 px-8 py-20 text-center">
        <p className="headline-script text-4xl text-kahf-berkeley">nothing here.</p>
        <h2 className="headline-display mt-3 text-2xl text-kahf-coffee">
          No high-confidence matches
        </h2>
        <p className="body-sans mx-auto mt-4 max-w-md text-sm leading-relaxed text-kahf-coffee/60">
          We didn&apos;t find anything above our 85% threshold. That can be good news —
          or try reference photos with more varied angles, from before and after hijab.
        </p>
      </div>
    );
  }

  return (
    <section>
      <p className="body-sans mb-8 text-sm text-kahf-mountain">
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
