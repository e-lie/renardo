<script lang="ts">
  import { useLocalization } from '../../localization'
  import type { ItemInterface } from '../../models/items/Item.interface'
  import ItemComponent from './children/Item.component.svelte'
  import Loader from '../shared/Loader.component.svelte'

  // Svelte 5: use $props() rune for props
  let {
    loading = false,
    items = [],
    onselectitem
  }: {
    loading?: boolean
    items?: ItemInterface[]
    onselectitem?: (event: { item: ItemInterface }) => void
  } = $props()

  const { t } = useLocalization()
</script>

<div>
  <h3>{$t('items.list.header')}:</h3>
  {#if loading}
    <Loader />
  {/if}
  {#if !loading}
    <ul>
      {#each items as item, index}
        <ItemComponent
          testid={`items.list.item.${item.id}`}
          {item}
          isLast={index === items.length - 1}
          {onselectitem}
        />
      {/each}
    </ul>
  {/if}
</div>
