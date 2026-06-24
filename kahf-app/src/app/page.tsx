"use client";

import { useState } from "react";
import { DiscoveryGrid } from "@/components/DiscoveryGrid";
import { HeroEditorial } from "@/components/HeroEditorial";
import { LoadingState } from "@/components/LoadingState";
import { PhotoBoothStrip } from "@/components/PhotoBoothStrip";
import { SessionBar } from "@/components/SessionBar";
import {
  runDiscovery,
  wipeSession,
  type DiscoveryResponse,
} from "@/lib/api";

type Phase = "upload" | "loading" | "results" | "wiped";

export default function Home() {
  const [phase, setPhase] = useState<Phase>("upload");
  const [files, setFiles] = useState<File[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<DiscoveryResponse | null>(null);
  const [wiping, setWiping] = useState(false);

  const handleDiscover = async () => {
    if (files.length < 3) {
      setError("Please add at least 3 reference photos.");
      return;
    }
    setError(null);
    setPhase("loading");
    try {
      const response = await runDiscovery(files);
      setData(response);
      setPhase("results");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong.");
      setPhase("upload");
    }
  };

  const handleWipe = async () => {
    if (!data?.session.session_id) return;
    setWiping(true);
    try {
      await wipeSession(data.session.session_id);
      setData(null);
      setFiles([]);
      setPhase("wiped");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not wipe session.");
    } finally {
      setWiping(false);
    }
  };

  const reset = () => {
    setPhase("upload");
    setError(null);
    setData(null);
    setFiles([]);
  };

  return (
    <div className="relative min-h-screen bg-kahf-fantasy">
      <header className="sticky top-0 z-40 border-b-2 border-kahf-tobago bg-kahf-fantasy">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
          <div className="flex items-center gap-3">
            <span className="headline-display text-2xl text-kahf-tobago">Kahf</span>
            <span className="font-arabic text-xl font-bold text-kahf-rose" lang="ar" dir="rtl">
              كهف
            </span>
          </div>
          {phase === "results" && (
            <button
              type="button"
              onClick={reset}
              className="border-2 border-kahf-tobago px-4 py-1.5 font-sans text-xs font-bold uppercase tracking-wider text-kahf-tobago transition-colors hover:bg-kahf-tobago hover:text-kahf-fantasy"
            >
              New search
            </button>
          )}
        </div>
      </header>

      <main>
        {phase === "upload" && (
          <>
            <HeroEditorial />

            <div className="mx-auto max-w-6xl px-6 pb-20 pt-10">
              <div className="grid gap-10 lg:grid-cols-[1fr_0.8fr] lg:items-start">
                <PhotoBoothStrip
                  files={files}
                  onFilesChange={setFiles}
                  onSearch={handleDiscover}
                  canSearch={files.length >= 3}
                  error={error}
                />

                <aside className="space-y-5 lg:pt-2">
                  <div className="tape-poster border-2 border-kahf-tobago bg-kahf-tobago p-6 text-kahf-fantasy sm:p-8">
                    <p className="font-arabic text-right text-2xl leading-none text-kahf-rose" lang="ar" dir="rtl">
                      قبل الحجاب
                    </p>
                    <p className="font-sans text-[10px] font-bold uppercase tracking-[0.3em] text-kahf-vanilla">
                      How it works
                    </p>
                    <p className="headline-display mt-4 text-3xl leading-tight text-kahf-fantasy">
                      Still out there.
                    </p>
                    <p className="headline-script -mt-1 text-4xl text-kahf-rose">
                      Still yours to find.
                    </p>
                    <p className="mt-5 font-sans text-sm leading-relaxed text-kahf-vanilla">
                      Old photos of you without hijab may still be indexed on social
                      media, news sites, and blogs. We search for them, verify each
                      match, and hand the results back to you. What you do next is
                      entirely your choice.
                    </p>
                  </div>

                  <div className="border-2 border-kahf-tobago bg-kahf-rose p-5">
                    <p className="font-arabic text-center text-3xl text-kahf-tobago" lang="ar" dir="rtl">
                      حريم
                    </p>
                    <p className="mt-2 text-center font-sans text-xs font-bold uppercase tracking-[0.2em] text-kahf-tobago">
                      Your privacy, protected
                    </p>
                    <p className="mt-3 text-center font-sans text-sm leading-relaxed text-kahf-tobago/85">
                      Nothing stored after your session. Auto-wipe in 30 minutes.
                    </p>
                  </div>
                </aside>
              </div>
            </div>
          </>
        )}

        {phase === "loading" && (
          <div className="mx-auto max-w-6xl px-6 py-12">
            <LoadingState />
          </div>
        )}

        {phase === "results" && data && (
          <div className="mx-auto max-w-6xl space-y-10 px-6 py-12">
            <div className="border-b-2 border-kahf-tobago pb-8">
              <p className="font-sans text-[10px] font-bold uppercase tracking-[0.3em] text-kahf-sand">
                Your discoveries
              </p>
              <h2 className="headline-display mt-2 text-4xl text-kahf-tobago sm:text-5xl">
                What we found
              </h2>
              <p className="headline-script -mt-1 text-3xl text-kahf-rose">for you.</p>
            </div>

            <SessionBar
              sessionId={data.session.session_id}
              expiresAt={data.session.expires_at}
              onWipe={handleWipe}
              wiping={wiping}
            />

            {data.message && (
              <p className="border-2 border-kahf-tobago bg-kahf-vanilla px-5 py-4 font-sans text-sm text-kahf-tobago">
                {data.message}
              </p>
            )}

            <DiscoveryGrid results={data.results} />
          </div>
        )}

        {phase === "wiped" && (
          <section className="mx-auto max-w-lg px-6 py-28 text-center">
            <p className="font-arabic text-5xl text-kahf-rose" lang="ar" dir="rtl">
              انتهى
            </p>
            <h2 className="headline-display mt-4 text-3xl text-kahf-tobago">Session wiped</h2>
            <p className="mt-5 font-sans text-sm leading-relaxed text-kahf-tobago/70">
              Your photos and results are gone. Like it never happened.
            </p>
            <button
              type="button"
              onClick={reset}
              className="mt-10 border-2 border-kahf-tobago bg-kahf-tobago px-8 py-3 font-sans text-sm font-bold uppercase tracking-wider text-kahf-fantasy transition-colors hover:bg-kahf-rose hover:text-kahf-tobago"
            >
              Start fresh
            </button>
          </section>
        )}
      </main>

      <footer className="border-t-2 border-kahf-tobago bg-kahf-vanilla py-10 text-center">
        <p className="font-arabic text-lg text-kahf-tobago" lang="ar" dir="rtl">
          كهف
        </p>
        <p className="mt-1 font-sans text-[10px] font-bold uppercase tracking-[0.25em] text-kahf-tobago/60">
          Zero retention · 30 min sessions
        </p>
      </footer>
    </div>
  );
}
