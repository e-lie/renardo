# Plan d'implémentation - Layout Panes pour webclient_fresh

## Vue d'ensemble

Réimplémentation du système de panes de `webclient/NewCodeEditor.svelte` dans `webclient_fresh` en respectant l'architecture Flux-like avec séparation models/store/components.

**Exclusions** : Pas de système EditorContainer splits récursifs (déjà commenté dans ARCHITECTURE.md).

---

## 1. Modèles de données

### 1.1 `models/layout/`

**Fichier : `models/layout/Pane.interface.ts`**
```typescript
export type PanePosition =
  | 'top-menu'
  | 'left-top' | 'left-middle' | 'left-bottom'
  | 'right-top' | 'right-middle' | 'right-bottom'
  | 'bottom-left' | 'bottom-right'
  | 'center'

export interface PaneDimensions {
  width?: number
  height?: number
  minWidth?: number
  minHeight?: number
}

export interface PaneInterface {
  id: string
  position: PanePosition
  title: string
  dimensions: PaneDimensions
  isVisible: boolean
  isResizable: boolean
}
```

**Fichier : `models/layout/PaneTab.interface.ts`**
```typescript
export type PaneComponentType = 'ColorPicker' | 'TextArea' | 'CodeEditor'

export interface PaneTabInterface {
  id: string
  title: string
  componentType: PaneComponentType
  componentId: string
  closable: boolean
  active: boolean
}
```

**Fichier : `models/layout/index.ts`**
```typescript
export * from './Pane.interface'
export * from './PaneTab.interface'
```

---

## 2. Store de gestion d'état

### 2.1 `store/layout/models/`

**Fichier : `store/layout/models/LayoutState.interface.ts`**
```typescript
import type { PaneInterface, PaneTabInterface } from '@/models/layout'

export interface PaneSetVisibility {
  left: boolean
  right: boolean
  bottom: boolean
}

export interface HoverStates {
  left: boolean
  right: boolean
  bottom: boolean
}

export interface PaneSizes {
  'left-top': number
  'left-middle': number
  'left-bottom': number
  'right-top': number
  'right-middle': number
  'right-bottom': number
  'bottom-left': number
  'bottom-right': number
}

export interface ContainerSizes {
  'left-column': number
  'right-column': number
  'bottom-area': number
}

export interface LayoutStateInterface {
  panes: Map<string, PaneInterface>
  paneTabConfigs: Map<string, PaneTabInterface[]>
  paneVisibility: Map<string, boolean>
  paneSetVisibility: PaneSetVisibility
  hoverStates: HoverStates
  paneSizes: PaneSizes
  containerSizes: ContainerSizes
  isResizing: boolean
  hideAppNavbar: boolean
}
```

**Fichier : `store/layout/models/LayoutStore.interface.ts`**
```typescript
import type { Readable } from 'svelte/store'
import type { PanePosition, PaneTabInterface } from '@/models/layout'

export interface LayoutStoreActionsInterface {
  // Pane visibility
  togglePaneVisibility: (paneId: string) => void
  togglePaneSet: (setName: 'left' | 'right' | 'bottom') => void
  setPaneSetHover: (setName: string, isHovering: boolean) => void

  // Tabs
  addTab: (paneId: string, tab: Omit<PaneTabInterface, 'id'>) => void
  removeTab: (paneId: string, tabId: string) => void
  switchToTab: (paneId: string, tabId: string) => void

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
```

**Fichier : `store/layout/models/index.ts`**
```typescript
export * from './LayoutState.interface'
export * from './LayoutStore.interface'
```

### 2.2 `store/layout/Layout.store.ts`

