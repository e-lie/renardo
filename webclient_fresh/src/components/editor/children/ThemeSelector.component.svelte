<script lang="ts">
  import { AVAILABLE_THEMES } from '../../../models/editor';
  import { useEditorStore } from '../../../store/editor/Editor.store';
  import { logger } from '../../../services/logger.service';

  const { actions, getters } = useEditorStore();
  const { settings } = getters;

  function handleThemeChange(event: Event) {
    const target = event.target as HTMLSelectElement;
    const newTheme = target.value as any;
    logger.info('ThemeSelector', 'Theme changed', { newTheme });
    actions.updateSettings({ theme: newTheme });
    logger.info('ThemeSelector', 'Settings updated, current theme:', { theme: $settings.theme });
  }
</script>

<div class="form-control">
  <div class="label">
    <span class="label-text font-medium">Syntax Theme</span>
  </div>
  <select
    class="select select-bordered select-sm w-full"
    value={$settings.theme}
    onchange={handleThemeChange}
  >
    {#each AVAILABLE_THEMES as theme}
      <option value={theme.value}>{theme.name}</option>
    {/each}
  </select>
</div>
