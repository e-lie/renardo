export class EdgeDetectionService {
  private threshold = 20

  detectEdge(
    clientX: number,
    clientY: number,
    paneSetVisibility?: { left: boolean; right: boolean; bottom: boolean },
    containerSizes?: { 'left-column': number; 'right-column': number; 'bottom-area': number }
  ): 'left' | 'right' | 'bottom' | null {
    const { innerWidth, innerHeight } = window

    // Left edge: check pane edge if open, otherwise screen edge
    if (paneSetVisibility?.left && containerSizes) {
      if (clientX >= containerSizes['left-column'] - this.threshold &&
          clientX <= containerSizes['left-column'] + this.threshold) {
        return 'left'
      }
    } else if (clientX <= this.threshold) {
      return 'left'
    }

    // Right edge: check pane edge if open, otherwise screen edge
    if (paneSetVisibility?.right && containerSizes) {
      const rightEdge = innerWidth - containerSizes['right-column']
      if (clientX >= rightEdge - this.threshold &&
          clientX <= rightEdge + this.threshold) {
        return 'right'
      }
    } else if (clientX >= innerWidth - this.threshold) {
      return 'right'
    }

    // Bottom edge: check pane edge if open, otherwise screen edge
    if (paneSetVisibility?.bottom && containerSizes) {
      const bottomEdge = innerHeight - containerSizes['bottom-area']
      if (clientY >= bottomEdge - this.threshold &&
          clientY <= bottomEdge + this.threshold) {
        return 'bottom'
      }
    } else if (clientY >= innerHeight - this.threshold) {
      return 'bottom'
    }

    return null
  }

  isNearButtonArea(
    edge: 'left' | 'right' | 'bottom',
    clientX: number,
    clientY: number,
    paneSetVisibility?: { left: boolean; right: boolean; bottom: boolean },
    containerSizes?: { 'left-column': number; 'right-column': number; 'bottom-area': number }
  ): boolean {
    const buttonAreaSize = 60
    const { innerWidth, innerHeight } = window

    if (edge === 'left') {
      if (paneSetVisibility?.left && containerSizes) {
        const paneEdge = containerSizes['left-column']
        return clientX >= paneEdge - buttonAreaSize && clientX <= paneEdge + buttonAreaSize
      }
      return clientX <= buttonAreaSize
    } else if (edge === 'right') {
      if (paneSetVisibility?.right && containerSizes) {
        const paneEdge = innerWidth - containerSizes['right-column']
        return clientX >= paneEdge - buttonAreaSize && clientX <= paneEdge + buttonAreaSize
      }
      return clientX >= innerWidth - buttonAreaSize
    } else if (edge === 'bottom') {
      if (paneSetVisibility?.bottom && containerSizes) {
        const paneEdge = innerHeight - containerSizes['bottom-area']
        return clientY >= paneEdge - buttonAreaSize && clientY <= paneEdge + buttonAreaSize
      }
      return clientY >= innerHeight - buttonAreaSize
    }

    return false
  }
}

export const edgeDetectionService = new EdgeDetectionService()
