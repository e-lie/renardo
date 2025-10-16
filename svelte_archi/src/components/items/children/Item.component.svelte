<script lang="ts">
  import type { ItemInterface } from '@/models'
  import ElText from '../../primitives/text/ElText.svelte'
  import ElToggle from '../../primitives/toggles/ElToggle.svelte'

  let {
    testid = 'not-set',
    isLast = false,
    item = {
      id: -1,
      name: '',
      selected: false
    },
    onselectitem
  }: {
    testid?: string
    isLast?: boolean
    item?: ItemInterface
    onselectitem?: (event: { item: ItemInterface }) => void
  } = $props()

  const cssClass = $derived(() => {
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
  })

  function handleClick() {
    if (onselectitem) {
      onselectitem({ item })
    }
  }
</script>

<li role="button" data-testid={testid} class={cssClass()} onclick={handleClick}>
  <ElText testid={`${testid}-text`} tag="div" text={item.name} />
  <ElToggle testid={`${testid}-toggle`} checked={item.selected} />
</li>
