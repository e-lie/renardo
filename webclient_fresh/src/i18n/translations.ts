export type Language = 'en' | 'fr' | 'es' | 'de'

export const translations = {
  en: {
    // Settings
    settings: 'Settings',
    editor: 'Editor',
    layout: 'Layout',
    done: 'Done',
    language: 'Language',

    // Layout Config
    layoutConfiguration: 'Layout Configuration',
    leftColumn: 'Left Column',
    rightColumn: 'Right Column',
    bottomArea: 'Bottom Area',
    show: 'Show',
    hide: 'Hide',
    paneTabManagement: 'Pane Tab Management',

    // Themes
    syntaxTheme: 'Syntax Theme',
    skeletonUITheme: 'Skeleton UI Theme',

    // Layout
    textArea: 'Text Area',
    codeEditor: 'Code Editor',
    consoleOutput: 'ฅ^•ﻌ•^ฅ >> output',
    tutorials: 'Tutorials',
    addComponent: '+ Add Component',
    hidden: 'Hidden',

    // Common
    close: 'Close',
    clear: 'Clear',

    // Panes
    menu: 'Menu',
    notes: 'Notes',
    scratch: 'Scratch',
    workspace: 'Workspace',
    draft: 'Draft'
  },
  fr: {
    // Settings
    settings: 'Paramètres',
    editor: 'Éditeur',
    layout: 'Disposition',
    done: 'Terminé',
    language: 'Langue',

    // Layout Config
    layoutConfiguration: 'Configuration de la disposition',
    leftColumn: 'Colonne gauche',
    rightColumn: 'Colonne droite',
    bottomArea: 'Zone inférieure',
    show: 'Afficher',
    hide: 'Masquer',
    paneTabManagement: 'Gestion des onglets',

    // Themes
    syntaxTheme: 'Thème de syntaxe',
    skeletonUITheme: 'Thème de l\'interface',

    // Layout
    textArea: 'Zone de texte',
    codeEditor: 'Éditeur de code',
    consoleOutput: 'ฅ^•ﻌ•^ฅ >> sortie',
    tutorials: 'Tutoriels',
    addComponent: '+ Ajouter un composant',
    hidden: 'Masqué',

    // Common
    close: 'Fermer',
    clear: 'Effacer',

    // Panes
    menu: 'Menu',
    notes: 'Notes',
    scratch: 'Brouillon',
    workspace: 'Espace de travail',
    draft: 'Ébauche'
  },
  es: {
    // Settings
    settings: 'Configuración',
    editor: 'Editor',
    layout: 'Diseño',
    done: 'Hecho',
    language: 'Idioma',

    // Layout Config
    layoutConfiguration: 'Configuración del diseño',
    leftColumn: 'Columna izquierda',
    rightColumn: 'Columna derecha',
    bottomArea: 'Área inferior',
    show: 'Mostrar',
    hide: 'Ocultar',
    paneTabManagement: 'Gestión de pestañas',

    // Themes
    syntaxTheme: 'Tema de sintaxis',
    skeletonUITheme: 'Tema de interfaz',

    // Layout
    textArea: 'Área de texto',
    codeEditor: 'Editor de código',
    consoleOutput: 'ฅ^•ﻌ•^ฅ >> salida',
    tutorials: 'Tutoriales',
    addComponent: '+ Añadir componente',
    hidden: 'Oculto',

    // Common
    close: 'Cerrar',
    clear: 'Limpiar',

    // Panes
    menu: 'Menú',
    notes: 'Notas',
    scratch: 'Borrador',
    workspace: 'Espacio de trabajo',
    draft: 'Borrador'
  },
  de: {
    // Settings
    settings: 'Einstellungen',
    editor: 'Editor',
    layout: 'Layout',
    done: 'Fertig',
    language: 'Sprache',

    // Layout Config
    layoutConfiguration: 'Layout-Konfiguration',
    leftColumn: 'Linke Spalte',
    rightColumn: 'Rechte Spalte',
    bottomArea: 'Unterer Bereich',
    show: 'Anzeigen',
    hide: 'Ausblenden',
    paneTabManagement: 'Tab-Verwaltung',

    // Themes
    syntaxTheme: 'Syntax-Theme',
    skeletonUITheme: 'UI-Theme',

    // Layout
    textArea: 'Textbereich',
    codeEditor: 'Code-Editor',
    consoleOutput: 'ฅ^•ﻌ•^ฅ >> Ausgabe',
    tutorials: 'Anleitungen',
    addComponent: '+ Komponente hinzufügen',
    hidden: 'Versteckt',

    // Common
    close: 'Schließen',
    clear: 'Löschen',

    // Panes
    menu: 'Menü',
    notes: 'Notizen',
    scratch: 'Entwurf',
    workspace: 'Arbeitsbereich',
    draft: 'Entwurf'
  }
} as const

export type TranslationKey = keyof typeof translations.en
