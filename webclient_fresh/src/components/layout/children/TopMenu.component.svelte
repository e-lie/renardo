<script lang="ts">
  import { useProjectStore } from '../../../store/project'
  import { useI18nStore } from '../../../store/i18n/I18n.store'
  import FileExplorerModal from '../../shared/FileExplorerModal.component.svelte'

  const { actions: projectActions, getters: projectGetters } = useProjectStore()
  const { currentProject } = projectGetters

  const { getters: i18nGetters } = useI18nStore()
  const { translate } = i18nGetters

  let showFileExplorer = $state(false)

  function handleProjectSelect(path: string) {
    projectActions.openProject(path)
    showFileExplorer = false
  }
</script>

<div class="h-full flex items-center justify-between px-4 bg-surface-200 dark:bg-surface-800">
  <div class="flex items-center gap-2">
    <div class="text-lg font-bold text-surface-900 dark:text-surface-50">
      Renardo
    </div>

    <div class="flex gap-1">
      <button
        class="btn btn-sm variant-ghost"
        onclick={() => showFileExplorer = true}
        title={$translate('selectCodeFolder')}
      >
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="w-4 h-4">
          <path stroke-linecap="round" stroke-linejoin="round" d="M2.25 12.75V12A2.25 2.25 0 014.5 9.75h15A2.25 2.25 0 0121.75 12v.75m-8.69-6.44l-2.12-2.12a1.5 1.5 0 00-1.061-.44H4.5A2.25 2.25 0 002.25 6v12a2.25 2.25 0 002.25 2.25h15A2.25 2.25 0 0021.75 18V9a2.25 2.25 0 00-2.25-2.25h-5.379a1.5 1.5 0 01-1.06-.44z" />
        </svg>
        {#if $currentProject}
          <span class="text-xs">{$currentProject.root_path.split('/').pop()}</span>
        {:else}
          <span class="text-xs">{$translate('selectCodeFolder')}</span>
        {/if}
      </button>
    </div>
  </div>
</div>

<FileExplorerModal
  isOpen={showFileExplorer}
  mode="select-folder"
  initialPath={$currentProject?.root_path || null}
  onclose={() => showFileExplorer = false}
  onselect={handleProjectSelect}
/>
