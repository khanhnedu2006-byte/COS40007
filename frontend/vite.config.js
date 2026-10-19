import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Chuyển tiếp /api sang backend FastAPI khi chạy dev
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: { "/api": "http://localhost:8000" },
  },
});
