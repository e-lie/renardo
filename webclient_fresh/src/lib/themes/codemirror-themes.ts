import { EditorView } from '@codemirror/view'
import type { Extension } from '@codemirror/state'
import { HighlightStyle, syntaxHighlighting } from '@codemirror/language'
import { tags as t } from '@lezer/highlight'

// Dracula Theme
export const draculaTheme = EditorView.theme(
  {
    '&': {
      backgroundColor: '#282a36',
      color: '#f8f8f2',
    },
    '.cm-content': {
      caretColor: '#f8f8f0',
    },
    '.cm-cursor, .cm-dropCursor': {
      borderLeftColor: '#f8f8f0',
    },
    '&.cm-focused .cm-selectionBackground, .cm-selectionBackground, .cm-content ::selection': {
      backgroundColor: 'rgba(255, 255, 255, 0.10)',
    },
    '.cm-activeLine': {
      backgroundColor: 'rgba(255, 255, 255, 0.1)',
    },
    '.cm-gutters': {
      backgroundColor: '#282a36',
      color: '#6D8A88',
      border: 'none',
    },
  },
  { dark: true }
)

const draculaHighlightStyle = HighlightStyle.define([
  { tag: t.comment, color: '#6272a4' },
  { tag: [t.string, t.special(t.string)], color: '#f1fa8c' },
  { tag: t.number, color: '#bd93f9' },
  { tag: t.variableName, color: '#50fa7b' },
  { tag: t.definition(t.variableName), color: '#50fa7b' },
  { tag: t.operator, color: '#ff79c6' },
  { tag: t.keyword, color: '#ff79c6' },
  { tag: t.atom, color: '#bd93f9' },
  { tag: t.meta, color: '#f8f8f2' },
  { tag: t.tagName, color: '#ff79c6' },
  { tag: t.attributeName, color: '#50fa7b' },
  { tag: t.propertyName, color: '#66d9ef' },
  { tag: t.function(t.variableName), color: '#50fa7b' },
  { tag: t.typeName, color: '#ffb86c' },
])

export const dracula: Extension = [draculaTheme, syntaxHighlighting(draculaHighlightStyle)]

// Monokai Theme
export const monokaiTheme = EditorView.theme(
  {
    '&': {
      backgroundColor: '#272822',
      color: '#f8f8f2',
    },
    '.cm-content': {
      caretColor: '#f8f8f0',
    },
    '.cm-cursor, .cm-dropCursor': {
      borderLeftColor: '#f8f8f0',
    },
    '&.cm-focused .cm-selectionBackground, .cm-selectionBackground, .cm-content ::selection': {
      backgroundColor: 'rgba(73, 72, 62, .99)',
    },
    '.cm-activeLine': {
      backgroundColor: '#373831',
    },
    '.cm-gutters': {
      backgroundColor: '#272822',
      color: '#d0d0d0',
      border: 'none',
    },
  },
  { dark: true }
)

const monokaiHighlightStyle = HighlightStyle.define([
  { tag: t.comment, color: '#75715e' },
  { tag: [t.string, t.special(t.string)], color: '#e6db74' },
  { tag: t.number, color: '#ae81ff' },
  { tag: t.atom, color: '#ae81ff' },
  { tag: t.variableName, color: '#f8f8f2' },
  { tag: t.definition(t.variableName), color: '#fd971f' },
  { tag: t.operator, color: '#f8f8f2' },
  { tag: t.keyword, color: '#f92672' },
  { tag: t.propertyName, color: '#a6e22e' },
  { tag: t.attributeName, color: '#a6e22e' },
  { tag: t.function(t.variableName), color: '#66d9ef' },
  { tag: t.typeName, color: '#66d9ef' },
  { tag: t.tagName, color: '#f92672' },
])

export const monokai: Extension = [monokaiTheme, syntaxHighlighting(monokaiHighlightStyle)]

// Nord Theme
export const nordTheme = EditorView.theme(
  {
    '&': {
      backgroundColor: '#2e3440',
      color: '#d8dee9',
    },
    '.cm-content': {
      caretColor: '#f8f8f0',
    },
    '.cm-cursor, .cm-dropCursor': {
      borderLeftColor: '#f8f8f0',
    },
    '&.cm-focused .cm-selectionBackground, .cm-selectionBackground, .cm-content ::selection': {
      backgroundColor: '#434c5e',
    },
    '.cm-activeLine': {
      backgroundColor: '#3b4252',
    },
    '.cm-gutters': {
      backgroundColor: '#2e3440',
      color: '#4c566a',
      border: 'none',
    },
  },
  { dark: true }
)

