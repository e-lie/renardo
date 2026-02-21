<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { useI18nStore } from '../../../store/i18n/I18n.store';

  const i18n = useI18nStore();
  const { translate } = i18n.getters;

  const SKELETON_THEMES = [
    'glass',
    'cerberus',
    'catppuccin',
    'concord',
    'crimson',
    'fennec',
    'hamlindigo',
    'legacy',
    'mint',
    'modern',
    'mona',
    'nosh',
    'nouveau',
    'pine',
    'reign',
    'rocket',
    'rose',
    'sahara',
    'seafoam',
    'terminus',
    'vintage',
    'vox',
    'wintry'
  ];

  const COLOR_SCHEME_MODES = ['dark', 'light', 'auto'] as const;
  type ColorSchemeMode = (typeof COLOR_SCHEME_MODES)[number];

  let currentTheme = $state('cerberus');
  let colorSchemeMode = $state<ColorSchemeMode>('dark');
  let mediaQueryListener: ((e: MediaQueryListEvent) => void) | null = null;
  let mediaQuery: MediaQueryList | null = null;

  onMount(() => {
    const savedTheme = localStorage.getItem('skeleton-theme') || 'cerberus';
    currentTheme = savedTheme;
    applyTheme(savedTheme);

    const savedMode = (localStorage.getItem('color-scheme-mode') as ColorSchemeMode) || 'dark';
    colorSchemeMode = savedMode;
    applyColorSchemeMode(savedMode);
  });

  onDestroy(() => {
    if (mediaQuery && mediaQueryListener) {
      mediaQuery.removeEventListener('change', mediaQueryListener);
    }
  });

  function applyTheme(theme: string) {
    document.documentElement.setAttribute('data-theme', theme);
  }

  function applyColorSchemeMode(mode: ColorSchemeMode) {
    // Remove previous media query listener
    if (mediaQuery && mediaQueryListener) {
      mediaQuery.removeEventListener('change', mediaQueryListener);
      mediaQueryListener = null;
      mediaQuery = null;
    }

    if (mode === 'auto') {
      mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
      const applyFromMedia = (dark: boolean) => {
        document.documentElement.setAttribute('data-mode', dark ? 'dark' : 'light');
      };
      applyFromMedia(mediaQuery.matches);
      mediaQueryListener = (e) => applyFromMedia(e.matches);
      mediaQuery.addEventListener('change', mediaQueryListener);
    } else {
      document.documentElement.setAttribute('data-mode', mode);
    }
  }

  function handleThemeChange(event: Event) {
    const target = event.target as HTMLSelectElement;
    const newTheme = target.value;
    currentTheme = newTheme;
    localStorage.setItem('skeleton-theme', newTheme);
    applyTheme(newTheme);
  }

  function handleColorSchemeModeChange(event: Event) {
    const target = event.target as HTMLSelectElement;
    const newMode = target.value as ColorSchemeMode;
    colorSchemeMode = newMode;
    localStorage.setItem('color-scheme-mode', newMode);
    applyColorSchemeMode(newMode);
  }
</script>

<div class="space-y-2">
  <label for="color-scheme-mode-select" class="label">
    <span class="font-semibold">{$translate('colorSchemeMode')}</span>
  </label>
  <select
    id="color-scheme-mode-select"
    class="select variant-form-material w-full"
    value={colorSchemeMode}
    onchange={handleColorSchemeModeChange}
  >
    {#each COLOR_SCHEME_MODES as mode}
      <option value={mode}>{mode.charAt(0).toUpperCase() + mode.slice(1)}</option>
    {/each}
  </select>
</div>

<div class="space-y-2">
  <label for="skeleton-theme-select" class="label">
    <span class="font-semibold">{$translate('skeletonUITheme')}</span>
  </label>
  <select
    id="skeleton-theme-select"
    class="select variant-form-material w-full"
    value={currentTheme}
    onchange={handleThemeChange}
  >
    {#each SKELETON_THEMES as theme}
      <option value={theme}>{theme.charAt(0).toUpperCase() + theme.slice(1)}</option>
    {/each}
  </select>
</div>
