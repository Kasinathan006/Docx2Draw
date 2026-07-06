"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { Sparkles, Key, ChevronDown } from "lucide-react";
import FileDropzone from "@/components/upload/FileDropzone";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { generateDiagram, uploadFile, verifyApiKey } from "@/lib/api";
import { useProjectStatus } from "@/hooks/useProjectStatus";
import { saveProject } from "@/lib/projects";

type Phase = "idle" | "working" | "error";

const VIDEO_RE = /\.(mp4|mov|avi|mkv|webm)$/i;

const STAGE_LABEL: Record<string, string> = {
  queued: "Queued",
  parsing: "Parsing document",
  extracting_media: "Extracting media",
  ai_structuring: "Structuring with AI",
  compiling: "Compiling Excalidraw",
  done: "Done",
  error: "Error",
};

type Provider = "openai" | "gemini" | "anthropic" | "groq";

const PROVIDERS: {
  value: Provider;
  label: string;
  logo: string;
  placeholder: string;
  hint: string;
  color: string;
}[] = [
  {
    value: "openai",
    label: "OpenAI",
    logo: "🟢",
    placeholder: "sk-...",
    hint: "Get from platform.openai.com/api-keys",
    color: "text-emerald-600",
  },
  {
    value: "gemini",
    label: "Google Gemini",
    logo: "🔵",
    placeholder: "AIza...",
    hint: "Get from aistudio.google.com/app/apikey",
    color: "text-blue-600",
  },
  {
    value: "anthropic",
    label: "Anthropic (Claude)",
    logo: "🟠",
    placeholder: "sk-ant-...",
    hint: "Get from console.anthropic.com/settings/keys",
    color: "text-orange-600",
  },
  {
    value: "groq",
    label: "Groq",
    logo: "🟣",
    placeholder: "gsk_...",
    hint: "Get from console.groq.com/keys",
    color: "text-purple-600",
  },
];

