import { defineConfig } from 'vite';
import { svelte } from '@sveltejs/vite-plugin-svelte';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [svelte()],
  optimizeDeps: {
    exclude: [
      "svelte-codemirror-editor",
      "codemirror",
      "@codemirror/language-javascript",
      "@codemirror/basic-setup",
      "@codemirror/lang-python",
      "@codemirror/theme-one-dark",
      ],
  },
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:12345',
        changeOrigin: true
      },
      '/ws': {
        target: 'ws://localhost:12345',
        ws: true
      }
    }
  }
});