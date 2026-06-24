"use client";

import { motion, useInView, useScroll, useSpring, useTransform } from "framer-motion";
import { useRef, useState } from "react";
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
  const howItWorksRef = useRef<HTMLElement | null>(null);
  const boothRef = useRef<HTMLElement | null>(null);
  const darkMasthead = useInView(howItWorksRef, {
    margin: "-72px 0px -78% 0px",
  });

  const { scrollYProgress: howItWorksProgress } = useScroll({
    target: howItWorksRef,
    offset: ["start 85%", "end 20%"],
  });
  const { scrollYProgress: boothProgress } = useScroll({
    target: boothRef,
    offset: ["start 85%", "end 20%"],
  });

  const howItWorksSpring = useSpring(howItWorksProgress, {
    stiffness: 110,
    damping: 24,
    mass: 0.8,
  });
  const boothSpring = useSpring(boothProgress, {
    stiffness: 120,
    damping: 26,
    mass: 0.9,
  });

  const orbitY = useTransform(howItWorksSpring, [0, 1], [56, -36]);
  const orbitRotate = useTransform(howItWorksSpring, [0, 1], [-5, 7]);
  const introY = useTransform(howItWorksSpring, [0, 1], [36, 0]);
  const boothY = useTransform(boothSpring, [0, 1], [44, 0]);
  const boothScale = useTransform(boothSpring, [0, 1], [0.965, 1]);

  const handleDiscover = async () => {
    if (files.length < 3) {
      setError("Please add at least 3 reference photos to continue.");
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

  const scrollToSection = (id: string) => {
    if (typeof window === "undefined") return;
    const target = document.getElementById(id);
    if (!target) return;

    const isDesktop = window.innerWidth >= 1024;
    const mastheadOffset =
      id === "how-it-works"
        ? isDesktop
          ? 64
          : 56
        : id === "start-search"
          ? isDesktop
            ? 76
            : 64
          : isDesktop
            ? 132
            : 112;
    const top = target.getBoundingClientRect().top + window.scrollY - mastheadOffset;

    window.scrollTo({
      top,
      behavior: "smooth",
    });
  };

  return (
    <div className="relative min-h-screen">
      <header className="fixed inset-x-0 top-4 z-40 px-4 sm:px-6">
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, ease: [0.22, 1, 0.36, 1] }}
          className={`editorial-masthead mx-auto flex max-w-5xl items-center justify-between gap-6 rounded-full px-5 py-3 transition-colors duration-500 sm:px-6 ${
            darkMasthead ? "text-kahf-cream" : "text-kahf-coffee"
          }`}
        >
          <div className="min-w-0">
            <span className="headline-display block text-[1.7rem] leading-none tracking-tight sm:text-[1.9rem]">
              Kahf
            </span>
          </div>

          <nav className="hidden items-center gap-5 sm:flex">
            <button
              type="button"
              onClick={() => scrollToSection("hero")}
              className={`body-sans text-[10px] font-medium uppercase tracking-[0.26em] transition-colors ${
                darkMasthead
                  ? "text-kahf-cream/72 hover:text-kahf-cream"
                  : "text-kahf-coffee/56 hover:text-kahf-berkeley"
              }`}
            >
              Cover
            </button>
            <button
              type="button"
              onClick={() => scrollToSection("how-it-works")}
              className={`body-sans text-[10px] font-medium uppercase tracking-[0.26em] transition-colors ${
                darkMasthead
                  ? "text-kahf-cream/72 hover:text-kahf-cream"
                  : "text-kahf-coffee/56 hover:text-kahf-berkeley"
              }`}
            >
              How it works
            </button>
            <button
              type="button"
              onClick={() => scrollToSection("start-search")}
              className={`body-sans text-[10px] font-medium uppercase tracking-[0.26em] transition-colors ${
                darkMasthead
                  ? "text-kahf-cream/72 hover:text-kahf-cream"
                  : "text-kahf-coffee/56 hover:text-kahf-berkeley"
              }`}
            >
              Start search
            </button>
          </nav>

          <div className="flex items-center gap-3">
            <span
              className={`hidden h-px w-10 transition-colors duration-500 sm:block ${
                darkMasthead ? "bg-kahf-cream/22" : "bg-kahf-coffee/12"
              }`}
              aria-hidden
            />
            {phase === "results" ? (
              <button
                type="button"
                onClick={reset}
                className={`body-sans text-[10px] font-medium uppercase tracking-[0.28em] transition-colors ${
                  darkMasthead
                    ? "text-kahf-cream/78 hover:text-kahf-cream"
                    : "text-kahf-coffee/68 hover:text-kahf-berkeley"
                }`}
              >
                New search
              </button>
            ) : (
              <button
                type="button"
                onClick={() => scrollToSection("start-search")}
                className={`body-sans text-[10px] font-medium uppercase tracking-[0.28em] transition-colors ${
                  darkMasthead
                    ? "text-kahf-cream/78 hover:text-kahf-cream"
                    : "text-kahf-coffee/68 hover:text-kahf-berkeley"
                }`}
              >
                Open booth
              </button>
            )}
          </div>
        </motion.div>
      </header>

      <main>
        {phase === "upload" && (
          <>
            <div id="hero" className="scroll-mt-28 sm:scroll-mt-32">
              <HeroEditorial />
            </div>

            <section
              ref={howItWorksRef}
              className="how-it-works-band marquee-fullbleed relative overflow-hidden py-24 sm:py-28 lg:min-h-[clamp(52rem,78vh,64rem)] lg:py-36"
            >
              <div
                id="how-it-works"
                className="absolute top-10 scroll-mt-28 sm:top-12 sm:scroll-mt-32 lg:top-20 lg:scroll-mt-36"
                aria-hidden
              />
              <motion.div
                aria-hidden
                className="how-it-works-orbit"
                style={{ y: orbitY, rotate: orbitRotate }}
              />
              <motion.div
                className="relative z-10 mx-auto max-w-6xl px-6"
                style={{ y: introY }}
              >
                <div className="max-w-2xl">
                  <p className="body-sans text-[10px] font-medium uppercase tracking-[0.32em] text-kahf-mojave/80">
                    How it works
                  </p>
                  <h2 className="headline-display mt-4 text-4xl text-kahf-cream sm:text-5xl lg:text-6xl">
                    We go looking.
                  </h2>
                  <p className="headline-script -mt-1 text-4xl text-kahf-mojave sm:text-5xl">
                    gently, but thoroughly.
                  </p>
                  <p className="body-sans mt-5 max-w-xl text-sm leading-relaxed text-kahf-cream/72 sm:text-base">
                    Pre-hijab photos can linger across old social profiles, blogs, school
                    pages, and reposts. Kahf helps you surface them, confirm them, and move
                    toward removal.
                  </p>
                </div>

                <div className="mt-12 grid gap-5 lg:grid-cols-3">
                  {[
                    {
                      step: "01",
                      title: "Give us a few anchors.",
                      text: "Upload a mix of before-hijab and current photos so the search has something real to follow.",
                    },
                    {
                      step: "02",
                      title: "We scan what still lingers.",
                      text: "Kahf searches for lookalike photos online, then verifies which matches are actually you.",
                    },
                    {
                      step: "03",
                      title: "You decide what happens next.",
                      text: "Review what was found and use that clarity to begin takedown requests with confidence.",
                    },
                  ].map((item, index) => (
                    <motion.article
                      key={item.step}
                      initial={{ opacity: 0, y: 28 }}
                      whileInView={{ opacity: 1, y: 0 }}
                      viewport={{ once: true, amount: 0.35 }}
                      transition={{
                        delay: index * 0.08,
                        duration: 0.7,
                        ease: [0.22, 1, 0.36, 1],
                      }}
                      className="how-it-works-card rounded-[1.4rem] border border-kahf-cream/10 px-6 py-7"
                    >
                      <p className="body-sans text-[10px] font-medium uppercase tracking-[0.28em] text-kahf-mojave/70">
                        {item.step}
                      </p>
                      <h3 className="headline-display mt-4 text-2xl leading-tight text-kahf-cream">
                        {item.title}
                      </h3>
                      <p className="body-sans mt-4 text-sm leading-relaxed text-kahf-cream/68">
                        {item.text}
                      </p>
                    </motion.article>
                  ))}
                </div>
              </motion.div>
            </section>

            <section ref={boothRef} className="relative overflow-hidden py-16 sm:py-20">
              <div
                id="start-search"
                className="absolute top-10 scroll-mt-28 sm:top-12 sm:scroll-mt-32 lg:top-20 lg:scroll-mt-36"
                aria-hidden
              />
              <motion.div
                className="mx-auto max-w-6xl px-6"
                style={{ y: boothY, scale: boothScale }}
              >
                <div className="mb-8 max-w-2xl">
                  <p className="body-sans text-[10px] font-medium uppercase tracking-[0.32em] text-kahf-mountain">
                    Start the search
                  </p>
                  <h2 className="headline-display mt-4 text-4xl text-kahf-coffee sm:text-5xl">
                    Build your reference strip.
                  </h2>
                  <p className="headline-script -mt-1 text-4xl text-kahf-berkeley sm:text-5xl">
                    then let it roll.
                  </p>
                  <p className="body-sans mt-5 max-w-xl text-sm leading-relaxed text-kahf-coffee/68 sm:text-base">
                    Add at least three photos. A mix of before-hijab and current images gives
                    Kahf the clearest trail to follow.
                  </p>
                </div>

                <motion.div
                  initial={{ opacity: 0, y: 24 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true, amount: 0.3 }}
                  transition={{ duration: 0.75, ease: [0.22, 1, 0.36, 1] }}
                  className="upload-stage rounded-[2rem] border border-kahf-coffee/10 px-5 py-6 shadow-[0_18px_60px_rgba(64,38,21,0.08)] sm:px-8 sm:py-8"
                >
                  <PhotoBoothStrip files={files} onFilesChange={setFiles} />

                  {error && (
                    <p className="body-sans mt-4 text-center text-sm text-kahf-berkeley" role="alert">
                      {error}
                    </p>
                  )}

                  <div className="mt-6 flex flex-col items-center gap-2">
                    <div className="space-y-2 text-center">
                      <p className="body-sans text-sm leading-relaxed text-kahf-coffee/60">
                        {files.length < 3 ? (
                          <>
                            <span className="headline-script text-xl text-kahf-berkeley">
                              {3 - files.length} more
                            </span>{" "}
                            to begin — include a mix of before-hijab and current photos from
                            different angles
                          </>
                        ) : (
                          "Ready to search. Add more references if you want stronger matching, or tap × to remove."
                        )}
                      </p>
                      <p className="body-sans text-[11px] text-kahf-mountain">
                        {files.length}/5 photos · used to scan for old images of you · wiped
                        when you&apos;re done
                      </p>
                    </div>

                    <button
                      type="button"
                      onClick={handleDiscover}
                      disabled={files.length < 3}
                      className="headline-display rounded-full bg-kahf-berkeley px-12 py-3.5 text-xl tracking-tight text-kahf-almond shadow-lg shadow-kahf-coffee/15 transition-all hover:bg-kahf-coffee disabled:cursor-not-allowed disabled:opacity-35 disabled:shadow-none"
                    >
                      Find photos of me
                    </button>
                    <p className="body-sans text-xs text-kahf-mountain">
                      {files.length}/5 photos ·{" "}
                      {files.length < 3 ? `${3 - files.length} more needed` : "ready"}
                    </p>
                  </div>
                </motion.div>
              </motion.div>
            </section>
          </>
        )}

        {phase === "loading" && (
          <div className="mx-auto max-w-6xl px-6 py-12">
            <LoadingState />
          </div>
        )}

        {phase === "results" && data && (
          <div className="mx-auto max-w-6xl space-y-10 px-6 py-12">
            <div className="border-b border-kahf-coffee/10 pb-8">
              <p className="body-sans text-[10px] font-medium uppercase tracking-[0.3em] text-kahf-mountain">
                Your discoveries
              </p>
              <h2 className="headline-display mt-2 text-4xl text-kahf-coffee sm:text-5xl">
                What we found
              </h2>
              <p className="headline-script -mt-1 text-3xl text-kahf-berkeley">for you.</p>
            </div>

            <SessionBar
              sessionId={data.session.session_id}
              expiresAt={data.session.expires_at}
              onWipe={handleWipe}
              wiping={wiping}
            />

            {data.message && (
              <p className="body-sans rounded-sm border border-kahf-mojave/50 bg-kahf-mojave/25 px-5 py-4 text-sm text-kahf-coffee/80">
                {data.message}
              </p>
            )}

            <DiscoveryGrid results={data.results} />
          </div>
        )}

        {phase === "wiped" && (
          <section className="mx-auto max-w-lg px-6 py-28 text-center">
            <p className="headline-script text-5xl text-kahf-berkeley">gone.</p>
            <h2 className="headline-display mt-4 text-3xl text-kahf-coffee">Session wiped</h2>
            <p className="body-sans mt-5 text-sm leading-relaxed text-kahf-coffee/65">
              Your reference photos, biometric templates, and search results have been
              permanently deleted. Like it never happened.
            </p>
            <button
              type="button"
              onClick={reset}
              className="body-sans mt-10 rounded-full border-2 border-kahf-coffee/25 px-8 py-3 text-sm font-medium text-kahf-coffee transition-colors hover:border-kahf-berkeley hover:text-kahf-berkeley"
            >
              Start fresh
            </button>
          </section>
        )}
      </main>

      <footer className="border-t border-kahf-coffee/10 py-10 text-center">
        <p className="headline-script text-xl text-kahf-berkeley/70">gently, always.</p>
        <p className="body-sans mt-2 text-[10px] uppercase tracking-[0.2em] text-kahf-mountain">
          Photo search · match review · session wipe in 30 minutes
        </p>
      </footer>
    </div>
  );
}
