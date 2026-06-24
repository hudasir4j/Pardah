"use client";

import { useCallback, useEffect, useRef, useState } from "react";

const SLOTS = 5;
const MIN_PHOTOS = 3;
const MAX_PHOTOS = 5;

interface PhotoBoothStripProps {
  files: File[];
  onFilesChange: (files: File[]) => void;
  onSearch: () => void;
  canSearch: boolean;
  searching?: boolean;
  error?: string | null;
  disabled?: boolean;
}

export function PhotoBoothStrip({
  files,
  onFilesChange,
  onSearch,
  canSearch,
  searching,
  error,
  disabled,
}: PhotoBoothStripProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [previews, setPreviews] = useState<string[]>([]);
  const [dragOver, setDragOver] = useState(false);
  const [replaceIndex, setReplaceIndex] = useState<number | null>(null);

  useEffect(() => {
    const urls = files.map((f) => URL.createObjectURL(f));
    setPreviews(urls);
    return () => urls.forEach((u) => URL.revokeObjectURL(u));
  }, [files]);

  const addFiles = useCallback(
    (incoming: FileList | File[], atIndex?: number) => {
      const list = Array.from(incoming).filter((f) => f.type.startsWith("image/"));
      if (!list.length) return;

      if (atIndex !== undefined && atIndex < files.length) {
        const next = [...files];
        next[atIndex] = list[0];
        onFilesChange(next.slice(0, MAX_PHOTOS));
        return;
      }

      onFilesChange([...files, ...list].slice(0, MAX_PHOTOS));
    },
    [files, onFilesChange]
  );

  const removeAt = (index: number) => {
    onFilesChange(files.filter((_, i) => i !== index));
  };

  const openPicker = (index?: number) => {
    if (disabled || searching) return;
    setReplaceIndex(index ?? null);
    inputRef.current?.click();
  };

  const remaining = Math.max(0, MIN_PHOTOS - files.length);

  return (
    <div
      className={`tape-poster mx-auto max-w-3xl transition-colors ${
        dragOver ? "ring-4 ring-kahf-rose" : ""
      }`}
      onDragOver={(e) => {
        e.preventDefault();
        if (!disabled && !searching) setDragOver(true);
      }}
      onDragLeave={() => setDragOver(false)}
      onDrop={(e) => {
        e.preventDefault();
        setDragOver(false);
        if (!disabled && !searching) addFiles(e.dataTransfer.files);
      }}
    >
      <div className="bg-kahf-sand px-4 py-3">
        <p className="font-sans text-[10px] font-bold uppercase tracking-[0.25em] text-kahf-tobago">
          Step 1 — add your photos
        </p>
        <p className="mt-0.5 font-sans text-xs text-kahf-tobago/70">
          With hijab today, so we can find you from before
        </p>
      </div>

      <div className="booth-strip">
        {Array.from({ length: SLOTS }).map((_, i) => {
          const src = previews[i];
          const isRequired = i < MIN_PHOTOS;
          return (
            <div key={i} className="group relative min-w-0 flex-1">
              <button
                type="button"
                disabled={disabled || searching || (i >= files.length && files.length >= MAX_PHOTOS)}
                onClick={() => openPicker(i < files.length ? i : undefined)}
                className={`booth-frame w-full transition-transform hover:scale-[1.02] ${
                  !src ? "booth-frame--empty" : ""
                } ${dragOver && !src ? "booth-frame--drag" : ""}`}
                aria-label={
                  src ? `Change photo ${i + 1}` : `Add photo ${i + 1}${isRequired ? " (required)" : ""}`
                }
              >
                {src ? (
                  // eslint-disable-next-line @next/next/no-img-element
                  <img src={src} alt={`Reference ${i + 1}`} />
                ) : (
                  <>
                    <span className="font-sans text-[10px] font-bold uppercase tracking-[0.2em] text-kahf-sand">
                      {isRequired ? "add" : "opt"}
                    </span>
                    {i === 0 && files.length === 0 && (
                      <span className="mt-1 font-sans text-[9px] text-kahf-tobago/50">
                        tap or drop
                      </span>
                    )}
                  </>
                )}
              </button>
              {src && !disabled && !searching && (
                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation();
                    removeAt(i);
                  }}
                  className="absolute -right-1 -top-1 z-10 flex h-5 w-5 items-center justify-center bg-kahf-tobago font-sans text-xs text-kahf-fantasy opacity-0 transition-opacity group-hover:opacity-100"
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
        multiple={replaceIndex === null}
        className="hidden"
        disabled={disabled || searching}
        onChange={(e) => {
          if (!e.target.files) return;
          if (replaceIndex !== null) {
            addFiles(e.target.files, replaceIndex);
          } else {
            addFiles(e.target.files);
          }
          setReplaceIndex(null);
          e.target.value = "";
        }}
      />

      {/* CTA attached directly to upload — clear next step */}
      <div className="border-t-2 border-kahf-tobago bg-kahf-vanilla px-4 py-5">
        <p className="text-center font-sans text-xs text-kahf-tobago/70">
          {files.length}/{MAX_PHOTOS} photos
          {remaining > 0 ? ` · ${remaining} more to search` : " · ready to search"}
        </p>

        {error && (
          <p className="mt-2 text-center font-sans text-sm text-kahf-rose" role="alert">
            {error}
          </p>
        )}

        <button
          type="button"
          onClick={onSearch}
          disabled={!canSearch || searching}
          className="headline-sans mt-4 w-full bg-kahf-tobago py-4 text-lg uppercase tracking-wide text-kahf-fantasy transition-colors hover:bg-kahf-rose hover:text-kahf-tobago disabled:cursor-not-allowed disabled:bg-kahf-sand disabled:text-kahf-tobago/40"
        >
          {searching ? "Searching…" : "Search for my photos"}
        </button>
        <p className="mt-2 text-center font-sans text-[10px] uppercase tracking-widest text-kahf-tobago/45">
          memory only · wiped when done
        </p>
      </div>
    </div>
  );
}
