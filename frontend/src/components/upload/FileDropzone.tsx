"use client";

import { useCallback, useRef, useState } from "react";
import { FileText, Film, UploadCloud } from "lucide-react";
import { cn, formatBytes } from "@/lib/utils";

const ACCEPT = ".docx,.pdf,.txt,.md,.mp4,.mov,.avi,.mkv,.webm,.png,.jpg,.jpeg";
const VIDEO_RE = /\.(mp4|mov|avi|mkv|webm)$/i;

interface Props {
  file: File | null;
  onFileSelected: (file: File) => void;
  disabled?: boolean;
}

export default function FileDropzone({ file, onFileSelected, disabled }: Props) {
  const [dragOver, setDragOver] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setDragOver(false);
      const f = e.dataTransfer.files?.[0];
      if (f) onFileSelected(f);
    },
    [onFileSelected],
  );

  const isVideo = file ? VIDEO_RE.test(file.name) : false;

  return (
    <div
      onDragOver={(e) => {
        e.preventDefault();
        setDragOver(true);
      }}
      onDragLeave={() => setDragOver(false)}
      onDrop={handleDrop}
      onClick={() => !disabled && inputRef.current?.click()}
      role="button"
      tabIndex={0}
      className={cn(
        "flex cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed px-6 py-10 text-center transition",
        dragOver
          ? "border-brand-500 bg-brand-50 dark:bg-brand-900/20"
          : "border-slate-300 hover:border-brand-400 hover:bg-brand-50/50 dark:border-slate-700",
        disabled && "pointer-events-none opacity-60",
      )}
    >
      <input
        ref={inputRef}
        type="file"
        accept={ACCEPT}
        className="hidden"
        onChange={(e) => {
          const f = e.target.files?.[0];
          if (f) onFileSelected(f);
        }}
      />
      {file ? (
        <div className="flex items-center gap-2 text-slate-700 dark:text-slate-200">
          {isVideo ? <Film className="h-6 w-6 text-brand-600" /> : <FileText className="h-6 w-6 text-brand-600" />}
          <span className="font-medium">{file.name}</span>
          <span className="text-xs text-slate-400">({formatBytes(file.size)})</span>
        </div>
      ) : (
        <>
          <UploadCloud className="mb-3 h-10 w-10 text-brand-500" />
          <p className="font-semibold text-slate-700 dark:text-slate-200">Drop a document or video here</p>
          <p className="mt-1 text-sm text-slate-400">.docx · .pdf · .txt · .md · .mp4 · images</p>
        </>
      )}
    </div>
  );
}
