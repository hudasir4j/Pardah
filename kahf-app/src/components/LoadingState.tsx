"use client";

import { motion } from "framer-motion";

const STEPS = [
  "building your private profile",
  "searching the open web",
  "verifying each match",
  "gathering context gently",
];

export function LoadingState() {
  return (
    <section className="relative mx-auto max-w-2xl py-16 text-center">
      <div
        className="absolute inset-x-8 top-0 h-48 rounded-full opacity-25 blur-3xl"
        style={{ background: "radial-gradient(circle, #7D5E3C 0%, transparent 70%)" }}
        aria-hidden
      />

      <motion.div
        animate={{ rotate: [0, 2, -2, 0] }}
        transition={{ repeat: Infinity, duration: 4, ease: "easeInOut" }}
        className="tape-poster relative mx-auto mb-10 max-w-xs rotate-[-1deg] bg-kahf-almond p-6"
      >
        <p className="headline-display text-4xl text-kahf-coffee">…</p>
        <p className="headline-script mt-2 text-3xl text-kahf-berkeley">searching</p>
      </motion.div>

      <h2 className="headline-sans text-2xl text-kahf-coffee">We&apos;re looking with care</h2>
      <p className="body-sans mx-auto mt-4 max-w-md text-sm leading-relaxed text-kahf-coffee/65">
        Your photos stay encrypted in memory. Everything wipes when you&apos;re done —
        or in 30 minutes, whichever comes first.
      </p>

      <ul className="mx-auto mt-10 max-w-xs space-y-3 text-left">
        {STEPS.map((step, i) => (
          <motion.li
            key={step}
            initial={{ opacity: 0.3 }}
            animate={{ opacity: [0.35, 1, 0.35] }}
            transition={{ repeat: Infinity, duration: 2.4, delay: i * 0.5 }}
            className="body-sans flex items-center gap-3 text-sm lowercase tracking-wide text-kahf-coffee/70"
          >
            <span className="h-2 w-2 rounded-full bg-kahf-berkeley" />
            {step}
          </motion.li>
        ))}
      </ul>
    </section>
  );
}
