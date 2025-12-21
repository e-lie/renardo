<script lang="ts">
  import type { Snippet } from 'svelte'

  let {
    languages = [],
    selectedLanguage = '',
    onchange,
    children
  }: {
    languages?: string[]
    selectedLanguage?: string
    onchange?: (language: string) => void
    children?: Snippet
  } = $props()

  function handleChange(event: Event) {
    const target = event.target as HTMLSelectElement
    if (target) {
      onchange?.(target.value)
    }
  }
</script>

<div class="form-control w-full max-w-xs">
  <label class="label" for="language-select">
    <span class="label-text">Language</span>
  </label>
  <select 
    id="language-select"
    class="select select-bordered" 
    value={selectedLanguage}
    onchange={handleChange}
  >
    {#each languages as language}
      <option value={language} selected={language === selectedLanguage}>
        {language.toUpperCase()}
      </option>
    {/each}
  </select>
  {#if children}
    {@render children()}
  {/if}
</div>