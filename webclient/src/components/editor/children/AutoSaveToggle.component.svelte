<script lang="ts">
  import { useEditorStore } from '../../../store/editor/Editor.store';
  import { useI18nStore } from '../../../store/i18n/I18n.store';

  const { getters, actions } = useEditorStore();
  const { getters: i18nGetters } = useI18nStore();
  const { translate } = i18nGetters;
  const { settings } = getters;

  const autoSave = $derived($settings.autoSave);

  function toggleAutoSave() {
    actions.updateSettings({ autoSave: !autoSave });
  }
</script>

<div class="space-y-2">
  <label class="flex items-center justify-between">
    <span class="text-sm font-medium text-surface-900 dark:text-surface-50">
      {$translate('autoSave')}
    </span>
    <input
      type="checkbox"
      class="toggle"
      checked={autoSave}
      onchange={toggleAutoSave}
    />
  </label>
  <p class="text-xs text-surface-600 dark:text-surface-400">
    {$translate('autoSaveDescription')}
  </p>
</div>