const nordHighlightStyle = HighlightStyle.define([
  { tag: t.comment, color: '#4c566a' },
  { tag: [t.string, t.special(t.string)], color: '#A3BE8C' },
  { tag: t.number, color: '#b48ead' },
  { tag: t.atom, color: '#b48ead' },
  { tag: t.variableName, color: '#d8dee9' },
  { tag: t.definition(t.variableName), color: '#8FBCBB' },
  { tag: t.keyword, color: '#81A1C1' },
  { tag: t.function(t.variableName), color: '#81A1C1' },
  { tag: t.propertyName, color: '#8FBCBB' },
  { tag: t.attributeName, color: '#8FBCBB' },
  { tag: t.tagName, color: '#bf616a' },
  { tag: t.typeName, color: '#d8dee9' },
])

export const nord: Extension = [nordTheme, syntaxHighlighting(nordHighlightStyle)]

// Material Theme
export const materialTheme = EditorView.theme(
  {
    '&': {
      backgroundColor: '#263238',
      color: '#eeffff',
    },
    '.cm-content': {
      caretColor: '#ffcc00',
    },
    '.cm-cursor, .cm-dropCursor': {
      borderLeftColor: '#ffcc00',
    },
    '&.cm-focused .cm-selectionBackground, .cm-selectionBackground, .cm-content ::selection': {
      backgroundColor: '#546e7a',
    },
    '.cm-activeLine': {
      backgroundColor: '#37474f',
    },
    '.cm-gutters': {
      backgroundColor: '#263238',
      color: '#546e7a',
      border: 'none',
    },
  },
  { dark: true }
)

const materialHighlightStyle = HighlightStyle.define([
  { tag: t.comment, color: '#546e7a', fontStyle: 'italic' },
  { tag: [t.string, t.special(t.string)], color: '#c3e88d' },
  { tag: t.number, color: '#f78c6c' },
  { tag: t.atom, color: '#f78c6c' },
  { tag: t.variableName, color: '#eeffff' },
  { tag: t.definition(t.variableName), color: '#82aaff' },
  { tag: t.keyword, color: '#c792ea' },
  { tag: t.operator, color: '#89ddff' },
  { tag: t.propertyName, color: '#82aaff' },
  { tag: t.function(t.variableName), color: '#82aaff' },
  { tag: t.typeName, color: '#ffcb6b' },
  { tag: t.tagName, color: '#f07178' },
])

export const material: Extension = [materialTheme, syntaxHighlighting(materialHighlightStyle)]

// Solarized Dark Theme
export const solarizedDarkTheme = EditorView.theme(
  {
    '&': {
      backgroundColor: '#002b36',
      color: '#839496',
    },
    '.cm-content': {
      caretColor: '#839496',
    },
    '.cm-cursor, .cm-dropCursor': {
      borderLeftColor: '#839496',
    },
    '&.cm-focused .cm-selectionBackground, .cm-selectionBackground, .cm-content ::selection': {
      backgroundColor: '#073642',
    },
    '.cm-activeLine': {
      backgroundColor: '#073642',
    },
    '.cm-gutters': {
      backgroundColor: '#002b36',
      color: '#586e75',
      border: 'none',
    },
  },
  { dark: true }
)

const solarizedDarkHighlightStyle = HighlightStyle.define([
  { tag: t.comment, color: '#586e75', fontStyle: 'italic' },
  { tag: [t.string, t.special(t.string)], color: '#2aa198' },
  { tag: t.number, color: '#d33682' },
  { tag: t.atom, color: '#d33682' },
  { tag: t.variableName, color: '#839496' },
  { tag: t.definition(t.variableName), color: '#268bd2' },
  { tag: t.keyword, color: '#859900' },
  { tag: t.operator, color: '#859900' },
  { tag: t.propertyName, color: '#268bd2' },
  { tag: t.function(t.variableName), color: '#268bd2' },
  { tag: t.typeName, color: '#b58900' },
  { tag: t.tagName, color: '#268bd2' },
])

export const solarizedDark: Extension = [
  solarizedDarkTheme,
  syntaxHighlighting(solarizedDarkHighlightStyle),
]

// Solarized Light Theme
export const solarizedLightTheme = EditorView.theme(
  {
    '&': {
      backgroundColor: '#fdf6e3',
      color: '#657b83',
    },
    '.cm-content': {
      caretColor: '#657b83',
    },
    '.cm-cursor, .cm-dropCursor': {
      borderLeftColor: '#657b83',
    },
    '&.cm-focused .cm-selectionBackground, .cm-selectionBackground, .cm-content ::selection': {
      backgroundColor: '#eee8d5',
    },
    '.cm-activeLine': {
      backgroundColor: '#eee8d5',
    },
    '.cm-gutters': {
      backgroundColor: '#fdf6e3',
      color: '#93a1a1',
      border: 'none',
    },
  },
  { dark: false }
)

