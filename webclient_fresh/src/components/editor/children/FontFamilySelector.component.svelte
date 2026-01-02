<script lang="ts">
  import { useEditorStore } from '../../../store/editor/Editor.store';
  import { useI18nStore } from '../../../store/i18n/I18n.store';

  const { getters, actions } = useEditorStore();
  const { getters: i18nGetters } = useI18nStore();
  const { translate } = i18nGetters;
  const { settings } = getters;

  const fontFamilies = [
    { name: 'Fira Code', value: 'Fira Code' },
    { name: 'JetBrains Mono', value: 'JetBrains Mono' },
    { name: 'Source Code Pro', value: 'Source Code Pro' },
    { name: 'Monaco', value: 'Monaco' },
    { name: 'Consolas', value: 'Consolas' },
    { name: 'Menlo', value: 'Menlo' },
    { name: 'Courier New', value: 'Courier New' },
  ];

  function handleChange(event: Event) {
    const target = event.target as HTMLSelectElement;
    actions.updateSettings({ fontFamily: target.value });
  }
</script>

<div class="space-y-2">
  <label class="flex flex-col gap-2">
    <span class="text-sm font-medium text-surface-900 dark:text-surface-50">
      {$translate('fontFamily')}
    </span>
    <select
      class="select variant-filled-surface"
      value={$settings.fontFamily}
      onchange={handleChange}
    >
      {#each fontFamilies as font}
        <option value={font.value}>{font.name}</option>
      {/each}
    </select>
  </label>
  <p class="text-xs text-surface-600 dark:text-surface-400">
    {$translate('fontFamilyDescription')}
  </p>
</div>
