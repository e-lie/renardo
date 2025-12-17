export type PaneComponentType = 'CodeEditor' | 'TextArea';

export interface ComponentRegistryEntry {
  component: any;
  defaultProps?: Record<string, any>;
}
