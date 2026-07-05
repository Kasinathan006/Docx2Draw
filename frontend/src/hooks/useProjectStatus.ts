"use client";

import useSWR from "swr";
import { apiClient, type JobStatusResponse } from "@/lib/api";

const fetcher = (url: string) => apiClient.get<JobStatusResponse>(url).then((res) => res.data);

/**
 * Real-time job polling (guide §6.3). Polls every second until the job
 * reaches a terminal state, then stops.
 */
export function useProjectStatus(jobId: string | null) {
  const { data, error, mutate } = useSWR<JobStatusResponse>(
    jobId ? `/api/v1/projects/${jobId}/status` : null,
    fetcher,
    {
      refreshInterval: (latest?: JobStatusResponse) => {
        if (latest && (latest.status === "done" || latest.status === "error")) {
          return 0;
        }
        return 1000;
      },
      revalidateOnFocus: false,
    },
  );

  return {
    data,
    status: data?.status,
    stage: data?.stage,
    progress: data?.progress ?? 0,
    message: data?.message ?? "",
    chapters: data?.chapters_extracted ?? 0,
    isDone: data?.status === "done",
    isError: data?.status === "error",
    errorMessage: data?.error_message ?? null,
    fetchError: error,
    refresh: mutate,
  };
}
