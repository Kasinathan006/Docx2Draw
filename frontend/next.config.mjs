/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // @excalidraw/excalidraw ships browser-only code; keep it out of server bundling.
  transpilePackages: ["@excalidraw/excalidraw"],
  // Type-checking stays on (catches real errors); ESLint setup is optional for the build.
  eslint: {
    ignoreDuringBuilds: true,
  },
};

export default nextConfig;
