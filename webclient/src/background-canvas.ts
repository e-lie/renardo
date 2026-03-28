import Hydra from 'hydra-synth'
import logger from './services/logger.service'

let hydraInstance: { canvas: HTMLCanvasElement; hydra: InstanceType<typeof Hydra> } | null = null
let hydraEnabled = true

const INITIAL_PATTERN = () => {
  const h = hydraInstance!.hydra.synth
  h.osc().mult(h.solid(.1,.1,.1)).out()
}

export function initBackgroundCanvas() {
  const container = document.getElementById('background-canvas-container')
  if (!container) {
    logger.error('initBackgroundCanvas', 'Background canvas container not found')
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

  hydraInstance = { canvas, hydra }

  // Run the initial pattern
  INITIAL_PATTERN()

  // Handle window resize
  const resize = () => {
    canvas.width = window.innerWidth
    canvas.height = window.innerHeight
  }
  window.addEventListener('resize', resize)

  return hydraInstance
}

export function executeHydraCode(code: string): { success: boolean; error?: string } {
  if (!hydraInstance) {
    const msg = 'Hydra not initialized'
    logger.error('executeHydraCode', msg)
    return { success: false, error: msg }
  }
  try {
    logger.debug('executeHydraCode', 'Executing hydra code', { codeLength: code.length })
    // Ensure canvas is visible when executing user code
    hydraInstance.canvas.style.display = ''
    // eslint-disable-next-line no-eval
    eval(code)
    return { success: true }
  } catch (e) {
    const msg = e instanceof Error ? e.message : String(e)
    logger.error('executeHydraCode', 'Hydra code execution error', { error: msg })
    return { success: false, error: msg }
  }
}

export function setHydraBackground(enabled: boolean): void {
  if (!hydraInstance) {
    logger.warn('setHydraBackground', 'Hydra not initialized')
    return
  }
  if (enabled === hydraEnabled) return
  hydraEnabled = enabled
  const { canvas, hydra } = hydraInstance
  if (enabled) {
    canvas.style.display = ''
    INITIAL_PATTERN()
    logger.debug('setHydraBackground', 'Hydra background enabled')
  } else {
    hydra.synth.hush()
    canvas.style.display = 'none'
    logger.debug('setHydraBackground', 'Hydra background disabled')
  }
}
