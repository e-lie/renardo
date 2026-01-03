import Hydra from 'hydra-synth'

export function initBackgroundCanvas() {
  const container = document.getElementById('background-canvas-container')
  if (!container) {
    console.error('Background canvas container not found')
    return
  }

  // Create canvas element
  const canvas = document.createElement('canvas')
  canvas.id = 'background-canvas'
  container.appendChild(canvas)

  // Set canvas size to window size
  canvas.width = window.innerWidth
  canvas.height = window.innerHeight

  // Initialize Hydra
  const hydra = new Hydra({
    canvas,
    detectAudio: false,
    enableStreamCapture: false,
  })

  // Make Hydra functions available globally on the hydra instance
  const h = hydra.synth

  // Run the Hydra code
  h.osc().contrast(.5).modulate(h.noise(3)).out()

  // Handle window resize
  const resize = () => {
    canvas.width = window.innerWidth
    canvas.height = window.innerHeight
  }
  window.addEventListener('resize', resize)

  return { canvas, hydra }
}
