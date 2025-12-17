# Layout State Interface

import type { LayoutDimensionsInterface, PanePosition } from '@/models/layout'

export interface PaneStateInterface {
  id: string
  position: PanePosition
  title: string
  isVisible: boolean
  isResizable: boolean
  dimensions: LayoutDimensionsInterface
  tabs: PaneTabStateInterface[]
  activeTabId: string | null
}

export interface PaneTabStateInterface {
  id: string
  paneId: string
  title: string
  componentType: string
  componentProps?: Record<string, any>
  isActive: boolean
  isCloseable: boolean
}

export interface LayoutStateInterface {
  panes: Record<string, PaneStateInterface>
  isResizing: boolean
  globalSettings: {
    theme: string
    showPaneTitles: boolean
    enableAnimations: boolean
  }
}