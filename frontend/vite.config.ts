import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

// One build, two homes:
//  - the Python backend serves the output at /ui/ (a browser UI), and
//  - Tauri wraps the same output in a native window.
// base "./" keeps asset paths relative so both the /ui/ sub-path and Tauri's
// file:// loading resolve correctly. Output lands directly in the package's
// web/ folder that FastAPI serves.
export default defineConfig({
  plugins: [react()],
  base: "./",
  root: ".",
  build: {
    outDir: "../src/purple/web",
    emptyOutDir: true,
  },
  server: {
    port: 5173,
    strictPort: true,
  },
});
