"use client";

import { useTheme } from "next-themes";
import { ArrowLeft, FileJson, Image as ImageIcon, Loader2, Moon, Sparkles, Sun } from "lucide-react";
import Link from "next/link";
import { Button } from "@/components/ui/button";

interface Props {
  title: string;
  busy: string | null;
  onExportPng: () => void;
  onExportSvg: () => void;
  onExportJson: () => void;
}

export default function CustomToolbar({ title, busy, onExportPng, onExportSvg, onExportJson }: Props) {
  const { resolvedTheme, setTheme } = useTheme();

  const icon = (which: string, fallback: React.ReactNode) =>
    busy === which ? <Loader2 className="h-4 w-4 animate-spin" /> : fallback;

  return (
    <div className="flex flex-wrap items-center gap-2 border-b border-slate-200 bg-white/80 px-4 py-2.5 backdrop-blur dark:border-slate-800 dark:bg-slate-900/70">
      <Link href="/dashboard">
        <Button variant="ghost" size="sm">
          <ArrowLeft className="h-4 w-4" /> Dashboard
        </Button>
      </Link>
      <div className="flex items-center gap-1.5 text-brand-600">
        <Sparkles className="h-4 w-4" />
        <span className="max-w-[40vw] truncate text-sm font-semibold text-slate-800 dark:text-slate-100">
          {title}
        </span>
      </div>

      <div className="ml-auto flex items-center gap-2">
        <Button variant="outline" size="sm" onClick={onExportPng} disabled={busy !== null}>
          {icon("png", <ImageIcon className="h-4 w-4" />)} PNG
        </Button>
        <Button variant="outline" size="sm" onClick={onExportSvg} disabled={busy !== null}>
          {icon("svg", <ImageIcon className="h-4 w-4" />)} SVG
        </Button>
        <Button variant="outline" size="sm" onClick={onExportJson} disabled={busy !== null}>
          {icon("json", <FileJson className="h-4 w-4" />)} .excalidraw
        </Button>
        <Button
          variant="ghost"
          size="icon"
          aria-label="Toggle theme"
          onClick={() => setTheme(resolvedTheme === "dark" ? "light" : "dark")}
        >
          {resolvedTheme === "dark" ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
        </Button>
      </div>
    </div>
  );
}
