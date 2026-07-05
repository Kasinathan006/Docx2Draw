"use client";

import { useCallback, useState } from "react";

/** Loosely-typed imperative Excalidraw API surface we rely on. */
export type ExcalidrawAPI = {
  getSceneElements: () => readonly unknown[];
  getAppState: () => Record<string, unknown>;
  getFiles: () => Record<string, unknown>;
};

function triggerDownload(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}

/** Canvas state + export handlers (guide §6.1 hooks/useExcalidraw). */
export function useExcalidraw(baseName: string) {
  const [api, setApi] = useState<ExcalidrawAPI | null>(null);
  const [busy, setBusy] = useState<string | null>(null);

  const safeName = (baseName || "doc2draw").replace(/[^\w.-]+/g, "_");

  const exportPng = useCallback(async () => {
    if (!api) return;
    setBusy("png");
    try {
      const { exportToBlob } = await import("@excalidraw/excalidraw");
      const blob = await exportToBlob({
        elements: api.getSceneElements() as never,
        appState: { ...api.getAppState(), exportBackground: true, exportWithDarkMode: false } as never,
        files: api.getFiles() as never,
        mimeType: "image/png",
        quality: 1,
        getDimensions: (w: number, h: number) => ({ width: w * 2, height: h * 2, scale: 2 }),
      });
      triggerDownload(blob, `${safeName}.png`);
    } finally {
      setBusy(null);
    }
  }, [api, safeName]);

  const exportSvg = useCallback(async () => {
    if (!api) return;
    setBusy("svg");
    try {
      const { exportToSvg } = await import("@excalidraw/excalidraw");
      const svg = await exportToSvg({
        elements: api.getSceneElements() as never,
        appState: { ...api.getAppState(), exportBackground: true } as never,
        files: api.getFiles() as never,
      });
      const svgString = new XMLSerializer().serializeToString(svg);
      triggerDownload(new Blob([svgString], { type: "image/svg+xml" }), `${safeName}.svg`);
    } finally {
      setBusy(null);
    }
  }, [api, safeName]);

  const exportJson = useCallback(async () => {
    if (!api) return;
    setBusy("json");
    try {
      const { serializeAsJSON } = await import("@excalidraw/excalidraw");
      const json = serializeAsJSON(
        api.getSceneElements() as never,
        api.getAppState() as never,
        api.getFiles() as never,
        "local",
      );
      triggerDownload(new Blob([json], { type: "application/json" }), `${safeName}.excalidraw`);
    } finally {
      setBusy(null);
    }
  }, [api, safeName]);

  return { api, setApi, busy, exportPng, exportSvg, exportJson };
}
