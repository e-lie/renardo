export class EdgeDetectionService {
  private threshold = 20

  detectEdge(clientX: number, clientY: number): 'left' | 'right' | 'bottom' | null {
    const { innerWidth, innerHeight } = window

    if (clientX <= this.threshold) return 'left'
    if (clientX >= innerWidth - this.threshold) return 'right'
    if (clientY >= innerHeight - this.threshold) return 'bottom'

    return null
  }

  isNearButtonArea(
    edge: 'left' | 'right' | 'bottom',
    clientX: number,
    clientY: number
  ): boolean {
    const buttonAreaSize = 60
    const { innerWidth, innerHeight } = window

    if (edge === 'left') {
      return clientX <= buttonAreaSize
    } else if (edge === 'right') {
      return clientX >= innerWidth - buttonAreaSize
    } else if (edge === 'bottom') {
      return clientY >= innerHeight - buttonAreaSize
    }

    return false
  }
}

export const edgeDetectionService = new EdgeDetectionService()