**Implémentation principale** :
```typescript
import { writable, derived } from 'svelte/store'
import type {
  LayoutStateInterface,
  LayoutStoreInterface,
  LayoutStoreActionsInterface,
  LayoutStoreGettersInterface
} from './models'

// Private writable store
const writableLayoutStore = writable<LayoutStateInterface>({
  panes: new Map(),
  paneTabConfigs: new Map(),
  paneVisibility: new Map(),
  paneSetVisibility: { left: true, right: true, bottom: true },
  hoverStates: { left: false, right: false, bottom: false },
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
})

// Initialize default layout
function initializeDefaultLayout() {
  // Implementation
}

export function useLayoutStore(): LayoutStoreInterface {
  // Actions
  const actions: LayoutStoreActionsInterface = {
    togglePaneVisibility: (paneId) => {
      writableLayoutStore.update(state => {
        const newVisibility = new Map(state.paneVisibility)
        newVisibility.set(paneId, !newVisibility.get(paneId))
        return { ...state, paneVisibility: newVisibility }
      })
    },

    togglePaneSet: (setName) => {
      writableLayoutStore.update(state => ({
        ...state,
        paneSetVisibility: {
          ...state.paneSetVisibility,
          [setName]: !state.paneSetVisibility[setName]
        }
      }))
    },

    // ... autres actions
  }

  // Getters
  const panes = derived(writableLayoutStore, $state =>
    Array.from($state.panes.values())
  )

  const visiblePanes = derived(writableLayoutStore, $state =>
    Array.from($state.panes.values()).filter(pane => pane.isVisible)
  )

  const getters: LayoutStoreGettersInterface = {
    panes,
    visiblePanes,
    paneSetVisibility: derived(writableLayoutStore, $state => $state.paneSetVisibility),
    // ... autres getters

    hasPanesVisible: (setName) => {
      // Implementation
    },

    getPaneTabConfigs: (paneId) => {
      // Implementation
    }
  }

  return { actions, getters }
}
```

**Fichier : `store/layout/index.ts`**
```typescript
export * from './Layout.store'
export * from './models'
```

---

## 3. Composants primitifs

### 3.1 Resize Handle

**Fichier : `components/primitives/layout/ElResizeHandle.svelte`**
```svelte
<script lang="ts">
  let {
    direction = 'horizontal',
    onresizestart,
    testid = 'resize-handle'
  }: {
    direction?: 'horizontal' | 'vertical'
    onresizestart?: (event: MouseEvent) => void
    testid?: string
  } = $props()

  const cursorClass = $derived(
    direction === 'horizontal' ? 'cursor-col-resize' : 'cursor-row-resize'
  )

  const sizeClass = $derived(
    direction === 'horizontal' ? 'w-1' : 'h-1'
  )

  const cssClass = $derived(
    `${sizeClass} bg-surface-300 dark:bg-surface-600 ${cursorClass} hover:bg-primary-500 transition-colors`
  )
</script>

<div
  data-testid={testid}
  class={cssClass}
  onmousedown={onresizestart}
  role="separator"
></div>
```

### 3.2 Floating Toggle Button

**Fichier : `components/primitives/layout/ElFloatingToggle.svelte`**
```svelte
<script lang="ts">
  import type { Snippet } from 'svelte'

  let {
    position = 'left',
    onclick,
    onmouseenter,
    onmouseleave,
    title = '',
    testid = 'floating-toggle',
    children
  }: {
    position?: 'left' | 'right' | 'bottom'
    onclick?: () => void
    onmouseenter?: () => void
    onmouseleave?: () => void
    title?: string
    testid?: string
    children?: Snippet
  } = $props()

  const positionClasses = $derived.by(() => {
    if (position === 'left') return 'fixed left-4 top-1/2 -translate-y-1/2'
    if (position === 'right') return 'fixed right-4 top-1/2 -translate-y-1/2'
    return 'fixed bottom-2 left-1/2 -translate-x-1/2'
  })
</script>

<button
  data-testid={testid}
  class="w-8 h-8 rounded-full bg-transparent border-2 border-primary-500 text-primary-500 shadow-xl z-50 flex items-center justify-center {positionClasses}"
  {onclick}
  {onmouseenter}
  {onmouseleave}
  {title}
>
  {#if children}
    {@render children()}
  {/if}
</button>
```

---

## 4. Composants de domaine

### 4.1 Pane Container

**Fichier : `components/layout/PaneContainer.component.svelte`**
```svelte
<script lang="ts">
  import type { PanePosition } from '@/models/layout'
  import TabbedPane from './children/TabbedPane.component.svelte'

  let {
    position,
    width,
    height,
    minWidth,
    minHeight
  }: {
    position: PanePosition
    width?: number
    height?: number
    minWidth?: number
    minHeight?: number
  } = $props()

  const style = $derived.by(() => {
    let s = ''
    if (width) s += `width: ${width}px; `
    if (height) s += `height: ${height}px; `
    if (minWidth) s += `min-width: ${minWidth}px; `
    if (minHeight) s += `min-height: ${minHeight}px; `
    return s
  })

  const bgColor = $derived.by(() => {
    const colors = {
      'top-menu': 'bg-surface-200 dark:bg-surface-800',
      'left-top': 'bg-primary-500/10 dark:bg-primary-500/20',
      'left-middle': 'bg-primary-500/20 dark:bg-primary-500/30',
      'left-bottom': 'bg-secondary-500/10 dark:bg-secondary-500/20',
      'right-top': 'bg-tertiary-500/10 dark:bg-tertiary-500/20',
      'right-middle': 'bg-tertiary-500/20 dark:bg-tertiary-500/30',
      'right-bottom': 'bg-success-500/10 dark:bg-success-500/20',
      'bottom-left': 'bg-warning-500/10 dark:bg-warning-500/20',
      'bottom-right': 'bg-error-500/10 dark:bg-error-500/20',
      'center': 'bg-surface-100 dark:bg-surface-900'
    }
    return colors[position] || 'bg-surface-100 dark:bg-surface-900'
  })

  const cssClass = $derived(`${bgColor} border border-surface-300 dark:border-surface-700 overflow-hidden`)
</script>

<div class={cssClass} {style}>
  <TabbedPane {position} />
</div>
```

