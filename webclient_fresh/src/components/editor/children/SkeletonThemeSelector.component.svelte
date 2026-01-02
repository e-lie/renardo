<script lang="ts">
  import { onMount } from 'svelte';
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

  let currentTheme = $state('cerberus');

  onMount(() => {
    const savedTheme = localStorage.getItem('skeleton-theme') || 'cerberus';
    currentTheme = savedTheme;
    applyTheme(savedTheme);
  });

  function applyTheme(theme: string) {
    document.documentElement.setAttribute('data-theme', theme);
  }

  function handleThemeChange(event: Event) {
    const target = event.target as HTMLSelectElement;
    const newTheme = target.value;
    currentTheme = newTheme;
    localStorage.setItem('skeleton-theme', newTheme);
    applyTheme(newTheme);
  }
</script>

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
