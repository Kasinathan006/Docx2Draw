"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { FolderOpen, Plus } from "lucide-react";
import { Button } from "@/components/ui/button";
import ProjectCard, { type ProjectRecord } from "@/components/dashboard/ProjectCard";
import { getProjects } from "@/lib/projects";

export default function DashboardPage() {
  const [projects, setProjects] = useState<ProjectRecord[]>([]);

  useEffect(() => {
    setProjects(getProjects());
  }, []);

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-800 dark:text-slate-100">Your projects</h1>
          <p className="text-sm text-slate-500 dark:text-slate-400">
            Visual maps you have generated on this device.
          </p>
        </div>
      </div>

      {projects.length === 0 ? (
        <div className="flex flex-col items-center justify-center rounded-2xl border border-dashed border-slate-300 py-20 text-center dark:border-slate-700">
          <FolderOpen className="mb-4 h-12 w-12 text-slate-300" />
          <p className="font-medium text-slate-600 dark:text-slate-300">No projects yet</p>
          <p className="mb-6 mt-1 text-sm text-slate-400">Upload a document to generate your first visual map.</p>
          <Link href="/dashboard/new">
            <Button>
              <Plus className="h-4 w-4" /> New project
            </Button>
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
          {projects.map((p) => (
            <ProjectCard key={p.projectId} project={p} />
          ))}
        </div>
      )}
    </div>
  );
}
