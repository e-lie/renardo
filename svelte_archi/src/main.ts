// file: src/main.ts
import App from './App.svelte'
// import tailwind main css file
import './tailwind/app.css'

const app = new App({
  target: document.getElementById('app')
})

export default app
