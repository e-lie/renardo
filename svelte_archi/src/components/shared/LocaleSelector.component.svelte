<script lang="ts">
  // expose component properties
  export let locales: { key: string }[] = []
  export let currentLocale: string = ''
  export let onLocaleClick: Function
  export let t: Function
</script>

<div class="locale-selector">
  {#each locales as item}
    <label class="cursor-pointer">
      <input
        type="radio"
        group={currentLocale}
        name="locale"
        value={item.key}
        checked={currentLocale === item.key}
        on:click={() => onLocaleClick(item.key)}
      />
      {t(`locale.selector.${item.key}`)}
    </label>
  {/each}
</div>

<style>
  .cursor-pointer {
    cursor: pointer;
  }
</style>
