"use client";

import { useEffect, useMemo, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { Loader2 } from "lucide-react";
import CustomToolbar from "@/components/canvas/CustomToolbar";
import ExcalidrawWrapper from "@/components/canvas/ExcalidrawWrapper";
import { Button } from "@/components/ui/button";
import { getExcalidraw } from "@/lib/api";
import { useExcalidraw } from "@/hooks/useExcalidraw";
import { getProjects } from "@/lib/projects";

export default function EditorPage() {
  const params = useParams<{ projectId: string }>();
  const projectId = params.projectId;

  const [scene, setScene] = useState<Record<string, unknown> | null>(null);
  const [error, setError] = useState<string>("");
  const [loading, setLoading] = useState(true);

  const title = useMemo(() => {
    const rec = getProjects().find((p) => p.projectId === projectId);
    return rec?.title || "Visual Map";
  }, [projectId]);

  const { setApi, busy, exportPng, exportSvg, exportJson } = useExcalidraw(title);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const data = await getExcalidraw(projectId);
        if (!cancelled) setScene(data);
      } catch (e) {
        if (!cancelled) setError(e instanceof Error ? e.message : String(e));
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [projectId]);

  const initialData = useMemo(() => {
    if (!scene) return null;
    return {
      elements: (scene.elements as unknown[]) ?? [],
      appState: (scene.appState as Record<string, unknown>) ?? {},
      files: (scene.files as Record<string, unknown>) ?? {},
      scrollToContent: true,
    } as Record<string, unknown>;
  }, [scene]);

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center text-slate-400">
        <Loader2 className="mr-2 h-5 w-5 animate-spin" /> Loading visual map…
      </div>
    );
  }

  if (error || !initialData) {
    return (
      <div className="flex h-screen flex-col items-center justify-center gap-4 text-center">
        <p className="font-semibold text-red-600">Could not load this map</p>
        <p className="max-w-md text-sm text-slate-500">{error || "No diagram data found."}</p>
        <Link href="/dashboard/new">
          <Button>Create a new map</Button>
        </Link>
      </div>
    );
  }

  return (
    <div className="flex h-screen flex-col">
      <CustomToolbar
        title={title}
        busy={busy}
        onExportPng={exportPng}
        onExportSvg={exportSvg}
        onExportJson={exportJson}
      />
      <div className="min-h-0 flex-1">
        <ExcalidrawWrapper initialData={initialData} onAPI={setApi} />
      </div>
    </div>
  );
}
