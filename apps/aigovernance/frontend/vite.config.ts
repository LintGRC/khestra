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
      "@aigov": path.join(khestraRoot, "apps/aigovernance/frontend/src"),
      "@cmmc": path.join(khestraRoot, "apps/aigovernance/frontend/src"),
    },
  },
  server: {
    host: "127.0.0.1",
    port: 5176,
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
      "/api/ai-governance": {
        target: process.env.PLATFORM_API_URL ?? "http://127.0.0.1:8083",
        rewrite: (p) => p.replace(/^\/api\/ai-governance/, "/api"),
      },
      "/api": process.env.PLATFORM_API_URL ?? "http://127.0.0.1:8083",
    },
  },
});
