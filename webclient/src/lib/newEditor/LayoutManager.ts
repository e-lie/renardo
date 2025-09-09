import { writable, derived, get, type Writable, type Readable } from 'svelte/store';
import { Pane, type PanePosition, type PaneDimensions } from './Pane';

export interface LayoutState {
  panes: Map<string, Pane>;
  isResizing: boolean;
  globalSettings: {
    theme: string;
    showPaneTitles: boolean;
    enableAnimations: boolean;
  };
}

export interface CreatePaneOptions {
  title?: string;
  dimensions?: PaneDimensions;
  isResizable?: boolean;
  isVisible?: boolean;
  defaultTabs?: {
    title: string;
    componentType: string;
    componentProps?: Record<string, any>;
    isCloseable?: boolean;
  }[];
}

/**
 * LayoutManager manages the entire layout system with resizable panes
 */
export class LayoutManager {
  private _state: Writable<LayoutState>;
  
  // Derived stores for easy access
  public readonly panes: Readable<Pane[]>;
  public readonly visiblePanes: Readable<Pane[]>;
  public readonly isResizing: Readable<boolean>;
  public readonly globalSettings: Readable<LayoutState['globalSettings']>;

  constructor() {
    this._state = writable({
      panes: new Map(),
      isResizing: false,
      globalSettings: {
        theme: 'dark',
        showPaneTitles: true,
        enableAnimations: true
      }
    });

    // Derived stores
    this.panes = derived(this._state, $state => 
      Array.from($state.panes.values())
    );

    this.visiblePanes = derived(this._state, $state => 
      Array.from($state.panes.values()).filter(pane => 
        pane.getState().isVisible
      )
    );

    this.isResizing = derived(this._state, $state => $state.isResizing);
    this.globalSettings = derived(this._state, $state => $state.globalSettings);

    // Initialize default panes
    this.initializeDefaultLayout();
  }

  /**
   * Initialize the default 8-pane layout
   */
  private initializeDefaultLayout(): void {
    const defaultPanes: Array<{
      id: string;
      position: PanePosition;
      title: string;
      dimensions: PaneDimensions;
      defaultTabs?: CreatePaneOptions['defaultTabs'];
    }> = [
      {
        id: 'top-menu',
        position: 'top-menu',
        title: 'Menu',
        dimensions: { height: 60, minHeight: 40, maxHeight: 100 },
        defaultTabs: [
          { 
            title: 'Main Menu', 
            componentType: 'TopMenu', 
            isCloseable: false 
          }
        ]
      },
      {
        id: 'left-top',
        position: 'left-top',
        title: 'Left Top',
        dimensions: { width: 300, minWidth: 200, height: 300, minHeight: 200 }
      },
      {
        id: 'left-bottom',
        position: 'left-bottom',
        title: 'Left Bottom',
        dimensions: { width: 300, minWidth: 200, height: 200, minHeight: 150 }
      },
      {
        id: 'right-top',
        position: 'right-top',
        title: 'Right Top',
        dimensions: { width: 300, minWidth: 200, height: 300, minHeight: 200 }
      },
      {
        id: 'right-bottom',
        position: 'right-bottom',
        title: 'Right Bottom',
        dimensions: { width: 300, minWidth: 200, height: 200, minHeight: 150 }
      },
      {
        id: 'bottom-left',
        position: 'bottom-left',
        title: 'Bottom Left',
        dimensions: { width: 400, minWidth: 300, height: 200, minHeight: 150 }
      },
      {
        id: 'bottom-right',
        position: 'bottom-right',
        title: 'Bottom Right',
        dimensions: { width: 400, minWidth: 300, height: 200, minHeight: 150 }
      },
      {
        id: 'center',
        position: 'center',
        title: 'Code Editor',
        dimensions: { minWidth: 400, minHeight: 300 },
        defaultTabs: [
          { 
            title: 'Editor Placeholder', 
            componentType: 'EditorPlaceholder', 
            isCloseable: false 
          }
        ]
      }
    ];

    defaultPanes.forEach(paneConfig => {
      this.createPane(
        paneConfig.position,
        {
          title: paneConfig.title,
          dimensions: paneConfig.dimensions,
          defaultTabs: paneConfig.defaultTabs
        }
      );
    });
  }

