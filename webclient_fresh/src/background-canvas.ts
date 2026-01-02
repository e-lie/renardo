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
  const resize = () => {
    canvas.width = window.innerWidth
    canvas.height = window.innerHeight
    drawGradient()
  }

  // Draw purple to black gradient
  const drawGradient = () => {
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    // Create diagonal gradient (top-left to bottom-right)
    const gradient = ctx.createLinearGradient(0, 0, canvas.width, canvas.height)

    // Purple to black gradient
    gradient.addColorStop(0, '#5a3f9e')    // Purple
    gradient.addColorStop(0.25, '#3d2a6d') // Dark purple
    gradient.addColorStop(0.5, '#221844')  // Very dark purple
    gradient.addColorStop(0.75, '#0f0a1f') // Almost black
    gradient.addColorStop(1, '#000000')    // Black

    ctx.fillStyle = gradient
    ctx.fillRect(0, 0, canvas.width, canvas.height)
  }

  // Initial draw
  resize()

  // Resize on window resize
  window.addEventListener('resize', resize)

  return canvas
}
