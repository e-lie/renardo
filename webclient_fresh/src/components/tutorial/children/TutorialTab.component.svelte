<script lang="ts">
  import { onMount } from 'svelte'
  import { useAppStore } from '../../../store/root'
  import ElText from '../../primitives/text/ElText.svelte'
  import ElButton from '../../primitives/buttons/ElButton.svelte'
  import ElLanguageSelector from '../../primitives/selects/ElLanguageSelector.svelte'
  import ElTutorialList from '../../primitives/lists/ElTutorialList.svelte'
  import type { TutorialFileInterface } from '../../../models/tutorial'

  let {
    componentId,
    title = 'Tutorials'
  }: {
    componentId: string
    title?: string
  } = $props()

  const { tutorialStore } = useAppStore()
  const { loading, selectedLanguage, tutorialFiles, error, availableLanguages } = tutorialStore.getters
  const { loadTutorialFiles, selectLanguage, selectTutorialFile } = tutorialStore.actions

    onMount(async () => {
    console.log('TutorialTab mounted')
    console.log('loadTutorialFiles function:', typeof loadTutorialFiles)
    console.log('Available languages getter:', $availableLanguages)
    
    // Test direct API call first
    try {
      console.log('Testing direct API call...')
      const directResponse = await fetch('http://localhost:8000/api/tutorial/files')
      const directData = await directResponse.json()
      console.log('Direct API response success:', directData.success)
      console.log('Direct API languages count:', Object.keys(directData.languages || {}).length)
    } catch (error) {
      console.error('Direct API call failed:', error)
    }
    
    // Then test via store
    try {
      await loadTutorialFiles()
      console.log('Store load completed')
      console.log('Store available languages after load:', $availableLanguages)
    } catch (error) {
      console.error('Store load failed:', error)
    }
  })

  function handleLanguageChange(language: string) {
    selectLanguage(language)
  }

  async function handleLoadFile(filename: string) {
    const file = $tutorialFiles.find((f: TutorialFileInterface) => f.name === filename)
    if (file) {
      await selectTutorialFile(file)
    }
  }
</script>

<div class="p-4 h-full overflow-auto">
  <ElText tag="h2" text={title || "Tutorials"} addCss="text-xl font-bold mb-4" />
  
  <!-- Debug info -->
  <div class="mb-4 p-2 bg-yellow-100 dark:bg-yellow-900 rounded">
    <ElText tag="p" text="Debug Info" addCss="font-bold mb-2" />
    <ElText tag="p" text={`Loading: ${$loading}`} addCss="text-sm" />
    <ElText tag="p" text={`Error: ${$error || 'None'}`} addCss="text-sm" />
    <ElText tag="p" text={`Available languages: ${$availableLanguages.length}`} addCss="text-sm" />
    <ElText tag="p" text={`Selected language: ${$selectedLanguage || 'None'}`} addCss="text-sm" />
    <ElText tag="p" text={`Tutorial files: ${$tutorialFiles.length}`} addCss="text-sm" />
  </div>

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
    {#if $availableLanguages.length > 1}
      <ElLanguageSelector
        languages={$availableLanguages}
        selectedLanguage={$selectedLanguage || ''}
        onchange={handleLanguageChange}
      />
    {/if}

    {#if $tutorialFiles.length > 0}
      <div class="mt-4">
        <ElText tag="h3" text="Available Tutorials" addCss="text-lg font-semibold mb-2" />
        <ElTutorialList
          files={$tutorialFiles.map((f: TutorialFileInterface) => f.name)}
          onloadfile={handleLoadFile}
        />
      </div>
    {:else if !$selectedLanguage}
      <ElText tag="p" text="No tutorials available. Please select a language." addCss="text-gray-500" />
    {:else}
      <ElText tag="p" text={`No tutorials available for ${$selectedLanguage}.`} addCss="text-gray-500" />
    {/if}
  {/if}

  <div class="mt-6 pt-4 border-t">
    <ElButton variant="ghost" onclick={() => loadTutorialFiles()}>
      <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
      </svg>
      Refresh
    </ElButton>
  </div>
</div>