const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export type MatchTier = "high" | "medium" | "low";

export interface DiscoveryResult {
  id: string;
  image_url: string;
  thumbnail_url?: string | null;
  page_url: string;
  confidence_score: number;
  match_tier: MatchTier;
  platform: string;
  page_title?: string | null;
  date_published?: string | null;
  context_snippet?: string | null;
  source_engine: string;
  scraped: boolean;
}

export interface SessionSummary {
  session_id: string;
  status: string;
  created_at: string;
  expires_at: string;
  reference_count: number;
  result_count: number;
}

export interface DiscoveryResponse {
  session: SessionSummary;
  results: DiscoveryResult[];
  engines_used: string[];
  message?: string | null;
}

export async function runDiscovery(files: File[]): Promise<DiscoveryResponse> {
  const formData = new FormData();
  files.forEach((file) => formData.append("files", file));

  const res = await fetch(`${API_BASE}/api/v1/discover`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Discovery search failed. Please try again.");
  }

  return res.json();
}

export async function wipeSession(sessionId: string): Promise<void> {
  const res = await fetch(`${API_BASE}/api/v1/session/${sessionId}/wipe`, {
    method: "POST",
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || "Could not wipe session.");
  }
}

export function matchLabel(tier: MatchTier, score: number): string {
  if (tier === "high" || score >= 85) return "High Match";
  if (tier === "medium") return "Possible Match";
  return "Low Match";
}
