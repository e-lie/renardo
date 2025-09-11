import { writable } from 'svelte/store';

// Default editor settings
const defaultSettings = {
  theme: 'dracula',
  fontSize: 14,
  fontFamily: 'fira-code',
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

// Font family options
export const fontFamilies = [
  { name: "Fira Code", value: "fira-code" },
  { name: "Source Code Pro", value: "source-code-pro" },
  { name: "JetBrains Mono", value: "jetbrains-mono" },
  { name: "JGS", value: "jgs" },
  { name: "JGS5", value: "jgs5" },
  { name: "JGS7", value: "jgs7" },
  { name: "JGS9", value: "jgs9" },
  { name: "Monaco", value: "monaco" },
  { name: "Consolas", value: "consolas" },
  { name: "Menlo", value: "menlo" },
  { name: "SF Mono", value: "sf-mono" }
];