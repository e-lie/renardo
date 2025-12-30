<script lang="ts">
  import { onMount } from 'svelte';
  import { useAppStore } from '../../../store/root';
  import { useEditorStore } from '../../../store/editor';
  import ElText from '../../primitives/text/ElText.svelte';
  import ElTutorialList from '../../primitives/lists/ElTutorialList.svelte';
  import type { MusicExampleFileInterface } from '../../../models/music-example';

  let {
    componentId,
    title = 'Music Examples',
  }: {
    componentId: string;
    title?: string;
  } = $props();

  const { musicExampleStore } = useAppStore();
  const { loading, musicExampleFiles, error } = musicExampleStore.getters;
  const { loadMusicExampleFiles, selectMusicExampleFile } = musicExampleStore.actions;

  const editorStore = useEditorStore();

  onMount(async () => {
    await loadMusicExampleFiles();
  });

  async function handleLoadFile(filename: string) {
    const file = $musicExampleFiles.find((f: MusicExampleFileInterface) => f.name === filename);
    if (file) {
      await selectMusicExampleFile(file, editorStore);
    }
  }
</script>

<div class="p-4 h-full overflow-auto">
  <ElText tag="h2" text={title || 'Music Examples'} addCss="text-xl font-bold mb-4" />

  {#if $error}
    <div class="alert alert-error mb-4">
      <ElText tag="span" text={$error} addCss="text-white" />
    </div>
  {/if}

  {#if $loading}
    <div class="flex justify-center py-8">
      <span class="loading loading-spinner loading-lg"></span>
    </div>
  {:else}
    {#if $musicExampleFiles.length > 0}
      <div class="mt-4">
        <ElTutorialList
          files={$musicExampleFiles.map((f: MusicExampleFileInterface) => f.name)}
          onloadfile={handleLoadFile}
        />
      </div>
    {:else}
      <ElText
        tag="p"
        text="No music examples available."
        addCss="text-gray-500"
      />
    {/if}
  {/if}
</div>