const solarizedLightHighlightStyle = HighlightStyle.define([
  { tag: t.comment, color: '#93a1a1', fontStyle: 'italic' },
  { tag: [t.string, t.special(t.string)], color: '#2aa198' },
  { tag: t.number, color: '#d33682' },
  { tag: t.atom, color: '#d33682' },
  { tag: t.variableName, color: '#657b83' },
  { tag: t.definition(t.variableName), color: '#268bd2' },
  { tag: t.keyword, color: '#859900' },
  { tag: t.operator, color: '#859900' },
  { tag: t.propertyName, color: '#268bd2' },
  { tag: t.function(t.variableName), color: '#268bd2' },
  { tag: t.typeName, color: '#b58900' },
  { tag: t.tagName, color: '#268bd2' },
])

export const solarizedLight: Extension = [
  solarizedLightTheme,
  syntaxHighlighting(solarizedLightHighlightStyle),
]

// Darcula Theme (JetBrains IntelliJ IDEA dark theme)
export const darculaTheme = EditorView.theme(
  {
    '&': {
      backgroundColor: '#2b2b2b',
      color: '#a9b7c6',
    },
    '.cm-content': {
      caretColor: '#bbbbbb',
    },
    '.cm-cursor, .cm-dropCursor': {
      borderLeftColor: '#bbbbbb',
    },
    '&.cm-focused .cm-selectionBackground, .cm-selectionBackground, .cm-content ::selection': {
      backgroundColor: '#214283',
    },
    '.cm-activeLine': {
      backgroundColor: '#323232',
    },
    '.cm-gutters': {
      backgroundColor: '#313335',
      color: '#606366',
      border: 'none',
    },
  },
  { dark: true }
)

const darculaHighlightStyle = HighlightStyle.define([
  { tag: t.comment, color: '#808080', fontStyle: 'italic' },
  { tag: [t.string, t.special(t.string)], color: '#6a8759' },
  { tag: t.number, color: '#6897bb' },
  { tag: t.atom, color: '#cc7832' },
  { tag: t.variableName, color: '#a9b7c6' },
  { tag: t.definition(t.variableName), color: '#ffc66d' },
  { tag: t.keyword, color: '#cc7832' },
  { tag: t.operator, color: '#a9b7c6' },
  { tag: t.propertyName, color: '#9876aa' },
  { tag: t.function(t.variableName), color: '#ffc66d' },
  { tag: t.typeName, color: '#b5b6e3' },
  { tag: t.tagName, color: '#e8bf6a' },
])

export const darcula: Extension = [darculaTheme, syntaxHighlighting(darculaHighlightStyle)]

// Eclipse Theme (light)
export const eclipseTheme = EditorView.theme(
  {
    '&': {
      backgroundColor: '#ffffff',
      color: '#000000',
    },
    '.cm-content': {
      caretColor: '#000000',
    },
    '.cm-cursor, .cm-dropCursor': {
      borderLeftColor: '#000000',
    },
    '&.cm-focused .cm-selectionBackground, .cm-selectionBackground, .cm-content ::selection': {
      backgroundColor: '#d7d4f0',
    },
    '.cm-activeLine': {
      backgroundColor: '#e8f2ff',
    },
    '.cm-gutters': {
      backgroundColor: '#f7f7f7',
      color: '#787878',
      border: 'none',
    },
  },
  { dark: false }
)

const eclipseHighlightStyle = HighlightStyle.define([
  { tag: t.comment, color: '#3f7f5f', fontStyle: 'italic' },
  { tag: [t.string, t.special(t.string)], color: '#2a00ff' },
  { tag: t.number, color: '#0000ff' },
  { tag: t.atom, color: '#7f0055', fontWeight: 'bold' },
  { tag: t.variableName, color: '#000000' },
  { tag: t.definition(t.variableName), color: '#0000ff' },
  { tag: t.keyword, color: '#7f0055', fontWeight: 'bold' },
  { tag: t.operator, color: '#000000' },
  { tag: t.propertyName, color: '#0000c0' },
  { tag: t.function(t.variableName), color: '#000000' },
  { tag: t.typeName, color: '#000000' },
  { tag: t.tagName, color: '#3f7f7f' },
])

export const eclipse: Extension = [eclipseTheme, syntaxHighlighting(eclipseHighlightStyle)]

// Theme registry
export const themes: Record<string, Extension> = {
  dracula,
  monokai,
  nord,
  material,
  'solarized-dark': solarizedDark,
  'solarized-light': solarizedLight,
  darcula,
  eclipse,
}

export function getTheme(themeName: string): Extension {
  return themes[themeName] || dracula
}
