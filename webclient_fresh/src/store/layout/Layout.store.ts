import { writable, derived, get } from 'svelte/store'
import type {
  LayoutStateInterface,
  LayoutStoreInterface,
  LayoutStoreActionsInterface,
  LayoutStoreGettersInterface
} from './models'
import type { PaneTabInterface } from '../../models/layout'

// Initial state
const initialState: LayoutStateInterface = {
  panes: new Map(),
  paneTabConfigs: new Map([
    ['top-menu', [
      { id: 'tab-top-menu-1', title: 'Menu', componentType: 'TopMenu', componentId: 'menu-1', closable: true, active: true }
    ]],
    ['center', [
      { id: 'tab-center-1', title: 'Code Editor', componentType: 'CodeEditor', componentId: 'editor-main', closable: true, active: true }
    ]],
    ['left-top', [
      { id: 'tab-left-top-1', title: 'Notes', componentType: 'TextArea', componentId: 'text-1', closable: true, active: true }
    ]],
    ['left-middle', [
      { id: 'tab-left-middle-1', title: 'Notes', componentType: 'TextArea', componentId: 'text-2', closable: true, active: true }
    ]],
    ['left-bottom', [
      { id: 'tab-left-bottom-1', title: 'Scratch', componentType: 'TextArea', componentId: 'text-scratch', closable: true, active: true }
    ]],
    ['right-top', [
      { id: 'tab-right-top-2', title: 'projectExplorer', componentType: 'ProjectExplorerTab', componentId: 'project-explorer-1', closable: true, active: false },
      { id: 'tab-right-top-1', title: 'tutorials', componentType: 'TutorialTab', componentId: 'tutorial-1', closable: true, active: true },
    ]],
    ['right-middle', [
      { id: 'tab-right-middle-1', title: 'Notes', componentType: 'TextArea', componentId: 'text-3', closable: true, active: true }
    ]],
    ['right-bottom', [
      { id: 'tab-right-bottom-1', title: 'Workspace', componentType: 'TextArea', componentId: 'text-2', closable: true, active: true }
    ]],
    ['bottom-left', [
      { id: 'tab-bottom-left-1', title: 'Draft', componentType: 'TextArea', componentId: 'text-4', closable: true, active: true }
    ]],
    ['bottom-right', [
      { id: 'tab-bottom-right-1', title: 'ฅ^•ﻌ•^ฅ >> output', componentType: 'ConsoleOutput', componentId: 'console-1', closable: true, active: true }
    ]]
  ]),
  paneVisibility: new Map([
    ['top-menu', true],
    ['left-top', true],
    ['left-middle', true],
    ['left-bottom', true],
    ['right-top', true],
    ['right-middle', false],
    ['right-bottom', false],
    ['bottom-left', false],
    ['bottom-right', true],
    ['center', true]
  ]),
  paneSetVisibility: {
    left: false,
    right: true,
    bottom: false
  },
  hoverStates: {
    left: false,
    right: false,
    bottom: false
  },
  paneSizes: {
    'left-top': 200,
    'left-middle': 200,
    'left-bottom': 200,
    'right-top': 200,
    'right-middle': 200,
    'right-bottom': 200,
    'bottom-left': 400,
    'bottom-right': 400
  },
  containerSizes: {
    'left-column': 300,
    'right-column': 300,
    'bottom-area': 200
  },
  isResizing: false,
  hideAppNavbar: false
}

// Private writable store
const writableLayoutStore = writable<LayoutStateInterface>(initialState)

