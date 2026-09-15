import path from "node:path";
import { fileURLToPath } from "node:url";
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

const dir = path.dirname(fileURLToPath(import.meta.url));
const khestraRoot = path.resolve(dir, "../../..");

export default defineConfig({
  plugins: [react()],
  publicDir: path.join(khestraRoot, "apps/cmmc/frontend/public"),
  resolve: {
    alias: {
      "@shared": path.join(khestraRoot, "shared/frontend"),
      "@cmmc": path.join(khestraRoot, "apps/cmmc/frontend/src"),
      "@soc2": path.join(khestraRoot, "apps/soc2/frontend/src"),
      "@aigov": path.join(khestraRoot, "apps/aigovernance/frontend/src"),
      "@iso27001": path.join(khestraRoot, "apps/iso27001/frontend/src"),
    },
  },
  server: {
    host: "127.0.0.1",
    port: 5173,
    strictPort: true,
    proxy: {
      // Neutral Core namespace — global collector/evidence infrastructure,
      // served by the standalone core service (8086).
      "/api/core": {
        target: "http://127.0.0.1:8086",
        changeOrigin: true,
        rewrite: (p) => p.replace(/^\/api\/core/, "/api"),
      },
      // Evidence Hub is served by Core too.
      "/api/evidence-hub": {
        target: "http://127.0.0.1:8086",
        changeOrigin: true,
      },
      "/api/posture": {
        target: "http://127.0.0.1:8086",
        changeOrigin: true,
      },
      "/api/cmmc": {
        target: "http://127.0.0.1:8081",
        changeOrigin: true,
        rewrite: (p) => p.replace(/^\/api\/cmmc/, "/api"),
      },
      "/api/soc2": {
        target: "http://127.0.0.1:8082",
        changeOrigin: true,
        rewrite: (p) => p.replace(/^\/api\/soc2/, "/api"),
      },
      "/api/ai-governance": {
        target: "http://127.0.0.1:8083",
        changeOrigin: true,
        rewrite: (p) => p.replace(/^\/api\/ai-governance\/?/, "/api/"),
      },
      "/api/iso27001": {
        target: "http://127.0.0.1:8085",
        changeOrigin: true,
        rewrite: (p) => p.replace(/^\/api\/iso27001/, "/api"),
      },
      // Global workspace services (merged into the Core/global app).
      "/api/settings": {
        target: "http://127.0.0.1:8086",
        changeOrigin: true,
      },
      "/api/personnel": {
        target: "http://127.0.0.1:8086",
        changeOrigin: true,
      },
      "/api/trust-center": {
        target: "http://127.0.0.1:8086",
        changeOrigin: true,
      },
      "/api": {
        target: "http://127.0.0.1:8081",
        changeOrigin: true,
      },
    },
  },
});
