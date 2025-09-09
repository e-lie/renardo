import { writable, derived, get, type Writable, type Readable } from 'svelte/store';
import { PaneTab, type PaneTabState } from './PaneTab';

export type PanePosition = 
  | 'top-menu'
  | 'left-top'
  | 'left-bottom' 
  | 'right-top'
  | 'right-bottom'
  | 'bottom-left'
  | 'bottom-right'
  | 'center';

export interface PaneDimensions {
  width?: number;  // in pixels or percentage
  height?: number; // in pixels or percentage
  minWidth?: number;
  minHeight?: number;
  maxWidth?: number;
  maxHeight?: number;
}

export interface PaneState {
  id: string;
  position: PanePosition;
  title: string;
  tabs: Map<string, PaneTab>;
  activeTabId: string | null;
  isVisible: boolean;
  isCollapsed: boolean;
  isResizable: boolean;
  dimensions: PaneDimensions;
  nextTabId: number;
}

/**
 * Pane represents a container that holds multiple tabs
 * Each pane can be resized and contains multiple switchable components via tabs
 */
export class Pane {
  private _state: Writable<PaneState>;
  
  // Derived stores for easy access
  public readonly id: Readable<string>;
  public readonly position: Readable<PanePosition>;
  public readonly title: Readable<string>;
  public readonly tabs: Readable<PaneTab[]>;
  public readonly activeTab: Readable<PaneTab | null>;
  public readonly isVisible: Readable<boolean>;
  public readonly isCollapsed: Readable<boolean>;
  public readonly isResizable: Readable<boolean>;
  public readonly dimensions: Readable<PaneDimensions>;

  constructor(
    id: string,
    position: PanePosition,
    title: string,
    dimensions: PaneDimensions = {},
    isResizable: boolean = true
  ) {
    this._state = writable({
      id,
      position,
      title,
      tabs: new Map(),
      activeTabId: null,
      isVisible: true,
      isCollapsed: false,
      isResizable,
      dimensions: {
        minWidth: 200,
        minHeight: 100,
        ...dimensions
      },
      nextTabId: 1
    });

    // Derived stores
    this.id = derived(this._state, $state => $state.id);
    this.position = derived(this._state, $state => $state.position);
    this.title = derived(this._state, $state => $state.title);
    this.tabs = derived(this._state, $state => 
      Array.from($state.tabs.values()).sort((a, b) => 
        a.getState().order - b.getState().order
      )
    );
    this.activeTab = derived(this._state, $state => 
      $state.activeTabId ? $state.tabs.get($state.activeTabId) || null : null
    );
    this.isVisible = derived(this._state, $state => $state.isVisible);
    this.isCollapsed = derived(this._state, $state => $state.isCollapsed);
    this.isResizable = derived(this._state, $state => $state.isResizable);
    this.dimensions = derived(this._state, $state => $state.dimensions);
  }

  /**
   * Get the current state synchronously
   */
  getState(): PaneState {
    return get(this._state);
  }

  /**
   * Add a new tab to this pane
   */
  addTab(
    title: string,
    componentType: string,
    componentProps: Record<string, any> = {},
    isCloseable: boolean = true
  ): string {
    const state = get(this._state);
    const tabId = `${state.id}-tab-${state.nextTabId}`;
    
    const tab = new PaneTab(
      tabId,
      state.id,
      title,
      componentType,
      componentProps,
      state.tabs.size,
      isCloseable
    );

    this._state.update(s => {
      const newTabs = new Map(s.tabs);
      newTabs.set(tabId, tab);
      
      return {
        ...s,
        tabs: newTabs,
        activeTabId: s.activeTabId || tabId, // Set as active if it's the first tab
        nextTabId: s.nextTabId + 1
      };
    });

    return tabId;
  }

  /**
   * Remove a tab from this pane
   */
  removeTab(tabId: string): boolean {
    const state = get(this._state);
    const tab = state.tabs.get(tabId);
    
    if (!tab || !tab.getState().isCloseable) {
      return false;
    }

    const newTabs = new Map(state.tabs);
    newTabs.delete(tabId);

    // Determine new active tab if the removed tab was active
    let newActiveTabId = state.activeTabId;
    if (state.activeTabId === tabId) {
      if (newTabs.size > 0) {
        // Find the first available tab
        newActiveTabId = Array.from(newTabs.keys())[0];
      } else {
        newActiveTabId = null;
      }
    }

    this._state.update(s => ({
      ...s,
      tabs: newTabs,
      activeTabId: newActiveTabId
    }));

    return true;
  }

