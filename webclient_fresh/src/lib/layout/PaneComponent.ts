import { writable, derived, get, type Writable, type Readable } from 'svelte/store';

export interface PaneComponentState {
  id: string;
  type: string;
  title: string;
  data: Record<string, any>;
  isActive: boolean;
  lastUpdated: number;
}

export interface PaneComponentConfig {
  id?: string;
  type: string;
  title: string;
  initialData?: Record<string, any>;
}

/**
 * PaneComponent represents a Svelte component that can be displayed in panes
 * All instances of the same component type share synchronized state
 */
export class PaneComponent {
  private _state: Writable<PaneComponentState>;

  // Derived stores for easy access
  public readonly id: Readable<string>;
  public readonly type: Readable<string>;
  public readonly title: Readable<string>;
  public readonly data: Readable<Record<string, any>>;
  public readonly isActive: Readable<boolean>;
  public readonly lastUpdated: Readable<number>;

  // Global state store for synchronized components
  private static _globalStates: Map<string, Writable<Record<string, any>>> = new Map();

  constructor(config: PaneComponentConfig) {
    const componentId = config.id || `${config.type}-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;

    this._state = writable({
      id: componentId,
      type: config.type,
      title: config.title,
      data: config.initialData || {},
      isActive: false,
      lastUpdated: Date.now()
    });

    // Initialize global state for this component type if it doesn't exist
    if (!PaneComponent._globalStates.has(config.type)) {
      PaneComponent._globalStates.set(config.type, writable(config.initialData || {}));
    }

    // Derived stores
    this.id = derived(this._state, $state => $state.id);
    this.type = derived(this._state, $state => $state.type);
    this.title = derived(this._state, $state => $state.title);
    this.data = derived(this._state, $state => $state.data);
    this.isActive = derived(this._state, $state => $state.isActive);
    this.lastUpdated = derived(this._state, $state => $state.lastUpdated);

    // Subscribe to global state changes for this component type
    this.subscribeToGlobalState();
  }

  /**
   * Subscribe to global state changes for synchronization
   */
  private subscribeToGlobalState(): void {
    const globalState = PaneComponent._globalStates.get(this.getState().type);
    if (globalState) {
      globalState.subscribe((newData) => {
        this._state.update(state => ({
          ...state,
          data: newData,
          lastUpdated: Date.now()
        }));
      });
    }
  }

  /**
   * Get the current state synchronously
   */
  getState(): PaneComponentState {
    return get(this._state);
  }

  /**
   * Update component data and sync with all instances of the same type
   */
  updateData(data: Partial<Record<string, any>>): void {
    const currentState = this.getState();
    const globalState = PaneComponent._globalStates.get(currentState.type);

    if (globalState) {
      const currentGlobalData = get(globalState);
      const newData = { ...currentGlobalData, ...data };

      // Update global state (this will trigger updates for all instances)
      globalState.set(newData);
    }
  }

  /**
   * Set a specific data property
   */
  setDataProperty(key: string, value: any): void {
    this.updateData({ [key]: value });
  }

  /**
   * Get a specific data property
   */
  getDataProperty(key: string): any {
    const state = this.getState();
    return state.data[key];
  }

  /**
   * Set active state
   */
  setActive(active: boolean): void {
    this._state.update(state => ({
      ...state,
      isActive: active
    }));
  }

  /**
   * Update component title
   */
  setTitle(title: string): void {
    this._state.update(state => ({
      ...state,
      title
    }));
  }

  /**
   * Get global state store for this component type
   */
  getGlobalState(): Readable<Record<string, any>> {
    const globalState = PaneComponent._globalStates.get(this.getState().type);
    if (!globalState) {
      throw new Error(`No global state found for component type: ${this.getState().type}`);
    }
    return globalState;
  }

  /**
   * Reset component data to initial state
   */
  reset(initialData: Record<string, any> = {}): void {
    const globalState = PaneComponent._globalStates.get(this.getState().type);
    if (globalState) {
      globalState.set(initialData);
    }
  }

  /**
   * Subscribe to state changes
   */
  subscribe(callback: (state: PaneComponentState) => void) {
    return this._state.subscribe(callback);
  }

  /**
   * Export component state for serialization
   */
  toJSON(): any {
    const state = this.getState();
    return {
      id: state.id,
      type: state.type,
      title: state.title,
      data: state.data,
      isActive: state.isActive,
      lastUpdated: state.lastUpdated
    };
  }

  /**
   * Create component from JSON
   */
  static fromJSON(json: any): PaneComponent {
    const component = new PaneComponent({
      id: json.id,
      type: json.type,
      title: json.title,
      initialData: json.data
    });

    component._state.update(state => ({
      ...state,
      isActive: json.isActive,
      lastUpdated: json.lastUpdated
    }));

    return component;
  }

  /**
   * Get all global states (for debugging or management)
   */
  static getGlobalStates(): Map<string, Readable<Record<string, any>>> {
    return new Map(PaneComponent._globalStates);
  }

  /**
   * Clear global state for a specific component type
   */
  static clearGlobalState(type: string): void {
    PaneComponent._globalStates.delete(type);
  }

  /**
   * Clear all global states
   */
  static clearAllGlobalStates(): void {
    PaneComponent._globalStates.clear();
  }
}
