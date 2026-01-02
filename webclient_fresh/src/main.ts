import './app.css'
import { mount } from 'svelte'
import App from './App.svelte'
import { initBackgroundCanvas } from './background-canvas'

// Initialize background canvas
initBackgroundCanvas()

const app = mount(App, {
  target: document.getElementById('app')!,
})

export default app