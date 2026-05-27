import { useLayoutStore } from '../store/layout'
import { useEditorStore } from '../store/editor/Editor.store'
import { useI18nStore } from '../store/i18n/I18n.store'
import { useProjectStore } from '../store/project'

const API_URL = 'http://localhost:8000'
const DEBOUNCE_MS = 2000

const PERSISTENCE_KEYS = [
    'editor-settings',
    'layout-config',
    'skeleton-theme',
    'skeleton-theme-last-non-glass',
    'color-scheme-mode',
    'renardo-language',
    'project-path',
    'editor-tabs',
] as const

function collectState(): Record<string, unknown> {
    const state: Record<string, unknown> = {}
    for (const key of PERSISTENCE_KEYS) {
        const raw = localStorage.getItem(key)
        if (raw === null) continue
        try {
            state[key] = JSON.parse(raw)
        } catch {
            state[key] = raw
        }
    }
    return state
}

let saveTimer: ReturnType<typeof setTimeout> | null = null

export function scheduleBackendSave(): void {
    if (saveTimer) clearTimeout(saveTimer)
    saveTimer = setTimeout(async () => {
        try {
            await fetch(`${API_URL}/api/frontend-state`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ state: collectState() }),
            })
        } catch {
            // localStorage reste le fallback si le backend est indisponible
        }
    }, DEBOUNCE_MS)
}

export async function loadFromBackend(): Promise<void> {
    try {
        const response = await fetch(`${API_URL}/api/frontend-state`)
        if (!response.ok) return
        const state: Record<string, unknown> = await response.json()
        if (!state || Object.keys(state).length === 0) return

        // Écrire toutes les clés dans localStorage
        for (const [key, value] of Object.entries(state)) {
            localStorage.setItem(key, typeof value === 'string' ? value : JSON.stringify(value))
        }

        // Appliquer les editor settings au store en mémoire
        if (state['editor-settings'] && typeof state['editor-settings'] === 'object') {
            useEditorStore().actions.updateSettings(state['editor-settings'] as any)
        }

        // Appliquer le layout au store en mémoire
        if (state['layout-config'] && typeof state['layout-config'] === 'object') {
            useLayoutStore().actions.importLayout(state['layout-config'])
        }

        // Appliquer la langue
        if (typeof state['renardo-language'] === 'string') {
            useI18nStore().actions.setLanguage(state['renardo-language'] as any)
        }

        // Restaurer le projet ouvert
        if (typeof state['project-path'] === 'string') {
            useProjectStore().actions.openProject(state['project-path']).catch(() => {
                // Le dossier n'existe peut-être plus, on nettoie
                localStorage.removeItem('project-path')
            })
        }

        // Appliquer le skeleton theme au DOM
        if (typeof state['skeleton-theme'] === 'string') {
            document.documentElement.setAttribute('data-theme', state['skeleton-theme'])
        }

        if (typeof state['color-scheme-mode'] === 'string') {
            const mode = state['color-scheme-mode']
            if (mode === 'auto') {
                const dark = window.matchMedia('(prefers-color-scheme: dark)').matches
                document.documentElement.setAttribute('data-mode', dark ? 'dark' : 'light')
            } else {
                document.documentElement.setAttribute('data-mode', mode)
            }
        }
    } catch {
        // silently fail — localStorage reste actif
    }
}

// Appelle cette fonction après loadFromBackend() pour activer la sauvegarde auto.
// Retourne une fonction de cleanup pour onDestroy.
export function startAutoSave(): () => void {
    const { getters: layoutGetters } = useLayoutStore()
    const { getters: editorGetters } = useEditorStore()
    const { getters: projectGetters } = useProjectStore()

    // Le subscribe Svelte fire immédiatement avec la valeur courante.
    // On ignore ce premier appel synchrone en settant initialized après.
    let initialized = false
    const defer = () => { if (initialized) scheduleBackendSave() }

    const unsubscribers = [
        layoutGetters.paneVisibility.subscribe(defer),
        layoutGetters.paneSetVisibility.subscribe(defer),
        layoutGetters.paneSizes.subscribe(defer),
        layoutGetters.containerSizes.subscribe(defer),
        editorGetters.settings.subscribe(defer),
        projectGetters.currentProject.subscribe(defer),
    ]

    initialized = true
    return () => unsubscribers.forEach(u => u())
}
