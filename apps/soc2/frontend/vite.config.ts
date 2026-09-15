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
    port: 5175,
    strictPort: true,
    proxy: {
      "/api/settings": {
        target: "http://127.0.0.1:8084",
        changeOrigin: true,
      },
      "/api/personnel": {
        target: "http://127.0.0.1:8084",
        changeOrigin: true,
      },
      "/api/soc2": {
        target: "http://127.0.0.1:8082",
        rewrite: (p) => p.replace(/^\/api\/soc2/, "/api"),
      },
      "/api": "http://127.0.0.1:8082",
    },
  },
});
