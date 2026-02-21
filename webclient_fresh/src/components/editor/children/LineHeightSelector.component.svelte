<script lang="ts">
  import { useEditorStore } from '../../../store/editor/Editor.store';
  import { useI18nStore } from '../../../store/i18n/I18n.store';

  const { getters, actions } = useEditorStore();
  const { translate } = useI18nStore().getters;
  const { settings } = getters;

  const lineHeights = [1.0, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 2.0];

  function handleChange(event: Event) {
    const target = event.target as HTMLSelectElement;
    actions.updateSettings({ lineHeight: Number(target.value) });
  }
</script>

<div class="space-y-2">
  <label for="line-height-select" class="label">
    <span class="font-semibold">{$translate('lineHeight')}</span>
  </label>
  <select
    id="line-height-select"
    class="select variant-form-material w-full"
    value={$settings.lineHeight}
    onchange={handleChange}
  >
    {#each lineHeights as lh}
      <option value={lh}>{lh}</option>
    {/each}
  </select>
</div>
