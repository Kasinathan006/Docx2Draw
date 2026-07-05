"use client";

import type { ProjectRecord } from "@/components/dashboard/ProjectCard";

const KEY = "doc2draw.projects";

/** Recent projects are persisted client-side so the dashboard works without a DB. */
export function getProjects(): ProjectRecord[] {
  if (typeof window === "undefined") return [];
  try {
    const raw = window.localStorage.getItem(KEY);
    return raw ? (JSON.parse(raw) as ProjectRecord[]) : [];
  } catch {
    return [];
  }
}

export function saveProject(record: ProjectRecord): void {
  if (typeof window === "undefined") return;
  const existing = getProjects().filter((p) => p.projectId !== record.projectId);
  const next = [record, ...existing].slice(0, 50);
  window.localStorage.setItem(KEY, JSON.stringify(next));
}
