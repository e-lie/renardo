import { writable } from 'svelte/store';

// Default editor settings
const defaultSettings = {
  theme: 'dracula',
  fontSize: 14,
  tabSize: 4,
  showLineNumbers: true,
  lineWrapping: true,
  vimModeEnabled: false
};

// Create the writable store
export const editorSettings = writable(defaultSettings);

// Theme options available
export const themeOptions = [
  { value: 'dracula', label: 'Dracula' },
  { value: 'monokai', label: 'Monokai' },
  { value: 'material', label: 'Material' },
  { value: 'solarized', label: 'Solarized' },
  { value: 'default', label: 'Default' }
];

// Font size options
export const fontSizes = [10, 11, 12, 13, 14, 15, 16, 18, 20, 22, 24];