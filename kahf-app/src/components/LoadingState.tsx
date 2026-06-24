"use client";

import { motion } from "framer-motion";

const STEPS = [
  "building your profile",
  "searching pre-hijab images",
  "verifying matches",
  "gathering context",
];

export function LoadingState() {
  return (
    <section className="relative mx-auto max-w-2xl py-16 text-center">
      <motion.div
        animate={{ rotate: [0, 2, -2, 0] }}
        transition={{ repeat: Infinity, duration: 4, ease: "easeInOut" }}
        className="tape-poster relative mx-auto mb-10 max-w-xs border-2 border-kahf-tobago bg-kahf-vanilla p-6"
      >
        <p className="font-arabic text-3xl text-kahf-rose" lang="ar" dir="rtl">
          بحث
        </p>
        <p className="headline-display mt-2 text-4xl text-kahf-tobago">…</p>
        <p className="headline-script text-3xl text-kahf-tobago">searching</p>
      </motion.div>

      <h2 className="headline-sans text-2xl text-kahf-tobago">Looking now</h2>
      <p className="mx-auto mt-4 max-w-md font-sans text-sm leading-relaxed text-kahf-tobago/70">
        Your photos stay in memory only. Everything wipes when you&apos;re done —
        or in 30 minutes.
      </p>

      <ul className="mx-auto mt-10 max-w-xs space-y-3 text-left">
        {STEPS.map((step, i) => (
          <motion.li
            key={step}
            initial={{ opacity: 0.3 }}
            animate={{ opacity: [0.35, 1, 0.35] }}
            transition={{ repeat: Infinity, duration: 2.4, delay: i * 0.5 }}
            className="flex items-center gap-3 font-sans text-sm lowercase tracking-wide text-kahf-tobago/70"
          >
            <span className="h-2 w-2 bg-kahf-rose" />
            {step}
          </motion.li>
        ))}
      </ul>
    </section>
  );
}
