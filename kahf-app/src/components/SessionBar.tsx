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
    <div className="flex flex-col gap-4 border-2 border-kahf-tobago bg-kahf-vanilla px-5 py-4 sm:flex-row sm:items-center sm:justify-between">
      <div className="font-sans text-sm text-kahf-tobago">
        <span className="font-bold uppercase tracking-wider">Private session</span>
        <span className="mx-2 text-kahf-sand">·</span>
        Auto-purge by {expires}
        <span className="mt-1 block font-mono text-[10px] text-kahf-tobago/45">
          {sessionId.slice(0, 14)}…
        </span>
      </div>
      <button
        type="button"
        onClick={onWipe}
        disabled={wiping}
        className="bg-kahf-tobago px-5 py-2.5 font-sans text-xs font-bold uppercase tracking-wider text-kahf-fantasy transition-colors hover:bg-kahf-rose hover:text-kahf-tobago disabled:opacity-50"
      >
        {wiping ? "Wiping…" : "Wipe session"}
      </button>
    </div>
  );
}
