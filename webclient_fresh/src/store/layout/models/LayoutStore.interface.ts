# Layout Store Interfaces

import type { Writable, Readable } from 'svelte/store'
import type { LayoutStateInterface, LayoutDimensionsInterface } from '@/models/layout'

export interface LayoutStoreActionsInterface {
  togglePaneVisibility: (position: string) => void
  setPaneVisibility: (position: string, visible: boolean) => void
  updatePaneDimensions: (position: string, dimensions: Partial<LayoutDimensionsInterface>) => void
  resetLayout: () => void
}

export interface LayoutStoreGettersInterface {
  panes: Readable<LayoutStateInterface['panes']>
  visiblePanes: Readable<LayoutStateInterface['panes']>
  isResizing: Readable<LayoutStateInterface['isResizing']>
  globalSettings: Readable<LayoutStateInterface['globalSettings']>
}

export interface LayoutStoreInterface {
  actions: LayoutStoreActionsInterface
  getters: LayoutStoreGettersInterface
}