import { createClient, type SupabaseClient } from "@supabase/supabase-js";

const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
const anonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

/** True only when Supabase env vars are present. Auth UI degrades gracefully otherwise. */
export const isSupabaseEnabled: boolean = Boolean(url && anonKey);

/** Supabase client, or null when unconfigured (guest-only mode). */
export const supabase: SupabaseClient | null = isSupabaseEnabled
  ? createClient(url as string, anonKey as string)
  : null;
