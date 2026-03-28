<script lang="ts">
  import { useEditorStore } from '../../../store/editor/Editor.store';
  import { useI18nStore } from '../../../store/i18n/I18n.store';

  const { getters, actions } = useEditorStore();
  const { translate } = useI18nStore().getters;
  const { settings } = getters;

  function handleChange(event: Event) {
    const target = event.target as HTMLInputElement;
    const value = Number(target.value);
    if (value >= 5 && value <= 72) actions.updateSettings({ fontSize: value });
  }
</script>

<div class="space-y-2">
  <label for="font-size-input" class="label">
    <span class="font-semibold">{$translate('fontSize')}</span>
  </label>
  <input
    id="font-size-input"
    type="number"
    class="input variant-form-material w-full"
    min="5"
    max="72"
    value={$settings.fontSize}
    onchange={handleChange}
  />
</div>
