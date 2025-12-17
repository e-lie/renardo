import { writable, type Writable } from 'svelte/store';
import { PaneComponent } from './PaneComponent';

export interface TabConfig {
  id: string;
  title: string;
  componentType: string;
  componentId: string;
  closable: boolean;
  active: boolean;
}

export class PaneTabManager {
  private _tabs: Writable<TabConfig[]>;
  private _activeTabId: Writable<string | null>;
  private _components: Map<string, PaneComponent> = new Map();

  constructor(initialTabs: TabConfig[] = []) {
    this._tabs = writable(initialTabs);
    this._activeTabId = writable(initialTabs.find(tab => tab.active)?.id || initialTabs[0]?.id || null);

    // Ensure only one tab is active
    this.validateActiveTab(initialTabs);
  }

  // Getters for reactive stores
  get tabs() {
    return this._tabs;
  }

  get activeTabId() {
    return this._activeTabId;
  }

  // Validate that only one tab is active
  private validateActiveTab(tabs: TabConfig[]) {
    const activeTabs = tabs.filter(tab => tab.active);
    if (activeTabs.length !== 1 && tabs.length > 0) {
      // Fix: make first tab active, others inactive
      tabs.forEach((tab, index) => {
        tab.active = index === 0;
      });
    }
  }

  // Add a new tab
  addTab(config: Omit<TabConfig, 'id' | 'active'>): string {
    const tabId = `tab-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    const newTab: TabConfig = {
      ...config,
      id: tabId,
      active: false // Will be set active if it's the first tab
    };

    this._tabs.update(tabs => {
      // If this is the first tab, make it active
      if (tabs.length === 0) {
        newTab.active = true;
        this._activeTabId.set(tabId);
      }

      return [...tabs, newTab];
    });

    return tabId;
  }

  // Remove a tab
  removeTab(tabId: string): void {
    let wasActive = false;
    let newActiveId: string | null = null;

    this._tabs.update(tabs => {
      const tabIndex = tabs.findIndex(tab => tab.id === tabId);
      if (tabIndex === -1) return tabs;

      const removedTab = tabs[tabIndex];
      wasActive = removedTab.active;

      const newTabs = tabs.filter(tab => tab.id !== tabId);

      // If we removed the active tab, select a new active tab
      if (wasActive && newTabs.length > 0) {
        // Try to activate the tab at the same index, or the last tab if index is out of bounds
        const newActiveIndex = Math.min(tabIndex, newTabs.length - 1);
        newTabs[newActiveIndex].active = true;
        newActiveId = newTabs[newActiveIndex].id;
      }

      return newTabs;
    });

    // Clean up component
    const component = this._components.get(tabId);
    if (component) {
      component.setActive(false);
      this._components.delete(tabId);
    }

    // Update active tab
    if (wasActive) {
      this._activeTabId.set(newActiveId);
    }
  }

  // Switch to a tab
  switchToTab(tabId: string): void {
    this._tabs.update(tabs => {
      const updatedTabs = tabs.map(tab => ({
        ...tab,
        active: tab.id === tabId
      }));

      // Verify the tab exists
      if (updatedTabs.find(tab => tab.id === tabId)) {
        this._activeTabId.set(tabId);
      }

      return updatedTabs;
    });
  }

  // Get the currently active tab
  getActiveTab(): TabConfig | null {
    let activeTab: TabConfig | null = null;
    this._tabs.subscribe(tabs => {
      activeTab = tabs.find(tab => tab.active) || null;
    })();
    return activeTab;
  }

  // Get component for a tab
  getComponent(tabId: string): PaneComponent | null {
    return this._components.get(tabId) || null;
  }

  // Register a component for a tab
  registerComponent(tabId: string, component: PaneComponent): void {
    this._components.set(tabId, component);
  }

  // Update tab title
  updateTabTitle(tabId: string, title: string): void {
    this._tabs.update(tabs =>
      tabs.map(tab =>
        tab.id === tabId ? { ...tab, title } : tab
      )
    );
  }

  // Get all tabs
  getAllTabs(): TabConfig[] {
    let allTabs: TabConfig[] = [];
    this._tabs.subscribe(tabs => {
      allTabs = [...tabs];
    })();
    return allTabs;
  }

  // Check if tab exists
  hasTab(tabId: string): boolean {
    return this.getAllTabs().some(tab => tab.id === tabId);
  }

  // Get tab count
  getTabCount(): number {
    return this.getAllTabs().length;
  }

  // Reorder tabs
  reorderTabs(fromIndex: number, toIndex: number): void {
    this._tabs.update(tabs => {
      const newTabs = [...tabs];
      const [movedTab] = newTabs.splice(fromIndex, 1);
      newTabs.splice(toIndex, 0, movedTab);
      return newTabs;
    });
  }

  // Destroy all components and cleanup
  destroy(): void {
    this._components.forEach(component => {
      component.setActive(false);
    });
    this._components.clear();
    this._tabs.set([]);
    this._activeTabId.set(null);
  }
}
