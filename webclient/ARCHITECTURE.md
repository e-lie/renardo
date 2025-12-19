# Architecture NewCodeEditor

## Concepts principaux

### 1. Panes (Panneaux)
Zones rectangulaires redimensionnables organisées en grille.

**Positions fixes** :
- `top-menu` : Barre d'actions (Run, Stop, Save...)
- `left-top`, `left-middle`, `left-bottom` : Colonne gauche
- `right-top`, `right-middle`, `right-bottom` : Colonne droite
- `bottom-left`, `bottom-right` : Zone inférieure
- `center` : Éditeur principal (toujours visible)

**Visibilité** :
- Toggle individuel par pane
- Toggle par groupe : `left`, `right`, `bottom`
- Détection edge (20px) pour show/hide automatique

**Redimensionnement** :
- Handles verticaux/horizontaux avec drag
- Contraintes : min 100px (panes), min 200px (containers)

<!-- ### 2. EditorContainer
Système récursif de splits pour CodeMirror.

**Types de container** :
- `LEAF` : Contient tabs avec CodeEditor
- `VERTICAL` : Split vertical (enfants côte à côte)
- `HORIZONTAL` : Split horizontal (enfants empilés)

**Opérations** :
- `splitVertical()` : Transforme leaf → 2 enfants verticaux
- `splitHorizontal()` : Transforme leaf → 2 enfants horizontaux
- `addTab()` : Ajoute tab dans leaf
- `removeTab()` : Supprime tab, collapse si dernier


**Collapse automatique** : Si 1 seul enfant reste après suppression, container adopte propriétés de l'enfant. -->

=> ne pas implémenter le système de split de l'EditorContainer dans la nouvelle architecture de webclient_fresh


### 3. TabbedPane
Affiche composants dans onglets multiples.

**Components supportés** :
- `ColorPicker` 🎨
- `TextArea` 📝
- `CodeEditor` 💻

**Fonctionnalités** :
- Switch entre tabs
- Drag & drop pour réorganiser
- Fermeture tabs (si closable)
- Tab bar masquée si 1 seul tab

## Classes TypeScript

### LayoutManager
Gestionnaire global du layout.

```typescript
class LayoutManager {
  - panes: Map<string, Pane>
  - globalSettings: { theme, showPaneTitles, enableAnimations }

  + createPane(position, options)
  + addTabToPane(paneId, title, componentType)
  + removeTabFromPane(paneId, tabId)
  + switchToTab(paneId, tabId)
  + exportLayout() / importLayout(config)
}
```

### PaneTabManager
Gestion tabs d'un pane.

```typescript
class PaneTabManager {
  - _tabs: Writable<TabConfig[]>
  - _activeTabId: Writable<string | null>
  - _components: Map<string, PaneComponent>

  + addTab(config): string
  + removeTab(tabId): void
  + switchToTab(tabId): void
  + reorderTabs(fromIndex, toIndex): void
}
```

### PaneComponent
Wrapper pour composant Svelte.

```typescript
class PaneComponent {
  - id, type, title
  - state: Writable<ComponentState>

  + setActive(active: boolean)
  + updateData(data: any)
}
```

## Composants Svelte

### NewCodeEditor.svelte
Composant racine avec layout flex.

**Structure** :
```
<top-menu>           // Actions + shortcuts
<main>
  <left-column>      // Panes left-*
  <center>           // EditorContainer
  <right-column>     // Panes right-*
  <bottom-area>      // Panes bottom-*
</main>
```

**State local** :
- `paneVisibility` : Map position → boolean
- `paneSetVisibility` : Map (left|right|bottom) → boolean
- `paneSizes` : Map position → px
- `paneTabConfigs` : Map position → TabConfig[]

### EditorContainer.svelte
Container récursif pour splits CodeMirror.

**Props** :
- `containerId` : ID unique
- `containerData` : State initial (type, tabs, children)
- `depth` : Profondeur récursion

**Events** :
- `containerChange` : Notifie parent de modifications
- `removeContainer` : Demande suppression au parent

**Récursion** : Utilise `<svelte:self>` pour splits enfants.

### TabbedPane.svelte
Pane avec tabs multiples.

**Props** :
- `position` : Position dans layout
- `initialTabs` : TabConfig[]

**Rendering** :
```svelte
{#if activeComponent}
  <svelte:component this={activeComponent.component} {...props} />
{/if}
```

## Fonctionnalités

### Resize
1. `mousedown` sur handle → `startResize()`
2. `mousemove` → calcul delta, update size
3. `mouseup` → `endResize()`, notifyParent

### Keyboard shortcuts
- `Ctrl+Enter` : Exécute paragraphe/sélection
- `Alt+Enter` : Exécute ligne courante
- `Ctrl+.` : Stop music

### Edge detection
```javascript
handleGlobalMouseMove(event) {
  if (clientX <= 20 && !paneSetVisible.left)
    showFloatingButton('left')
  if (clientX >= width - 20 && !paneSetVisible.right)
    showFloatingButton('right')
  if (clientY >= height - 20 && !paneSetVisible.bottom)
    showFloatingButton('bottom')
}
```

### Layout configuration
Modal permettant :
- Toggle visibilité panes
- Configuration tabs par pane
- Ajout/suppression tabs
- Toggle navbar app

## Persistence

**Export** :
```json
{
  "globalSettings": { "theme": "dark", ... },
  "panes": [
    { "id": "left-top", "data": { "tabs": [...], "dimensions": {...} } }
  ]
}
```

**Import** : Reconstruit LayoutManager depuis JSON.
