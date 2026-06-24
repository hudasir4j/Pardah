"use client";

import { motion } from "framer-motion";
import { ScrapbookPolaroid, type ScrapbookPose } from "@/components/ScrapbookPolaroid";

const FLOAT_LABELS = [
  "find old photos",
  "before hijab",
  "verify matches",
  "track where they live",
  "prepare takedowns",
  "bring them back to you",
];

const POLAROID_LAYOUT = [
  {
    src: "/inspo/kahf-hero.png",
    right: "1rem",
    top: "0.5rem",
    width: 160,
    holdMs: 1000,
    startDelayMs: 0,
    poses: [
      { x: 0, y: 0, rotate: -6, scale: 1 },
      { x: -2, y: -4, rotate: -4.5, scale: 1 },
      { x: 3, y: 2, rotate: -7.2, scale: 1 },
      { x: -1, y: -3, rotate: -5.8, scale: 1.01 },
      { x: 2, y: 3, rotate: -6.8, scale: 1 },
    ] satisfies ScrapbookPose[],
  },
  {
    src: "/inspo/kahf-hero-2.png",
    right: "11.5rem",
    top: "4.5rem",
    width: 160,
    holdMs: 1400,
    startDelayMs: 400,
    poses: [
      { x: 0, y: 0, rotate: 5, scale: 1 },
      { x: 3, y: -3, rotate: 6.5, scale: 1 },
      { x: -2, y: 2, rotate: 3.8, scale: 1.01 },
      { x: 2, y: -2, rotate: 5.6, scale: 1 },
      { x: -3, y: 3, rotate: 4.2, scale: 1 },
    ] satisfies ScrapbookPose[],
  },
  {
    src: "/inspo/kahf-hero-3.png",
    right: "2rem",
    top: "12.75rem",
    width: 160,
    holdMs: 1350,
    startDelayMs: 800,
    poses: [
      { x: 0, y: 0, rotate: -3, scale: 1 },
      { x: -3, y: 2, rotate: -1.5, scale: 1 },
      { x: 2, y: -3, rotate: -4.2, scale: 1.01 },
      { x: -2, y: -2, rotate: -2.8, scale: 1 },
      { x: 3, y: 2, rotate: -3.6, scale: 1 },
    ] satisfies ScrapbookPose[],
  },
];

export function HeroEditorial() {
  return (
    <>
      <section className="relative w-full overflow-hidden pb-10">
        <div className="hero-mountain-wash" aria-hidden />

        <div className="relative z-10 mx-auto max-w-6xl px-6 pb-4 pt-18 lg:pt-24">
          <div className="relative grid gap-10 lg:grid-cols-2 lg:items-center lg:gap-8">
            <div className="relative z-10 lg:max-w-[34rem]">
              <motion.h1
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.05 }}
                className="headline-display text-[clamp(3.4rem,10vw,6.8rem)] text-kahf-coffee"
              >
                YOU COVERED.
              </motion.h1>
              <div className="relative -mt-2 sm:-mt-3">
                <motion.span
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: 0.12 }}
                  className="headline-script block text-[clamp(2.9rem,7.4vw,5.2rem)] leading-[0.88] text-kahf-berkeley"
                >
                  the internet didn&apos;t.
                </motion.span>
                <motion.p
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 0.22 }}
                  className="body-sans mt-3 max-w-sm text-sm leading-relaxed text-kahf-coffee/72 sm:text-base"
                >
                  Kahf finds your pre-hijab photos online and helps you take the next step.
                </motion.p>
              </div>
            </div>

            <div className="relative hidden min-h-[390px] lg:block lg:w-full" aria-hidden>
              <div className="relative w-full max-w-[28rem]">
              {POLAROID_LAYOUT.map((p) => (
                <ScrapbookPolaroid
                  key={p.src}
                  src={p.src}
                  poses={p.poses}
                  holdMs={p.holdMs}
                  startDelayMs={p.startDelayMs}
                  style={{
                    right: p.right,
                    top: p.top,
                    width: p.width,
                  }}
                />
              ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      <div className="marquee-fullbleed relative z-10 overflow-hidden border-y border-kahf-coffee/10 bg-kahf-cream py-3.5">
        <div className="marquee-track flex gap-16 whitespace-nowrap px-4">
          {[...FLOAT_LABELS, ...FLOAT_LABELS, ...FLOAT_LABELS].map((label, i) => (
            <span key={`${label}-${i}`} className="float-label text-sm">
              {label} ·
            </span>
          ))}
        </div>
      </div>
    </>
  );
}