// Public hook
export function useLayoutStore(): LayoutStoreInterface {
  // Actions
  const actions: LayoutStoreActionsInterface = {
    togglePaneVisibility: (paneId: string) => {
      writableLayoutStore.update(state => {
        const newVisibility = new Map(state.paneVisibility)
        newVisibility.set(paneId, !newVisibility.get(paneId))
        return { ...state, paneVisibility: newVisibility }
      })
    },

    togglePaneSet: (setName: 'left' | 'right' | 'bottom') => {
      writableLayoutStore.update(state => ({
        ...state,
        paneSetVisibility: {
          ...state.paneSetVisibility,
          [setName]: !state.paneSetVisibility[setName]
        }
      }))
    },

    setPaneSetHover: (setName: string, isHovering: boolean) => {
      writableLayoutStore.update(state => ({
        ...state,
        hoverStates: {
          ...state.hoverStates,
          [setName]: isHovering
        }
      }))
    },

    addTab: (paneId: string, tab: Omit<PaneTabInterface, 'id'>) => {
      writableLayoutStore.update(state => {
        const tabs = state.paneTabConfigs.get(paneId) || []
        const newTab: PaneTabInterface = {
          ...tab,
          id: `tab-${paneId}-${Date.now()}`,
          active: tabs.length === 0
        }

        const newTabConfigs = new Map(state.paneTabConfigs)
        newTabConfigs.set(paneId, [...tabs, newTab])

        return { ...state, paneTabConfigs: newTabConfigs }
      })
    },

    removeTab: (paneId: string, tabId: string) => {
      writableLayoutStore.update(state => {
        const tabs = state.paneTabConfigs.get(paneId) || []
        const filteredTabs = tabs.filter(t => t.id !== tabId)

        // If we removed the active tab, activate the first one
        if (tabs.find(t => t.id === tabId)?.active && filteredTabs.length > 0) {
          filteredTabs[0].active = true
        }

        const newTabConfigs = new Map(state.paneTabConfigs)
        newTabConfigs.set(paneId, filteredTabs)

        return { ...state, paneTabConfigs: newTabConfigs }
      })
    },

    switchToTab: (paneId: string, tabId: string) => {
      writableLayoutStore.update(state => {
        const tabs = state.paneTabConfigs.get(paneId) || []
        const updatedTabs = tabs.map(t => ({
          ...t,
          active: t.id === tabId
        }))

        const newTabConfigs = new Map(state.paneTabConfigs)
        newTabConfigs.set(paneId, updatedTabs)

        return { ...state, paneTabConfigs: newTabConfigs }
      })
    },

    moveTab: (paneId: string, tabId: string, direction: 'up' | 'down') => {
      writableLayoutStore.update(state => {
        const tabs = state.paneTabConfigs.get(paneId) || []
        const index = tabs.findIndex(t => t.id === tabId)

        if (index === -1) return state

        const newIndex = direction === 'up' ? index - 1 : index + 1
        if (newIndex < 0 || newIndex >= tabs.length) return state

        const newTabs = [...tabs]
        const [removed] = newTabs.splice(index, 1)
        newTabs.splice(newIndex, 0, removed)

        const newTabConfigs = new Map(state.paneTabConfigs)
        newTabConfigs.set(paneId, newTabs)

        return { ...state, paneTabConfigs: newTabConfigs }
      })
    },

    startResize: () => {
      writableLayoutStore.update(state => ({ ...state, isResizing: true }))
    },

    endResize: () => {
      writableLayoutStore.update(state => ({ ...state, isResizing: false }))
    },

    updatePaneSize: (paneId: string, size: number) => {
      writableLayoutStore.update(state => ({
        ...state,
        paneSizes: {
          ...state.paneSizes,
          [paneId]: size
        }
      }))
    },

    updateContainerSize: (containerId: string, size: number) => {
      writableLayoutStore.update(state => ({
        ...state,
        containerSizes: {
          ...state.containerSizes,
          [containerId]: size
        }
      }))
    },

    toggleNavbar: (hide: boolean) => {
      writableLayoutStore.update(state => ({ ...state, hideAppNavbar: hide }))
    },

    exportLayout: () => {
      const state = get(writableLayoutStore)
      return {
        paneVisibility: Object.fromEntries(state.paneVisibility),
        paneSetVisibility: state.paneSetVisibility,
        paneSizes: state.paneSizes,
        containerSizes: state.containerSizes,
        hideAppNavbar: state.hideAppNavbar
      }
    },

    importLayout: (config: any) => {
      writableLayoutStore.update(state => ({
        ...state,
        paneVisibility: new Map(Object.entries(config.paneVisibility || {})),
        paneSetVisibility: config.paneSetVisibility || state.paneSetVisibility,
        paneSizes: config.paneSizes || state.paneSizes,
        containerSizes: config.containerSizes || state.containerSizes,
        hideAppNavbar: config.hideAppNavbar || state.hideAppNavbar
      }))
    }
  }

  // Getters
  const panes = derived(writableLayoutStore, $state =>
    Array.from($state.panes.values())
  )

  const visiblePanes = derived(writableLayoutStore, $state =>
    Array.from($state.panes.values()).filter(pane => pane.isVisible)
  )

  const paneVisibility = derived(writableLayoutStore, $state => $state.paneVisibility)
  const paneTabConfigs = derived(writableLayoutStore, $state => $state.paneTabConfigs)

  const getters: LayoutStoreGettersInterface = {
    panes,
    visiblePanes,
    paneVisibility,
    paneTabConfigs,
    paneSetVisibility: derived(writableLayoutStore, $state => $state.paneSetVisibility),
    hoverStates: derived(writableLayoutStore, $state => $state.hoverStates),
    paneSizes: derived(writableLayoutStore, $state => $state.paneSizes),
    containerSizes: derived(writableLayoutStore, $state => $state.containerSizes),
    isResizing: derived(writableLayoutStore, $state => $state.isResizing),
    hideAppNavbar: derived(writableLayoutStore, $state => $state.hideAppNavbar),

    hasPanesVisible: (setName: 'left' | 'right' | 'bottom'): boolean => {
      const state = get(writableLayoutStore)
      if (setName === 'left') {
        return state.paneVisibility.get('left-top') ||
          state.paneVisibility.get('left-middle') ||
          state.paneVisibility.get('left-bottom') || false
      } else if (setName === 'right') {
        return state.paneVisibility.get('right-top') ||
          state.paneVisibility.get('right-middle') ||
          state.paneVisibility.get('right-bottom') || false
      } else if (setName === 'bottom') {
        return state.paneVisibility.get('bottom-left') ||
          state.paneVisibility.get('bottom-right') || false
      }
      return false
    },

    getPaneTabConfigs: (paneId: string): PaneTabInterface[] => {
      const state = get(writableLayoutStore)
      return state.paneTabConfigs.get(paneId) || []
    }
  }

  return { actions, getters }
}
