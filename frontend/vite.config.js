import { defineConfig } from "vite";

// Dev server for the voice-agent frontend.
// The Pipecat bot runs separately (default dev runner at http://localhost:7860).
export default defineConfig({
  server: {
    port: 5173,
    // Proxy the WebRTC offer endpoint to the Pipecat dev runner so the
    // browser can talk to the bot without CORS headaches during development.
    proxy: {
      "/api": {
        target: "http://localhost:7860",
        changeOrigin: true,
      },
    },
  },
});
