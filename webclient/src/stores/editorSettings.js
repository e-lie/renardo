import { writable } from 'svelte/store';

// Default editor settings
const defaultSettings = {
  theme: 'dracula',
  fontSize: 14,
  fontFamily: 'fira-code',
  lineHeight: 1.5,
  tabSize: 4,
  showLineNumbers: true,
  lineWrapping: true,
  vimModeEnabled: false
};

// Create the writable store
export const editorSettings = writable(defaultSettings);

// Theme options available (matching EditorSettings.svelte)
export const themeOptions = [
  { value: 'monokai', label: 'Monokai' },
  { value: 'dracula', label: 'Dracula' },
  { value: 'material', label: 'Material' },
  { value: 'nord', label: 'Nord' },
  { value: 'solarized-dark', label: 'Solarized Dark' },
  { value: 'solarized-light', label: 'Solarized Light' },
  { value: 'darcula', label: 'Darcula' },
  { value: 'eclipse', label: 'Eclipse' },
  { value: 'default', label: 'Default' }
];

// Font size options
export const fontSizes = [10, 11, 12, 13, 14, 15, 16, 18, 20, 22, 24];

// Line height options
export const lineHeights = [
  { value: 1.0, label: '1.0 (Compact)' },
  { value: 1.2, label: '1.2 (Tight)' },
  { value: 1.4, label: '1.4 (Normal)' },
  { value: 1.5, label: '1.5 (Default)' },
  { value: 1.6, label: '1.6 (Comfortable)' },
  { value: 1.8, label: '1.8 (Spacious)' },
  { value: 2.0, label: '2.0 (Double)' }
];

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