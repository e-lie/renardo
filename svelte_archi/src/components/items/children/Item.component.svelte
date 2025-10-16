<script lang="ts">
  // import createEventDispatcher from Svelte:
  import { createEventDispatcher } from 'svelte'
  // import a reference to our ItemInterace
  import type { ItemInterface } from '@/models'
  // add the following two lines:
  import ElText from '../../primitives/text/ElText.svelte'
  import ElToggle from '../../primitives/toggles/ElToggle.svelte'

  // expose a property called testid
  export let testid: string = 'not-set'
  // expose a property called isLast
  export let isLast: boolean = false
  // expose a property called item
  export let item: ItemInterface = {
    id: -1,
    name: '',
    selected: false
  }

  // create an instance of Svelte event dispatcher
  const dispatch = createEventDispatcher()

  // a computed property to return a different css class based on the selected value
  $: cssClass = (): string => {
    let css = 'item flex items-center justify-between cursor-pointer border border-l-4 list-none rounded-sm px-3 py-3'
    if (item.selected) {
      css += ' font-bold bg-pink-200 hover:bg-pink-100 selected'
    } else {
      css += ' text-gray-500 hover:bg-gray-100'
    }
    if (!isLast) {
      css += ' border-b-0'
    }
    return css.trim()
  }

  // item click handler
  function handleClick(item: ItemInterface) {
    // dispatch a 'selectItem' even through Svelte dispatch
    dispatch('selectItem', {
      item
    })
  }
</script>

<li role="button" data-testid={testid} class={cssClass()} on:click={() => handleClick(item)}>
  <ElText testid={`${testid}-text`} tag="div" text={item.name} />
  <ElToggle testid={`${testid}-toggle`} checked={item.selected} />
</li>
