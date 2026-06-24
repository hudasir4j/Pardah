"use client";

interface SessionBarProps {
  sessionId: string;
  expiresAt: string;
  onWipe: () => void;
  wiping?: boolean;
}

export function SessionBar({ sessionId, expiresAt, onWipe, wiping }: SessionBarProps) {
  const expires = new Date(expiresAt).toLocaleTimeString(undefined, {
    hour: "numeric",
    minute: "2-digit",
  });

  return (
    <div className="flex flex-col gap-4 rounded-sm border border-kahf-mountain/35 bg-kahf-mountain/12 px-5 py-4 sm:flex-row sm:items-center sm:justify-between">
      <div className="body-sans text-sm text-kahf-coffee/75">
        <span className="font-semibold uppercase tracking-wider text-kahf-coffee">
          Private session
        </span>
        <span className="mx-2 text-kahf-coffee/25">·</span>
        Auto-purge by {expires}
        <span className="mt-1 block font-mono text-[10px] text-kahf-mountain">
          {sessionId.slice(0, 14)}…
        </span>
      </div>
      <button
        type="button"
        onClick={onWipe}
        disabled={wiping}
        className="body-sans rounded-full bg-kahf-coffee px-5 py-2.5 text-xs font-semibold uppercase tracking-wider text-kahf-almond transition-opacity hover:opacity-85 disabled:opacity-50"
      >
        {wiping ? "Wiping…" : "Wipe session"}
      </button>
    </div>
  );
}
