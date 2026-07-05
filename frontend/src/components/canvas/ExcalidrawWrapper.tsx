"use client";

import React, { useEffect, useState } from "react";
import dynamic from "next/dynamic";
import { useTheme } from "next-themes";
import { Loader2 } from "lucide-react";
import type { ExcalidrawAPI } from "@/hooks/useExcalidraw";

// @excalidraw/excalidraw relies on browser DOM APIs; import it without SSR.
// (v0.17.x injects its own CSS at runtime, so there is no stylesheet to import.)
const Excalidraw = dynamic(
  async () => (await import("@excalidraw/excalidraw")).Excalidraw,
  {
    ssr: false,
    loading: () => (
      <div className="flex h-full w-full items-center justify-center text-slate-400">
        <Loader2 className="mr-2 h-5 w-5 animate-spin" /> Loading canvas…
      </div>
    ),
  },
);

interface ExcalidrawWrapperProps {
  initialData: Record<string, unknown>;
  onAPI?: (api: ExcalidrawAPI) => void;
}

export default function ExcalidrawWrapper({ initialData, onAPI }: ExcalidrawWrapperProps) {
  const { resolvedTheme } = useTheme();
  const [excalidrawAPI, setExcalidrawAPI] = useState<ExcalidrawAPI | null>(null);

  useEffect(() => {
    if (!excalidrawAPI) return;
    const api = excalidrawAPI as unknown as {
      updateScene: (s: unknown) => void;
    };
    api.updateScene({
      elements: (initialData.elements as unknown[]) || [],
      appState: {
        ...(initialData.appState as Record<string, unknown>),
        theme: resolvedTheme === "dark" ? "dark" : "light",
      },
      files: (initialData.files as Record<string, unknown>) || {},
    });
  }, [excalidrawAPI, initialData, resolvedTheme]);

  return (
    <div className="excalidraw-wrapper h-full w-full">
      <Excalidraw
        excalidrawAPI={(api: unknown) => {
          const typed = api as ExcalidrawAPI;
          setExcalidrawAPI(typed);
          onAPI?.(typed);
        }}
        initialData={initialData as never}
      />
    </div>
  );
}
