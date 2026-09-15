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
      "@iso27001": path.join(khestraRoot, "apps/iso27001/frontend/src"),
    },
  },
  server: {
    host: "127.0.0.1",
    port: 5177,
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
      "/api/iso27001": {
        target: process.env.ISO27001_API_URL ?? "http://127.0.0.1:8085",
        rewrite: (p) => p.replace(/^\/api\/iso27001/, "/api"),
      },
      "/api": process.env.ISO27001_API_URL ?? "http://127.0.0.1:8085",
    },
  },
});
