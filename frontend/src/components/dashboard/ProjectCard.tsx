"use client";

import Link from "next/link";
import { FileText, Layers } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";

export interface ProjectRecord {
  projectId: string;
  title: string;
  createdAt: number;
  status: "done" | "error" | "processing";
  chapters?: number;
}

const STATUS_VARIANT = {
  done: "success",
  error: "error",
  processing: "warning",
} as const;

export default function ProjectCard({ project }: { project: ProjectRecord }) {
  const date = new Date(project.createdAt).toLocaleDateString();
  return (
    <Link href={`/editor/${project.projectId}`}>
      <Card className="group cursor-pointer p-5 transition hover:-translate-y-0.5 hover:shadow-md">
        <div className="mb-3 flex items-start justify-between">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-brand-100 text-brand-600">
            <FileText className="h-5 w-5" />
          </div>
          <Badge variant={STATUS_VARIANT[project.status]}>{project.status}</Badge>
        </div>
        <h3 className="truncate font-semibold text-slate-800 group-hover:text-brand-700 dark:text-slate-100">
          {project.title}
        </h3>
        <div className="mt-2 flex items-center gap-3 text-xs text-slate-400">
          <span className="inline-flex items-center gap-1">
            <Layers className="h-3.5 w-3.5" /> {project.chapters ?? 0} chapters
          </span>
          <span>{date}</span>
        </div>
      </Card>
    </Link>
  );
}
