import type { DiscoveryResult } from "@/lib/api";
import { matchLabel } from "@/lib/api";

interface DiscoveryCardProps {
  result: DiscoveryResult;
}

function tierStyles(tier: DiscoveryResult["match_tier"]) {
  switch (tier) {
    case "high":
      return "bg-kahf-rose text-kahf-tobago border-kahf-tobago";
    case "medium":
      return "bg-kahf-vanilla text-kahf-tobago border-kahf-tobago";
    default:
      return "bg-kahf-sand text-kahf-tobago border-kahf-tobago";
  }
}

export function DiscoveryCard({ result }: DiscoveryCardProps) {
  const label = matchLabel(result.match_tier, result.confidence_score);

  return (
    <article className="tape-poster flex flex-col overflow-hidden border-2 border-kahf-tobago bg-kahf-paper transition-transform hover:-translate-y-1">
      <div className="relative aspect-[4/3] bg-kahf-vanilla">
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img
          src={result.thumbnail_url || result.image_url}
          alt={result.page_title || "Discovered image"}
          className="h-full w-full object-cover"
          onError={(e) => {
            (e.target as HTMLImageElement).style.display = "none";
          }}
        />
        <span
          className={`absolute left-3 top-3 border-2 px-3 py-1 font-sans text-[10px] font-bold uppercase tracking-wider ${tierStyles(result.match_tier)}`}
        >
          {label}
        </span>
      </div>

      <div className="flex flex-1 flex-col gap-3 p-5">
        <div className="flex flex-wrap items-center gap-2">
          <span className="bg-kahf-tobago px-3 py-0.5 font-sans text-[10px] font-bold uppercase tracking-wider text-kahf-fantasy">
            {result.platform}
          </span>
          {result.date_published && (
            <span className="font-sans text-xs text-kahf-tobago/50">
              {new Date(result.date_published).toLocaleDateString(undefined, {
                year: "numeric",
                month: "short",
              })}
            </span>
          )}
        </div>

        <h3 className="headline-display text-xl leading-snug text-kahf-tobago line-clamp-2">
          {result.page_title || "Untitled page"}
        </h3>

        <p className="flex-1 font-sans text-sm leading-relaxed text-kahf-tobago/65 line-clamp-3">
          {result.context_snippet || `Discovered via ${result.source_engine}`}
        </p>

        <a
          href={result.page_url}
          target="_blank"
          rel="noopener noreferrer"
          className="mt-auto inline-flex w-fit border-2 border-kahf-tobago px-5 py-2 font-sans text-xs font-bold uppercase tracking-wider text-kahf-tobago transition-colors hover:bg-kahf-tobago hover:text-kahf-fantasy"
        >
          Review link
        </a>
      </div>
    </article>
  );
}
