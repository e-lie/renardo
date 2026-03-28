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
    port: 3001
  },
  build: {
    outDir: 'dist',
    sourcemap: true
  }
})