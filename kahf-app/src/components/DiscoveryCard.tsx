import type { DiscoveryResult } from "@/lib/api";
import { matchLabel } from "@/lib/api";

interface DiscoveryCardProps {
  result: DiscoveryResult;
}

function tierStyles(tier: DiscoveryResult["match_tier"]) {
  switch (tier) {
    case "high":
      return "bg-kahf-mountain/25 text-kahf-coffee border-kahf-mountain/50";
    case "medium":
      return "bg-kahf-mojave/40 text-kahf-coffee border-kahf-mojave/60";
    default:
      return "bg-kahf-almond text-kahf-coffee border-kahf-almond";
  }
}

export function DiscoveryCard({ result }: DiscoveryCardProps) {
  const label = matchLabel(result.match_tier, result.confidence_score);

  return (
    <article className="tape-poster flex flex-col overflow-hidden rounded-sm border border-kahf-coffee/10 bg-kahf-almond/60 transition-transform hover:-translate-y-1">
      <div className="relative aspect-[4/3] bg-kahf-cream">
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img
          src={result.thumbnail_url || result.image_url}
          alt={result.page_title || "Discovered image"}
          className="h-full w-full object-cover sepia-[.2]"
          onError={(e) => {
            (e.target as HTMLImageElement).style.display = "none";
          }}
        />
        <span
          className={`body-sans absolute left-3 top-3 rounded-full border px-3 py-1 text-[10px] font-semibold uppercase tracking-wider ${tierStyles(result.match_tier)}`}
        >
          {label}
        </span>
      </div>

      <div className="flex flex-1 flex-col gap-3 p-5">
        <div className="flex flex-wrap items-center gap-2">
          <span className="body-sans rounded-full bg-kahf-coffee/10 px-3 py-0.5 text-[10px] font-medium uppercase tracking-wider text-kahf-coffee">
            {result.platform}
          </span>
          {result.date_published && (
            <span className="body-sans text-xs text-kahf-mountain">
              {new Date(result.date_published).toLocaleDateString(undefined, {
                year: "numeric",
                month: "short",
              })}
            </span>
          )}
        </div>

        <h3 className="headline-display text-xl leading-snug text-kahf-coffee line-clamp-2">
          {result.page_title || "Untitled page"}
        </h3>

        <p className="body-sans flex-1 text-sm leading-relaxed text-kahf-coffee/60 line-clamp-3">
          {result.context_snippet || `Discovered via ${result.source_engine}`}
        </p>

        <a
          href={result.page_url}
          target="_blank"
          rel="noopener noreferrer"
          className="body-sans mt-auto inline-flex w-fit items-center justify-center rounded-full border border-kahf-coffee/25 px-5 py-2 text-xs font-semibold uppercase tracking-wider text-kahf-coffee transition-colors hover:border-kahf-coffee hover:bg-kahf-coffee hover:text-kahf-almond"
        >
          Review link
        </a>
      </div>
    </article>
  );
}
