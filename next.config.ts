import type { NextConfig } from "next";

/**
 * Project site: https://<user>.github.io/StudyWeb/
 * Do not point this at a user site (<user>.github.io) — that would overwrite it.
 */
const rawBase = process.env.NEXT_PUBLIC_BASE_PATH ?? "/StudyWeb";
const basePath = rawBase === "/" ? "" : rawBase.replace(/\/$/, "");

const nextConfig: NextConfig = {
  output: "export",
  trailingSlash: true,
  images: { unoptimized: true },
  ...(basePath
    ? {
        basePath,
        assetPrefix: basePath,
      }
    : {}),
  env: {
    NEXT_PUBLIC_BASE_PATH: basePath,
  },
  allowedDevOrigins: ["127.0.0.1"],
  turbopack: {
    rules: {
      "*.css": {
        loaders: ["@tailwindcss/turbopack"],
        as: "*.css",
      },
    },
  },
};

export default nextConfig;
