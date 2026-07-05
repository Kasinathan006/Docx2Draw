/** @type {import('next').NextConfig} */
const BACKEND_URL =
  process.env.NEXT_PUBLIC_API_URL ||
  process.env.BACKEND_URL ||
  "http://localhost:8000";

const nextConfig = {
  reactStrictMode: true,
  // @excalidraw/excalidraw ships browser-only code; keep it out of server bundling.
  transpilePackages: ["@excalidraw/excalidraw"],
  // Type-checking stays on (catches real errors); ESLint setup is optional for the build.
  eslint: {
    ignoreDuringBuilds: true,
  },
  /**
   * Proxy /api/v1/* → backend so that the browser never calls the backend
   * directly (avoids CORS entirely). Vercel rewrites happen server-side.
   * Local dev: calls go to http://localhost:8000
   * Cloud:     set NEXT_PUBLIC_API_URL in Vercel env → calls go to Render
   */
  async rewrites() {
    return [
      {
        source: "/api/v1/:path*",
        destination: `${BACKEND_URL}/api/v1/:path*`,
      },
      {
        source: "/health",
        destination: `${BACKEND_URL}/health`,
      },
    ];
  },
};

export default nextConfig;

