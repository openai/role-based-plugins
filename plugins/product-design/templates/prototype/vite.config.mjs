import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { fileURLToPath } from "node:url";

export default defineConfig({
  resolve: {
    alias: {
      "motion/react": fileURLToPath(
        new URL("./node_modules/motion/dist/es/react.mjs", import.meta.url)
      ),
    },
  },
  optimizeDeps: {
    include: ["react", "react-dom/client", "motion/react"],
  },
  server: {
    warmup: {
      clientFiles: ["./src/main.jsx"],
    },
  },
  plugins: [react()],
});
