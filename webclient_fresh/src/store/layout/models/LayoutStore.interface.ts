import type { Readable } from 'svelte/store'
import type { PaneInterface, PaneTabInterface } from '../../../models/layout'
import type { PaneSetVisibility, HoverStates, PaneSizes, ContainerSizes } from './LayoutState.interface'

export interface LayoutStoreActionsInterface {
  // Pane visibility
  togglePaneVisibility: (paneId: string) => void
  togglePaneSet: (setName: 'left' | 'right' | 'bottom') => void
  setPaneSetHover: (setName: string, isHovering: boolean) => void

  // Tabs
  addTab: (paneId: string, tab: Omit<PaneTabInterface, 'id'>) => void
  removeTab: (paneId: string, tabId: string) => void
  switchToTab: (paneId: string, tabId: string) => void
  moveTab: (paneId: string, tabId: string, direction: 'up' | 'down') => void

  // Resize
  startResize: () => void
  endResize: () => void
  updatePaneSize: (paneId: string, size: number) => void
  updateContainerSize: (containerId: string, size: number) => void

  // Navbar
  toggleNavbar: (hide: boolean) => void

  // Layout persistence
  exportLayout: () => any
  importLayout: (config: any) => void
}

export interface LayoutStoreGettersInterface {
  panes: Readable<PaneInterface[]>
  visiblePanes: Readable<PaneInterface[]>
  paneVisibility: Readable<Map<string, boolean>>
  paneTabConfigs: Readable<Map<string, PaneTabInterface[]>>
  paneSetVisibility: Readable<PaneSetVisibility>
  hoverStates: Readable<HoverStates>
  paneSizes: Readable<PaneSizes>
  containerSizes: Readable<ContainerSizes>
  isResizing: Readable<boolean>
  hideAppNavbar: Readable<boolean>

  // Helpers
  hasPanesVisible: (setName: 'left' | 'right' | 'bottom') => boolean
  getPaneTabConfigs: (paneId: string) => PaneTabInterface[]
}

export interface LayoutStoreInterface {
  actions: LayoutStoreActionsInterface
  getters: LayoutStoreGettersInterface
}
