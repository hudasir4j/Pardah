"use client";

import { useCallback, useRef, useState } from "react";

const MIN_PHOTOS = 3;
const MAX_PHOTOS = 5;

interface UploadZoneProps {
  files: File[];
  onFilesChange: (files: File[]) => void;
  disabled?: boolean;
}

export function UploadZone({ files, onFilesChange, disabled }: UploadZoneProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [dragOver, setDragOver] = useState(false);

  const addFiles = useCallback(
    (incoming: FileList | File[]) => {
      const list = Array.from(incoming).filter((f) => f.type.startsWith("image/"));
      const merged = [...files, ...list].slice(0, MAX_PHOTOS);
      onFilesChange(merged);
    },
    [files, onFilesChange]
  );

  return (
    <section className="paper-grid tape-poster rounded-sm border border-kahf-charcoal/8 bg-kahf-paper/90 p-6 sm:p-8">
      <div
        role="button"
        tabIndex={0}
        onKeyDown={(e) => e.key === "Enter" && inputRef.current?.click()}
        onDragOver={(e) => {
          e.preventDefault();
          setDragOver(true);
        }}
        onDragLeave={() => setDragOver(false)}
        onDrop={(e) => {
          e.preventDefault();
          setDragOver(false);
          if (!disabled) addFiles(e.dataTransfer.files);
        }}
        onClick={() => !disabled && inputRef.current?.click()}
        className={`group cursor-pointer rounded-sm border border-dashed px-6 py-10 transition-all ${
          dragOver
            ? "border-kahf-wine bg-kahf-blush/30"
            : "border-kahf-charcoal/20 bg-white/40 hover:border-kahf-terracotta/50 hover:bg-kahf-yellow/15"
        } ${disabled ? "pointer-events-none opacity-60" : ""}`}
      >
        <div className="flex flex-col items-center gap-5 text-center">
          {/* Mouth-grid inspired icon row */}
          <div className="flex gap-2 opacity-60 grayscale" aria-hidden>
            {["◡", "○", "∀"].map((glyph, i) => (
              <span
                key={i}
                className="flex h-10 w-10 items-center justify-center border border-kahf-charcoal/15 bg-kahf-cream font-serif text-lg"
              >
                {glyph}
              </span>
            ))}
          </div>

          <div>
            <p className="headline-sans text-xl text-kahf-ink sm:text-2xl">
              drop {MIN_PHOTOS}–{MAX_PHOTOS} reference photos
            </p>
            <p className="mt-3 max-w-md font-sans text-sm leading-relaxed text-kahf-charcoal/65">
              Different angles, different eras — we build a gentle biometric profile
              in memory only. Nothing saved. Nothing kept.
            </p>
          </div>

          <span className="rounded-full border-2 border-kahf-terracotta bg-kahf-terracotta px-6 py-2.5 font-sans text-sm font-semibold text-white transition-transform group-hover:scale-[1.03]">
            Choose photos
          </span>
        </div>

        <input
          ref={inputRef}
          type="file"
          accept="image/*"
          multiple
          className="hidden"
          disabled={disabled}
          onChange={(e) => e.target.files && addFiles(e.target.files)}
        />
      </div>

      {files.length > 0 && (
        <ul className="mt-5 flex flex-wrap justify-center gap-2">
          {files.map((file, i) => (
            <li
              key={`${file.name}-${i}`}
              className="flex items-center gap-2 rounded-full border border-kahf-sage/40 bg-kahf-sage/15 px-3 py-1.5"
            >
              <span className="max-w-[120px] truncate font-sans text-xs text-kahf-charcoal">
                {file.name}
              </span>
              {!disabled && (
                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation();
                    onFilesChange(files.filter((_, idx) => idx !== i));
                  }}
                  className="text-xs text-kahf-charcoal/45 hover:text-kahf-wine"
                  aria-label={`Remove ${file.name}`}
                >
                  ×
                </button>
              )}
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
