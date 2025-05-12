/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './index.html',
    './src/**/*.{svelte,js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {},
  },
  plugins: ['daisyui'],
  daisyui: {
    themes: ["light", "dark", "default", "synthwave", "coffee", "pastel", "cyberpunk"],
  },
}