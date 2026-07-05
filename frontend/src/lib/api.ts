import axios from "axios";

export const API_BASE = (
  process.env.NEXT_PUBLIC_API_URL ||
  process.env.NEXT_PUBLIC_API_BASE ||
  "http://localhost:8000"
).replace(/\/$/, "");

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
