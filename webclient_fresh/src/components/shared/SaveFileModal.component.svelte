<script lang="ts">
  import FileExplorerModal from './FileExplorerModal.component.svelte'

  let {
    isOpen = false,
    onclose,
    onsave
  }: {
    isOpen?: boolean
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
  onclose={onclose}
  onselect={handleFileSelect}
/>
