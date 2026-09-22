import tailwindcss from '@tailwindcss/vite'
import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// In development the UI talks to the FastAPI backend through this proxy so the
// browser only ever sees same-origin /api/* calls (no CORS, no env juggling).
// In Docker, nginx performs the same job (see nginx.conf).
export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: process.env.BACKEND_URL ?? 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
