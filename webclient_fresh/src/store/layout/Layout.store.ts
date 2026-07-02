# Layout Store Implementation

import { writable, derived, type Writable, type Readable } from 'svelte/store'
import type { 
  LayoutStateInterface, 
  PaneStateInterface,
  LayoutStoreInterface,
  LayoutStoreActionsInterface,
  LayoutStoreGettersInterface
} from './models'

// Private writable store
const writableLayoutStore = writable<LayoutStateInterface>({
  panes: {
    'left-top': {
      id: 'left-top',
      position: 'left-top',
      title: 'Left Top',
      isVisible: false,
      isResizable: true,
      dimensions: { width: 300, minWidth: 200, height: 300, minHeight: 200 },
      tabs: [{
        id: 'left-top-tab-1',
        paneId: 'left-top',
        title: 'Notes',
        componentType: 'TextArea',
        isActive: true,
        isCloseable: true
      }],
      activeTabId: 'left-top-tab-1'
    },
    'left-bottom': {
      id: 'left-bottom',
      position: 'left-bottom',
      title: 'Left Bottom',
      isVisible: false,
      isResizable: true,
      dimensions: { width: 300, minWidth: 200, height: 200, minHeight: 150 },
      tabs: [{
        id: 'left-bottom-tab-1',
        paneId: 'left-bottom',
        title: 'Scratch',
        componentType: 'TextArea',
        isActive: true,
        isCloseable: true
      }],
      activeTabId: 'left-bottom-tab-1'
    },
    'right-top': {
      id: 'right-top',
      position: 'right-top',
      title: 'Right Top',
      isVisible: false,
      isResizable: true,
      dimensions: { width: 300, minWidth: 200, height: 300, minHeight: 200 },
      tabs: [{
        id: 'right-top-tab-1',
        paneId: 'right-top',
        title: 'Workspace',
        componentType: 'TextArea',
        isActive: true,
        isCloseable: true
      }],
      activeTabId: 'right-top-tab-1'
    },
    'right-bottom': {
      id: 'right-bottom',
      position: 'right-bottom',
      title: 'Right Bottom',
      isVisible: false,
      isResizable: true,
      dimensions: { width: 300, minWidth: 200, height: 200, minHeight: 150 },
      tabs: [{
        id: 'right-bottom-tab-1',
        paneId: 'right-bottom',
        title: 'Debug',
        componentType: 'TextArea',
        isActive: true,
        isCloseable: true
      }],
      activeTabId: 'right-bottom-tab-1'
    },
    'bottom-left': {
      id: 'bottom-left',
      position: 'bottom-left',
      title: 'Bottom Left',
      isVisible: false,
      isResizable: true,
      dimensions: { width: 400, minWidth: 300, height: 200, minHeight: 150 },
      tabs: [{
        id: 'bottom-left-tab-1',
        paneId: 'bottom-left',
        title: 'Output',
        componentType: 'TextArea',
        isActive: true,
        isCloseable: true
      }],
      activeTabId: 'bottom-left-tab-1'
    },
    'bottom-right': {
      id: 'bottom-right',
      position: 'bottom-right',
      title: 'Bottom Right',
      isVisible: false,
      isResizable: true,
      dimensions: { width: 400, minWidth: 300, height: 200, minHeight: 150 },
      tabs: [{
        id: 'bottom-right-tab-1',
        paneId: 'bottom-right',
        title: 'Console',
        componentType: 'TextArea',
        isActive: true,
        isCloseable: true
      }],
      activeTabId: 'bottom-right-tab-1'
    },
    'center': {
      id: 'center',
      position: 'center',
      title: 'Code Editor',
      isVisible: true,
      isResizable: true,
      dimensions: { width: 400, minWidth: 300, height: 400, minHeight: 300 },
      tabs: [],
      activeTabId: null
    }
  },
  isResizing: false,
  globalSettings: {
    theme: 'dark',
    showPaneTitles: true,
    enableAnimations: true
  }
})

// Public hook
export function useLayoutStore(): LayoutStoreInterface {
  // Actions: modify state
  const actions: LayoutStoreActionsInterface = {
    togglePaneVisibility: (position: string) => {
      const positions = {
        left: ['left-top', 'left-bottom'],
        right: ['right-top', 'right-bottom'],
        bottom: ['bottom-left', 'bottom-right']
      }
      
      const positionsToToggle = positions[position as keyof typeof positions] || [position]
      const anyVisible = positionsToToggle.some(pos => 
        writableLayoutStore.get().panes[pos]?.isVisible
      )
      
      writableLayoutStore.update(state => {
        const newPanes = { ...state.panes }
        positionsToToggle.forEach(pos => {
          if (newPanes[pos]) {
            newPanes[pos] = { ...newPanes[pos], isVisible: !anyVisible }
          }
        })
        return { ...state, panes: newPanes }
      })
    },
    
    setPaneVisibility: (position: string, visible: boolean) => {
      writableLayoutStore.update(state => ({
        ...state,
        panes: {
          ...state.panes,
          [position]: {
            ...state.panes[position],
            isVisible: visible
          }
        }
      }))
    },
    
    updatePaneDimensions: (position: string, dimensions: Partial<LayoutDimensionsInterface>) => {
      writableLayoutStore.update(state => ({
        ...state,
        panes: {
          ...state.panes,
          [position]: {
            ...state.panes[position],
            dimensions: {
              ...state.panes[position].dimensions,
              ...dimensions
            }
          }
        }
      }))
    },
    
    resetLayout: () => {
      // Reset to default state
      const defaultState = writableLayoutStore.get()
      writableLayoutStore.update(state => ({
        ...state,
        panes: Object.fromEntries(
          Object.entries(state.panes).map(([key, pane]) => [
            key,
            { ...pane, isVisible: key === 'center' }
          ])
        )
      }))
    }
  }

  // Getters: read-only derived stores
  const panes = derived(writableLayoutStore, $state => $state.panes)
  const visiblePanes = derived(writableLayoutStore, $state => 
    Object.fromEntries(
      Object.entries($state.panes).filter(([_, pane]) => pane.isVisible)
    )
  )
  const isResizing = derived(writableLayoutStore, $state => $state.isResizing)
  const globalSettings = derived(writableLayoutStore, $state => $state.globalSettings)

  const getters: LayoutStoreGettersInterface = {
    panes,
    visiblePanes,
    isResizing,
    globalSettings
  }

  return { actions, getters }
}