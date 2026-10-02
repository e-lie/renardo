import { defineConfig } from 'vite'
import { svelte } from '@sveltejs/vite-plugin-svelte'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [
    tailwindcss(),
    svelte() // <-- Must come after Tailwind
  ],
  server: {
    host: '0.0.0.0',
    port: 54321,
    // same-origin API in dev: forward backend routes to the uvicorn server
    proxy: {
      '/api': 'http://127.0.0.1:8000',
      '/execute': 'http://127.0.0.1:8000',
      '/health': 'http://127.0.0.1:8000',
      '/ws': { target: 'ws://127.0.0.1:8000', ws: true }
    }
  },
  build: {
    outDir: 'dist',
    sourcemap: true
  }
})