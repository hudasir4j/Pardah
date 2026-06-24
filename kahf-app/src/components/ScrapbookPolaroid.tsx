"use client";

import { motion } from "framer-motion";
import { useEffect, useState } from "react";

export interface ScrapbookPose {
  x: number;
  y: number;
  rotate: number;
  scale: number;
}

interface ScrapbookPolaroidProps {
  src: string;
  poses: ScrapbookPose[];
  holdMs?: number;
  startDelayMs?: number;
  className?: string;
  style: React.CSSProperties;
}

export function ScrapbookPolaroid({
  src,
  poses,
  holdMs = 1100,
  startDelayMs = 0,
  className = "",
  style,
}: ScrapbookPolaroidProps) {
  const [index, setIndex] = useState(0);
  const [active, setActive] = useState(startDelayMs === 0);

  useEffect(() => {
    if (startDelayMs <= 0) return;
    const timer = setTimeout(() => setActive(true), startDelayMs);
    return () => clearTimeout(timer);
  }, [startDelayMs]);

  useEffect(() => {
    if (!active || poses.length < 2) return;
    const prefersReduced =
      typeof window !== "undefined" &&
      window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (prefersReduced) return;

    const interval = setInterval(() => {
      setIndex((i) => (i + 1) % poses.length);
    }, holdMs);
    return () => clearInterval(interval);
  }, [active, holdMs, poses.length]);

  const pose = poses[index] ?? poses[0];

  return (
    <motion.div
      className={`hero-polaroid-wrap absolute ${className}`.trim()}
      style={{ ...style, transformOrigin: "48% 88%" }}
      initial={false}
      animate={{
        x: pose.x,
        y: pose.y,
        rotate: pose.rotate,
        scale: pose.scale,
      }}
      transition={{
        duration: 0,
        type: "tween",
        ease: "linear",
      }}
    >
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img src={src} alt="" className="hero-polaroid-img" />
    </motion.div>
  );
}