### 4.2 Tabbed Pane

**Fichier : `components/layout/children/TabbedPane.component.svelte`**
```svelte
<script lang="ts">
  import type { PanePosition } from '@/models/layout'
  import { useLayoutStore } from '@/store/layout'
  import ColorPicker from './ColorPicker.component.svelte'
  import TextArea from './TextArea.component.svelte'

  let { position }: { position: PanePosition } = $props()

  const { getters, actions } = useLayoutStore()
  const tabs = $derived(getters.getPaneTabConfigs(position))
  const activeTab = $derived(tabs.find(t => t.active))

  const componentMap = {
    'ColorPicker': ColorPicker,
    'TextArea': TextArea,
    'CodeEditor': null // TODO: CodeEditor component
  }

  function handleSwitchTab(tabId: string) {
    actions.switchToTab(position, tabId)
  }

  function handleCloseTab(tabId: string) {
    actions.removeTab(position, tabId)
  }
</script>

<div class="h-full flex flex-col">
  {#if tabs.length > 1}
    <!-- Tab bar -->
    <div class="flex items-center bg-surface-200 dark:bg-surface-800 border-b border-surface-300 dark:border-surface-700">
      {#each tabs as tab}
        <button
          class="px-3 py-2 text-sm transition-colors {tab.active ? 'bg-surface-100 dark:bg-surface-900 border-b-2 border-primary-500' : 'hover:bg-surface-300 dark:hover:bg-surface-700'}"
          onclick={() => handleSwitchTab(tab.id)}
        >
          <span class="text-surface-900 dark:text-surface-50">{tab.title}</span>
          {#if tab.closable}
            <span
              class="ml-2 text-surface-600 dark:text-surface-400 hover:text-error-500"
              onclick={(e) => { e.stopPropagation(); handleCloseTab(tab.id) }}
            >×</span>
          {/if}
        </button>
      {/each}
    </div>
  {/if}

  <!-- Active tab content -->
  <div class="flex-1 overflow-hidden">
    {#if activeTab}
      <svelte:component this={componentMap[activeTab.componentType]} componentId={activeTab.componentId} />
    {/if}
  </div>
</div>
```

---

## 5. Vue principale

### 5.1 Layout View

**Fichier : `views/Layout.view.svelte`**
```svelte
<script lang="ts">
  import { onMount, onDestroy } from 'svelte'
  import { useLayoutStore } from '@/store/layout'
  import PaneContainer from '@/components/layout/PaneContainer.component.svelte'
  import ElResizeHandle from '@/components/primitives/layout/ElResizeHandle.svelte'
  import ElFloatingToggle from '@/components/primitives/layout/ElFloatingToggle.svelte'

  const { getters, actions } = useLayoutStore()
  const {
    paneSetVisibility,
    hoverStates,
    paneSizes,
    containerSizes,
    hideAppNavbar
  } = getters

  let resizeData = $state(null)

  onMount(() => {
    document.addEventListener('mousemove', handleGlobalMouseMove)
    document.addEventListener('keydown', handleKeyDown)
  })

  onDestroy(() => {
    document.removeEventListener('mousemove', handleGlobalMouseMove)
    document.removeEventListener('keydown', handleKeyDown)
  })

  function startResize(event, paneId, direction) {
    actions.startResize()
    resizeData = { paneId, direction, startPos: event.clientX, startSize: $paneSizes[paneId] }
    document.addEventListener('mousemove', handleResize)
    document.addEventListener('mouseup', endResize)
  }

  function handleResize(event) {
    if (!resizeData) return
    const delta = event.clientX - resizeData.startPos
    const newSize = Math.max(100, resizeData.startSize + delta)
    actions.updatePaneSize(resizeData.paneId, newSize)
  }

  function endResize() {
    actions.endResize()
    resizeData = null
    document.removeEventListener('mousemove', handleResize)
    document.removeEventListener('mouseup', endResize)
  }

  function handleGlobalMouseMove(event) {
    // Edge detection logic
  }

  function handleKeyDown(event) {
    // Keyboard shortcuts
  }
</script>

<div class="h-screen flex flex-col overflow-hidden">
  <!-- Top menu -->
  <div class="h-16 bg-surface-200">
    <!-- Action buttons -->
  </div>

  <!-- Main area -->
  <div class="flex flex-1 overflow-hidden">
    <!-- Left column -->
    {#if $paneSetVisibility.left}
      <div style="width: {$containerSizes['left-column']}px">
        <PaneContainer position="left-top" height={$paneSizes['left-top']} />
        <ElResizeHandle direction="vertical" onresizestart={(e) => startResize(e, 'left-top', 'vertical')} />
        <PaneContainer position="left-middle" height={$paneSizes['left-middle']} />
      </div>
      <ElResizeHandle direction="horizontal" />
    {/if}

    <!-- Center -->
    <div class="flex-1">
      <PaneContainer position="center" />
    </div>

    <!-- Right column -->
    {#if $paneSetVisibility.right}
      <ElResizeHandle direction="horizontal" />
      <div style="width: {$containerSizes['right-column']}px">
        <!-- Similar structure -->
      </div>
    {/if}
  </div>

  <!-- Floating toggle buttons -->
  {#if $hoverStates.left}
    <ElFloatingToggle position="left" onclick={() => actions.togglePaneSet('left')}>
      <!-- Arrow icon -->
    </ElFloatingToggle>
  {/if}
</div>
```