  /**
   * Create a new pane at the specified position
   */
  createPane(position: PanePosition, options: CreatePaneOptions = {}): string {
    const paneId = options.title ? 
      `${position}-${options.title.toLowerCase().replace(/\s+/g, '-')}` : 
      position;
    
    const pane = new Pane(
      paneId,
      position,
      options.title || position,
      options.dimensions || {},
      options.isResizable !== false
    );

    // Add default tabs if provided
    if (options.defaultTabs) {
      options.defaultTabs.forEach(tab => {
        pane.addTab(
          tab.title,
          tab.componentType,
          tab.componentProps || {},
          tab.isCloseable !== false
        );
      });
    }

    // Set visibility
    if (options.isVisible !== undefined) {
      pane.setVisible(options.isVisible);
    }

    this._state.update(s => ({
      ...s,
      panes: new Map(s.panes).set(paneId, pane)
    }));

    return paneId;
  }

  /**
   * Get a pane by ID
   */
  getPane(paneId: string): Pane | null {
    const state = get(this._state);
    return state.panes.get(paneId) || null;
  }

  /**
   * Get pane by position
   */
  getPaneByPosition(position: PanePosition): Pane | null {
    const state = get(this._state);
    for (const pane of state.panes.values()) {
      if (pane.getState().position === position) {
        return pane;
      }
    }
    return null;
  }

  /**
   * Remove a pane
   */
  removePane(paneId: string): boolean {
    const state = get(this._state);
    
    if (!state.panes.has(paneId)) {
      return false;
    }

    const newPanes = new Map(state.panes);
    newPanes.delete(paneId);

    this._state.update(s => ({
      ...s,
      panes: newPanes
    }));

    return true;
  }

  /**
   * Add a tab to a specific pane
   */
  addTabToPane(
    paneId: string,
    title: string,
    componentType: string,
    componentProps: Record<string, any> = {},
    isCloseable: boolean = true
  ): string | null {
    const pane = this.getPane(paneId);
    if (!pane) {
      return null;
    }

    return pane.addTab(title, componentType, componentProps, isCloseable);
  }

  /**
   * Remove a tab from a pane
   */
  removeTabFromPane(paneId: string, tabId: string): boolean {
    const pane = this.getPane(paneId);
    if (!pane) {
      return false;
    }

    return pane.removeTab(tabId);
  }

  /**
   * Switch to a specific tab in a pane
   */
  switchToTab(paneId: string, tabId: string): boolean {
    const pane = this.getPane(paneId);
    if (!pane) {
      return false;
    }

    return pane.switchToTab(tabId);
  }

  /**
   * Start resize operation
   */
  startResize(): void {
    this._state.update(s => ({
      ...s,
      isResizing: true
    }));
  }

  /**
   * End resize operation
   */
  endResize(): void {
    this._state.update(s => ({
      ...s,
      isResizing: false
    }));
  }

  /**
   * Update pane dimensions
   */
  updatePaneDimensions(paneId: string, dimensions: Partial<PaneDimensions>): boolean {
    const pane = this.getPane(paneId);
    if (!pane) {
      return false;
    }

    pane.setDimensions(dimensions);
    return true;
  }

  /**
   * Toggle pane visibility
   */
  togglePaneVisibility(paneId: string): boolean {
    const pane = this.getPane(paneId);
    if (!pane) {
      return false;
    }

    pane.toggleVisibility();
    return true;
  }

  /**
   * Update global settings
   */
  updateGlobalSettings(settings: Partial<LayoutState['globalSettings']>): void {
    this._state.update(s => ({
      ...s,
      globalSettings: {
        ...s.globalSettings,
        ...settings
      }
    }));
  }

  /**
   * Reset layout to default
   */
  resetToDefault(): void {
    this._state.update(s => ({
      ...s,
      panes: new Map(),
      isResizing: false
    }));

    this.initializeDefaultLayout();
  }

  /**
   * Export layout configuration
   */
  exportLayout(): any {
    const state = get(this._state);
    return {
      globalSettings: state.globalSettings,
      panes: Array.from(state.panes.entries()).map(([id, pane]) => ({
        id,
        data: pane.toJSON()
      }))
    };
  }

  /**
   * Import layout configuration
   */
  importLayout(config: any): void {
    const panes = new Map<string, Pane>();
    
    for (const { id, data } of config.panes) {
      panes.set(id, Pane.fromJSON(data));
    }

    this._state.update(s => ({
      ...s,
      panes,
      globalSettings: config.globalSettings || s.globalSettings
    }));
  }

  /**
   * Get current state
   */
  getState(): LayoutState {
    return get(this._state);
  }

  /**
   * Subscribe to state changes
   */
  subscribe(callback: (state: LayoutState) => void) {
    return this._state.subscribe(callback);
  }
}