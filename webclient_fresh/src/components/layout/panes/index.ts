import CodeEditorPane from './CodeEditorPane.component.svelte';
import TextAreaPane from './TextAreaPane.component.svelte';

export const PANE_COMPONENT_REGISTRY = {
  'CodeEditor': CodeEditorPane,
  'TextArea': TextAreaPane,
} as const;

export type PaneComponentType = keyof typeof PANE_COMPONENT_REGISTRY;
