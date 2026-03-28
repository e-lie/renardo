<script lang="ts">
  import FileExplorerModal from './FileExplorerModal.component.svelte'

  let {
    isOpen = false,
    initialPath = null,
    onclose,
    onsave
  }: {
    isOpen?: boolean
    initialPath?: string | null
    onclose: () => void
    onsave: (filePath: string) => void
  } = $props()

  function handleFileSelect(fullPath: string) {
    onsave(fullPath)
    onclose()
  }
</script>

<FileExplorerModal
  isOpen={isOpen}
  mode="save-file"
  initialPath={initialPath}
  onclose={onclose}
  onselect={handleFileSelect}
/>