  /**
   * Switch to a specific tab
   */
  switchToTab(tabId: string): boolean {
    const state = get(this._state);
    
    if (!state.tabs.has(tabId)) {
      return false;
    }

    // Deactivate current active tab
    if (state.activeTabId && state.activeTabId !== tabId) {
      const currentTab = state.tabs.get(state.activeTabId);
      currentTab?.setActive(false);
    }

    // Activate new tab
    const newTab = state.tabs.get(tabId);
    newTab?.setActive(true);

    this._state.update(s => ({
      ...s,
      activeTabId: tabId
    }));

    return true;
  }

  /**
   * Update pane dimensions
   */
  setDimensions(dimensions: Partial<PaneDimensions>): void {
    this._state.update(s => ({
      ...s,
      dimensions: {
        ...s.dimensions,
        ...dimensions
      }
    }));
  }

  /**
   * Toggle pane visibility
   */
  toggleVisibility(): void {
    this._state.update(s => ({
      ...s,
      isVisible: !s.isVisible
    }));
  }

  /**
   * Set pane visibility
   */
  setVisible(visible: boolean): void {
    this._state.update(s => ({
      ...s,
      isVisible: visible
    }));
  }

  /**
   * Toggle collapsed state
   */
  toggleCollapsed(): void {
    this._state.update(s => ({
      ...s,
      isCollapsed: !s.isCollapsed
    }));
  }

  /**
   * Set collapsed state
   */
  setCollapsed(collapsed: boolean): void {
    this._state.update(s => ({
      ...s,
      isCollapsed: collapsed
    }));
  }

  /**
   * Update pane title
   */
  setTitle(title: string): void {
    this._state.update(s => ({
      ...s,
      title
    }));
  }

  /**
   * Reorder tabs
   */
  reorderTabs(tabIds: string[]): void {
    const state = get(this._state);
    
    tabIds.forEach((tabId, index) => {
      const tab = state.tabs.get(tabId);
      if (tab) {
        tab.setOrder(index);
      }
    });
  }

  /**
   * Get tab by ID
   */
  getTab(tabId: string): PaneTab | null {
    const state = get(this._state);
    return state.tabs.get(tabId) || null;
  }

  /**
   * Get all tab IDs in order
   */
  getTabIds(): string[] {
    const tabs = get(this.tabs);
    return tabs.map(tab => tab.getState().id);
  }

  /**
   * Check if pane has any tabs
   */
  hasTabs(): boolean {
    const state = get(this._state);
    return state.tabs.size > 0;
  }

  /**
   * Subscribe to state changes
   */
  subscribe(callback: (state: PaneState) => void) {
    return this._state.subscribe(callback);
  }

  /**
   * Export pane state for serialization
   */
  toJSON(): any {
    const state = get(this._state);
    return {
      id: state.id,
      position: state.position,
      title: state.title,
      activeTabId: state.activeTabId,
      isVisible: state.isVisible,
      isCollapsed: state.isCollapsed,
      isResizable: state.isResizable,
      dimensions: state.dimensions,
      nextTabId: state.nextTabId,
      tabs: Array.from(state.tabs.entries()).map(([id, tab]) => ({
        id,
        data: tab.toJSON()
      }))
    };
  }

  /**
   * Create pane from JSON
   */
  static fromJSON(json: any): Pane {
    const pane = new Pane(
      json.id,
      json.position,
      json.title,
      json.dimensions,
      json.isResizable
    );

    // Restore tabs
    const tabs = new Map<string, PaneTab>();
    for (const { id, data } of json.tabs) {
      tabs.set(id, PaneTab.fromJSON(data));
    }

    pane._state.update(s => ({
      ...s,
      tabs,
      activeTabId: json.activeTabId,
      isVisible: json.isVisible,
      isCollapsed: json.isCollapsed,
      nextTabId: json.nextTabId
    }));

    return pane;
  }
}