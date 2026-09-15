import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "node:path";
import { fileURLToPath } from "node:url";

const dir = path.dirname(fileURLToPath(import.meta.url));
const khestraRoot = path.resolve(dir, "../../..");

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@shared": path.join(khestraRoot, "shared/frontend"),
      "@cmmc": path.join(khestraRoot, "apps/cmmc/frontend/src"),
    },
  },
  server: {
    host: "127.0.0.1",
    port: 5174,
    strictPort: true,
    proxy: {
      "/api/settings": {
        target: process.env.PLATFORM_API_URL ?? "http://127.0.0.1:8084",
        changeOrigin: true,
      },
      "/api/personnel": {
        target: process.env.PLATFORM_API_URL ?? "http://127.0.0.1:8084",
        changeOrigin: true,
      },
      "/api/cmmc": {
        target: process.env.PLATFORM_API_URL ?? "http://127.0.0.1:8081",
        rewrite: (p) => p.replace(/^\/api\/cmmc/, "/api"),
      },
      "/api": process.env.PLATFORM_API_URL ?? "http://127.0.0.1:8081",
    },
  },
});
