"use client";

import { motion } from "framer-motion";

const FLOAT_LABELS = [
  "قبل الحجاب",
  "خصوصية",
  "حريم",
  "memory only",
  "wiped clean",
];

export function HeroEditorial() {
  return (
    <section className="relative overflow-hidden bg-kahf-fantasy">
      {/* Solid editorial block — no gradient */}
      <div
        className="absolute right-0 top-0 hidden h-full w-[38%] bg-kahf-rose lg:block"
        aria-hidden
      />
      <div
        className="absolute right-0 top-0 h-48 w-full bg-kahf-tobago lg:hidden"
        aria-hidden
      />

      <div className="relative mx-auto max-w-6xl px-6 pb-4 pt-10 lg:pt-14">
        <motion.div
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8 flex items-center gap-4"
        >
          <span className="font-arabic text-3xl font-bold text-kahf-tobago" lang="ar" dir="rtl">
            كهف
          </span>
          <span className="h-8 w-0.5 bg-kahf-rose" aria-hidden />
          <p className="font-sans text-[0.65rem] font-semibold uppercase tracking-[0.35em] text-kahf-tobago">
            Digital footprint discovery
          </p>
        </motion.div>

        <div className="relative grid gap-10 lg:grid-cols-[1.15fr_0.85fr] lg:items-end">
          <div className="relative z-10">
            <motion.p
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="font-arabic mb-2 text-lg text-kahf-rose lg:text-xl"
              lang="ar"
              dir="rtl"
            >
              قبل الحجاب
            </motion.p>
            <motion.h1
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.05 }}
              className="headline-display text-[clamp(2.8rem,10vw,6.5rem)] text-kahf-tobago"
            >
              PHOTOS WITHOUT
            </motion.h1>
            <motion.h1
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="headline-display -mt-1 text-[clamp(2.8rem,10vw,6.5rem)] text-kahf-tobago"
            >
              HIJAB STILL
            </motion.h1>
            <motion.h1
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.15 }}
              className="headline-display -mt-1 text-[clamp(2.8rem,10vw,6.5rem)] text-kahf-rose"
            >
              EXIST ONLINE
            </motion.h1>
            <div className="relative mt-4 flex flex-wrap items-baseline gap-x-4">
              <motion.span
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.22 }}
                className="headline-script text-[clamp(2.4rem,7vw,4.5rem)] text-kahf-tobago"
              >
                find them.
              </motion.span>
              <motion.p
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.3 }}
                className="max-w-md font-sans text-base leading-relaxed text-kahf-tobago/80"
              >
                Upload photos of you in hijab now. We search for older images of you
                without it — so you can reclaim your narrative, privately.
              </motion.p>
            </div>
          </div>

          <div className="relative hidden min-h-[300px] lg:block" aria-hidden>
            <div
              className="polaroid animate-drift absolute right-6 top-0 z-10 w-[145px] bg-kahf-fantasy"
              style={{ "--tilt": "-5deg" } as React.CSSProperties}
            >
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img src="/inspo/photo-booth.png" alt="" />
              <p className="mt-2 text-center font-sans text-[10px] font-bold uppercase tracking-widest text-kahf-tobago">
                you, elsewhere
              </p>
            </div>
            <div
              className="polaroid animate-drift absolute right-40 top-20 w-[115px] bg-kahf-vanilla"
              style={{ "--tilt": "4deg", animationDelay: "1s" } as React.CSSProperties}
            >
              <div className="flex aspect-square items-center justify-center bg-kahf-sand">
                <span className="font-arabic text-2xl text-kahf-tobago" lang="ar">
                  حجاب
                </span>
              </div>
            </div>
            <div
              className="absolute right-4 top-52 w-[90px] border-2 border-kahf-tobago bg-kahf-tobago p-3 text-kahf-fantasy"
              style={{ transform: "rotate(2deg)" }}
            >
              <p className="font-arabic text-center text-xl leading-tight" lang="ar" dir="rtl">
                خصوصية
              </p>
              <p className="mt-1 text-center font-sans text-[8px] uppercase tracking-widest">
                privacy
              </p>
            </div>
          </div>
        </div>

        <div className="mt-10 overflow-hidden border-y-2 border-kahf-tobago bg-kahf-vanilla py-3">
          <div className="marquee-track flex w-max gap-14 whitespace-nowrap">
            {[...FLOAT_LABELS, ...FLOAT_LABELS].map((label, i) => (
              <span
                key={`${label}-${i}`}
                className={`float-label font-semibold ${
                  /[\u0600-\u06FF]/.test(label) ? "font-arabic text-base" : "font-sans"
                }`}
                lang={/[\u0600-\u06FF]/.test(label) ? "ar" : undefined}
                dir={/[\u0600-\u06FF]/.test(label) ? "rtl" : undefined}
              >
                {label} ·
              </span>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
