"use client";

import { useCallback, useEffect, useRef, useState } from "react";

const SLOTS = 5;
const MIN_PHOTOS = 3;
const MAX_PHOTOS = 5;

interface PhotoBoothStripProps {
  files: File[];
  onFilesChange: (files: File[]) => void;
  disabled?: boolean;
}

export function PhotoBoothStrip({ files, onFilesChange, disabled }: PhotoBoothStripProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [previews, setPreviews] = useState<string[]>([]);
  const [dragOver, setDragOver] = useState(false);

  useEffect(() => {
    const urls = files.map((f) => URL.createObjectURL(f));
    setPreviews(urls);
    return () => urls.forEach((u) => URL.revokeObjectURL(u));
  }, [files]);

  const addFiles = useCallback(
    (incoming: FileList | File[]) => {
      const list = Array.from(incoming).filter((f) => f.type.startsWith("image/"));
      onFilesChange([...files, ...list].slice(0, MAX_PHOTOS));
    },
    [files, onFilesChange]
  );

  const removeAt = (index: number) => {
    onFilesChange(files.filter((_, i) => i !== index));
  };

  return (
    <div
      className={`tape-poster w-full rotate-[0.5deg] transition-colors ${
        dragOver ? "ring-2 ring-kahf-mountain/50" : ""
      }`}
      onDragOver={(e) => {
        e.preventDefault();
        if (!disabled) setDragOver(true);
      }}
      onDragLeave={() => setDragOver(false)}
      onDrop={(e) => {
        e.preventDefault();
        setDragOver(false);
        if (!disabled) addFiles(e.dataTransfer.files);
      }}
    >
      <div className="booth-strip rounded-sm">
        {Array.from({ length: SLOTS }).map((_, i) => {
          const src = previews[i];
          const filled = Boolean(src);
          return (
            <div key={i} className="relative min-w-0">
              <button
                type="button"
                disabled={disabled || (!filled && files.length >= MAX_PHOTOS)}
                onClick={() => {
                  if (filled) return;
                  inputRef.current?.click();
                }}
                className={`booth-frame w-full rounded-sm ${
                  filled ? "" : "booth-frame--empty"
                }`}
                aria-label={
                  filled ? `Reference photo ${i + 1}` : `Add reference photo ${i + 1}`
                }
              >
                {src ? (
                  // eslint-disable-next-line @next/next/no-img-element
                  <img src={src} alt={`Reference ${i + 1}`} />
                ) : (
                  <>
                    <span className="headline-display text-2xl leading-none text-kahf-coffee/35">
                      +
                    </span>
                    <span className="body-sans text-[10px] font-medium uppercase tracking-[0.2em] text-kahf-coffee/40">
                      {i < MIN_PHOTOS ? "add" : "opt"}
                    </span>
                    {i === 0 && files.length === 0 && (
                      <span className="body-sans px-2 text-center text-[9px] leading-tight text-kahf-coffee/35">
                        tap or drop
                      </span>
                    )}
                  </>
                )}
              </button>
              {filled && !disabled && (
                <button
                  type="button"
                  onClick={() => removeAt(i)}
                  className="body-sans absolute -right-1 -top-1 z-10 flex h-5 w-5 items-center justify-center rounded-full bg-kahf-coffee text-[10px] text-kahf-almond hover:bg-kahf-berkeley"
                  aria-label={`Remove photo ${i + 1}`}
                >
                  ×
                </button>
              )}
            </div>
          );
        })}
      </div>

      <input
        ref={inputRef}
        type="file"
        accept="image/*"
        multiple
        className="hidden"
        disabled={disabled}
        onChange={(e) => {
          if (e.target.files) addFiles(e.target.files);
          e.target.value = "";
        }}
      />
    </div>
  );
}