export default function NewProjectPage() {
  const router = useRouter();
  const [file, setFile] = useState<File | null>(null);
  const [title, setTitle] = useState("");
  const [columns, setColumns] = useState(3);
  const [extractScreenshots, setExtractScreenshots] = useState(true);
  const [phase, setPhase] = useState<Phase>("idle");
  const [jobId, setJobId] = useState<string | null>(null);
  const [projectId, setProjectId] = useState<string | null>(null);
  const [error, setError] = useState("");
  const [provider, setProvider] = useState<Provider>("openai");
  const [apiKey, setApiKey] = useState("");
  const [keyStatus, setKeyStatus] = useState<"idle" | "checking" | "valid" | "invalid">("idle");
  const [keyError, setKeyError] = useState("");
  const [showProviderDropdown, setShowProviderDropdown] = useState(false);

  const { stage, progress, message, isDone, isError, errorMessage, chapters } =
    useProjectStatus(jobId);

  const currentProvider = PROVIDERS.find((p) => p.value === provider)!;

  useEffect(() => {
    if (isDone && projectId) {
      saveProject({
        projectId,
        title: title || "Visual Map",
        createdAt: Date.now(),
        status: "done",
        chapters,
      });
      router.push(`/editor/${projectId}`);
    }
  }, [isDone, projectId, title, chapters, router]);

  useEffect(() => {
    if (isError) {
      setError(errorMessage || "Generation failed");
      setPhase("error");
    }
  }, [isError, errorMessage]);

  const pickFile = (f: File) => {
    setFile(f);
    if (!title) {
      const base = f.name.replace(/\.[^.]+$/, "").replace(/[_-]+/g, " ");
      setTitle(base.replace(/\b\w/g, (c) => c.toUpperCase()));
    }
  };

  const handleProviderChange = (p: Provider) => {
    setProvider(p);
    setApiKey("");
    setKeyStatus("idle");
    setKeyError("");
    setShowProviderDropdown(false);
  };

  const handleVerifyKey = async () => {
    if (!apiKey.trim()) return;
    setKeyStatus("checking");
    setKeyError("");
    try {
      const res = await verifyApiKey(apiKey.trim(), provider);
      setKeyStatus(res.valid ? "valid" : "invalid");
      if (!res.valid) setKeyError(res.error || "Invalid key");
    } catch (e) {
      setKeyStatus("invalid");
      setKeyError(e instanceof Error ? e.message : String(e));
    }
  };

  const start = async () => {
    if (!file) return;
    setPhase("working");
    setError("");
    try {
      const uploaded = await uploadFile(file);
      setProjectId(uploaded.project_id);
      const job = await generateDiagram(uploaded.project_id, {
        title: title || "Visual Map",
        columns,
        extract_screenshots: extractScreenshots,
        api_key: keyStatus === "valid" ? apiKey.trim() : undefined,
        ai_provider: keyStatus === "valid" ? provider : undefined,
      });
      setJobId(job.job_id);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
      setPhase("error");
    }
  };

  const isVideo = file ? VIDEO_RE.test(file.name) : false;

  return (
    <div className="mx-auto max-w-2xl">
      <h1 className="mb-1 text-2xl font-bold text-slate-800 dark:text-slate-100">New visual map</h1>
      <p className="mb-6 text-sm text-slate-500 dark:text-slate-400">
        Upload a document or video and Doc2Draw will generate an interactive Excalidraw map.
      </p>

      {phase !== "working" && (
        <Card>
          <CardContent className="space-y-5 pt-6">
            <FileDropzone file={file} onFileSelected={pickFile} />

            <div>
              <label className="mb-1 block text-sm font-medium text-slate-600 dark:text-slate-300">
                Diagram title
              </label>
              <input
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="e.g. Make.com Masterclass"
                className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm outline-none focus:border-brand-500 focus:ring-2 focus:ring-brand-200 dark:border-slate-700 dark:bg-slate-900"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="mb-1 block text-sm font-medium text-slate-600 dark:text-slate-300">
                  Columns (1–6)
                </label>
                <select
                  value={columns}
                  onChange={(e) => setColumns(Number(e.target.value))}
                  className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm outline-none focus:border-brand-500 dark:border-slate-700 dark:bg-slate-900"
                >
                  {[1, 2, 3, 4, 5, 6].map((n) => (
                    <option key={n} value={n}>
                      {n} column{n > 1 ? "s" : ""}{n === 3 ? " (default)" : n === 6 ? " (compact)" : ""}
                    </option>
                  ))}
                </select>
                <p className="mt-1 text-xs text-slate-400">
                  More columns = smaller cards, wider canvas
                </p>
              </div>

              <div>
                <label className="mb-1 block text-sm font-medium text-slate-600 dark:text-slate-300">
                  Screenshots
                </label>
                <label className="flex items-center gap-2 rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm cursor-pointer dark:border-slate-700 dark:bg-slate-900">
                  <input
                    type="checkbox"
                    checked={extractScreenshots}
                    onChange={(e) => setExtractScreenshots(e.target.checked)}
                    className="h-4 w-4 rounded border-slate-300 text-brand-600"
                  />
                  <span className="text-slate-700 dark:text-slate-300">
                    {isVideo ? "Extract video frames" : "Embed images"}
                  </span>
                </label>
                <p className="mt-1 text-xs text-slate-400">
                  {isVideo
                    ? "Key frames embedded into cards"
                    : "Images from the document embedded"}
                </p>
              </div>
            </div>

            {/* ─── AI Provider + API Key Section ─────────────────────────── */}
            <div className="rounded-xl border border-slate-200 bg-slate-50 p-4 space-y-3 dark:border-slate-700 dark:bg-slate-800/50">
              <div className="flex items-center gap-2 mb-1">
                <Key className="h-4 w-4 text-slate-500" />
                <span className="text-sm font-medium text-slate-700 dark:text-slate-300">
                  AI Provider &amp; API Key
                </span>
                <span className="text-xs text-slate-400 font-normal">(optional — enables smarter diagrams)</span>
              </div>

              {/* Provider Selector */}
              <div className="relative">
                <button
                  type="button"
                  onClick={() => setShowProviderDropdown((v) => !v)}
                  className="w-full flex items-center justify-between rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-900 hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors"
                >
                  <span className="flex items-center gap-2">
                    <span>{currentProvider.logo}</span>
                    <span className="font-medium text-slate-700 dark:text-slate-200">{currentProvider.label}</span>
                  </span>
                  <ChevronDown className={`h-4 w-4 text-slate-400 transition-transform ${showProviderDropdown ? "rotate-180" : ""}`} />
                </button>

                {showProviderDropdown && (
                  <div className="absolute z-20 mt-1 w-full rounded-lg border border-slate-200 bg-white shadow-lg dark:border-slate-700 dark:bg-slate-900 overflow-hidden">
                    {PROVIDERS.map((p) => (
                      <button
                        key={p.value}
                        type="button"
                        onClick={() => handleProviderChange(p.value)}
                        className={`w-full flex items-center gap-3 px-3 py-2.5 text-sm text-left hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors ${
                          provider === p.value ? "bg-slate-100 dark:bg-slate-800" : ""
                        }`}
                      >
                        <span className="text-base">{p.logo}</span>
                        <div>
                          <div className="font-medium text-slate-800 dark:text-slate-100">{p.label}</div>
                          <div className="text-xs text-slate-400">{p.hint}</div>
                        </div>
                        {provider === p.value && (
                          <span className="ml-auto text-xs text-brand-600 font-medium">✓</span>
                        )}
                      </button>
                    ))}
                  </div>
                )}
              </div>

              {/* Key Input + Verify */}
              <div className="flex gap-2">
                <input
                  type="password"
                  value={apiKey}
                  onChange={(e) => {
                    setApiKey(e.target.value);
                    setKeyStatus("idle");
                    setKeyError("");
                  }}
                  placeholder={currentProvider.placeholder}
                  className="flex-1 rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm font-mono outline-none focus:border-brand-500 focus:ring-2 focus:ring-brand-200 dark:border-slate-700 dark:bg-slate-900"
                />
                <button
                  type="button"
                  onClick={handleVerifyKey}
                  disabled={!apiKey.trim() || keyStatus === "checking"}
                  className="shrink-0 rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50 disabled:opacity-50 dark:border-slate-600 dark:bg-slate-800 dark:text-slate-200 transition-colors"
                >
                  {keyStatus === "checking" ? "Checking…" : "Verify"}
                </button>
              </div>

              {/* Status feedback */}
              {keyStatus === "valid" && (
                <p className="text-xs font-medium text-emerald-600">
                  ✓ {currentProvider.label} key verified — AI extraction enabled
                </p>
              )}
              {keyStatus === "invalid" && (
                <p className="text-xs text-red-500">✗ {keyError || "Invalid key — check and try again"}</p>
              )}
              {keyStatus === "idle" && !apiKey && (
                <p className="text-xs text-slate-400">
                  Leave blank to use fast rule-based extraction (no API key needed)
                </p>
              )}
              {keyStatus === "idle" && apiKey && (
                <p className="text-xs text-amber-500">Click Verify to validate your key before generating</p>
              )}
            </div>
            {/* ─────────────────────────────────────────────────────────────── */}

            {phase === "error" && (
              <div className="rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-600">
                <strong>Error:</strong> {error}
                <div className="mt-2 text-xs text-red-400 space-y-1">
                  <p>The API request failed. Possible causes:</p>
                  <ul className="list-disc ml-4 space-y-0.5">
                    <li>Backend (Render) may be sleeping — wait 30 s and retry</li>
                    <li>
                      Set <code className="font-mono">NEXT_PUBLIC_API_URL</code> in
                      Vercel → Settings → Environment Variables → your Render URL
                    </li>
                  </ul>
                </div>
              </div>
            )}

            <Button className="w-full" disabled={!file} onClick={start}>
              Generate Visual Map <Sparkles className="h-4 w-4" />
            </Button>
          </CardContent>
        </Card>
      )}

      {phase === "working" && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
          <Card>
            <CardHeader>
              <CardTitle>{STAGE_LABEL[stage ?? "queued"] ?? "Working…"}</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <p className="text-sm text-slate-500 dark:text-slate-400">{message || "Starting…"}</p>
              <Progress value={progress} />
              <p className="text-center text-xs text-slate-400">{progress}% complete</p>
            </CardContent>
          </Card>
        </motion.div>
      )}
    </div>
  );
}
