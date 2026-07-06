import axios from "axios";

/**
 * API_BASE strategy:
 * - In browser (client-side): use "" (empty = relative URLs like /api/v1/...)
 *   These go through Next.js rewrites → backend. No CORS ever.
 * - In server-side rendering (SSR): use the full backend URL so Next.js
 *   can proxy the request during rewrite resolution.
 *
 * Set NEXT_PUBLIC_API_URL in Vercel → Project Settings → Environment Variables
 * to your Render backend URL: https://your-service.onrender.com
 */
const isServer = typeof window === "undefined";

export const API_BASE = isServer
  ? (
      process.env.NEXT_PUBLIC_API_URL ||
      process.env.BACKEND_URL ||
      "http://localhost:8000"
    ).replace(/\/$/, "")
  : ""; // Client-side: always relative (proxied by Next.js rewrites)

export const apiClient = axios.create({ baseURL: API_BASE });

/** Attach (or clear) a Supabase JWT for authenticated requests. */
export function setAuthToken(token: string | null): void {
  if (token) {
    apiClient.defaults.headers.common["Authorization"] = `Bearer ${token}`;
  } else {
    delete apiClient.defaults.headers.common["Authorization"];
  }
}

// ---- Types ----------------------------------------------------------------
export type JobStatus =
  | "queued"
  | "processing"
  | "done"
  | "error";

export interface UploadResponse {
  project_id: string;
  filename: string;
  file_type: string;
  file_size_bytes: number;
}

export interface GenerateResponse {
  job_id: string;
  project_id: string;
  status: JobStatus;
  estimated_time_sec: number;
}

export interface JobStatusResponse {
  job_id: string;
  project_id: string;
  status: JobStatus;
  stage: string;
  progress: number;
  message: string;
  result_available: boolean;
  chapters_extracted: number;
  error_message: string | null;
}

export interface GenerateOptions {
  title?: string;
  columns?: number;
  layout_style?: string;
  extract_screenshots?: boolean;
  api_key?: string;
}

export interface VerifyKeyResponse {
  valid: boolean;
  error?: string;
}

// ---- Calls ----------------------------------------------------------------
export async function uploadFile(file: File): Promise<UploadResponse> {
  const form = new FormData();
  form.append("file", file);
  const { data } = await apiClient.post<UploadResponse>("/api/v1/projects/upload", form);
  return data;
}

export async function generateDiagram(
  projectId: string,
  opts: GenerateOptions = {},
): Promise<GenerateResponse> {
  const { data } = await apiClient.post<GenerateResponse>("/api/v1/projects/generate", {
    project_id: projectId,
    ...opts,
  });
  return data;
}

export async function getExcalidraw(projectId: string): Promise<Record<string, unknown>> {
  const { data } = await apiClient.get(`/api/v1/projects/${projectId}/excalidraw`);
  return data as Record<string, unknown>;
}

export function downloadUrl(projectId: string): string {
  return `${API_BASE}/api/v1/projects/${projectId}/download`;
}

export async function verifyApiKey(apiKey: string): Promise<VerifyKeyResponse> {
  const { data } = await apiClient.post<VerifyKeyResponse>("/api/v1/projects/verify-key", {
    api_key: apiKey,
  });
  return data;
}