---

## 6. Services

### 6.1 Edge Detection Service

**Fichier : `services/layout/edgeDetection.service.ts`**
```typescript
export class EdgeDetectionService {
  private threshold = 20

  detectEdge(clientX: number, clientY: number): 'left' | 'right' | 'bottom' | null {
    const { innerWidth, innerHeight } = window

    if (clientX <= this.threshold) return 'left'
    if (clientX >= innerWidth - this.threshold) return 'right'
    if (clientY >= innerHeight - this.threshold) return 'bottom'

    return null
  }
}
```

---

## 7. Ordre d'implémentation

1. **Modèles** (`models/layout/`) - Définir interfaces
2. **Store State** (`store/layout/models/`) - Définir state interfaces
3. **Store Implementation** (`store/layout/Layout.store.ts`) - Implémenter actions/getters
4. **Primitives** (`components/primitives/layout/`) - ElResizeHandle, ElFloatingToggle
5. **Services** (`services/layout/`) - Edge detection
6. **Domain Components** (`components/layout/`) - PaneContainer, TabbedPane
7. **View** (`views/Layout.view.svelte`) - Assembler le tout
8. **Integration** - Tester et ajuster

---

## 8. Différences avec webclient

- ✅ Pas de système EditorContainer splits récursifs
- ✅ Utilisation Flux-like pattern (actions/getters)
- ✅ Séparation models/store/components
- ✅ TypeScript strict partout
- ✅ **Skeleton design system** au lieu de DaisyUI
- ✅ Svelte 5 runes (`$state`, `$derived`, `$effect`)

### 8.1 Migration Design System vers Skeleton

**Classes DaisyUI → Skeleton** :

| DaisyUI | Skeleton |
|---------|----------|
| `bg-base-100`, `bg-base-200`, `bg-base-300` | `bg-surface-100`, `bg-surface-200`, `bg-surface-300` |
| `btn btn-primary` | `btn variant-filled-primary` |
| `btn btn-ghost` | `btn variant-ghost` |
| `border-base-300` | `border-surface-300` |
| `text-base-content` | `text-surface-900 dark:text-surface-50` |
| `bg-primary/10`, `bg-primary/20` | `bg-primary-500/10`, `bg-primary-500/20` |
| `hover:bg-base-300` | `hover:bg-surface-300` |

**Tokens Skeleton** :
- Surface : `surface-50` → `surface-900` (backgrounds)
- Primary : `primary-50` → `primary-900` (brand colors)
- Secondary, Accent, Success, Warning, Error : même pattern

**Dark mode** : Skeleton gère automatiquement via `dark:` prefix.

---

## 9. Persistence

Export/import layout via `actions.exportLayout()` et `actions.importLayout(config)` :

```typescript
interface LayoutConfig {
  paneVisibility: Record<string, boolean>
  paneSetVisibility: PaneSetVisibility
  paneSizes: PaneSizes
  containerSizes: ContainerSizes
  hideAppNavbar: boolean
}
```

Stockage dans `localStorage` avec clé `renardo-layout-config`.
