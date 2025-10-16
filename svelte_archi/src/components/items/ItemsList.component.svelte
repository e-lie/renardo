<script lang="ts">
  // import localization
  import { useLocalization } from '../../localization'
  // import a reference to our ItemInterace
  import type { ItemInterface } from '../../models/items/Item.interface'
  // import a reference to our Item component
  import ItemComponent from './children/Item.component.svelte'
  // import a reference to our Loader component:
  import Loader from '../shared/Loader.component.svelte'

  // expose loading property:
  export let loading = false
  // expose a property called items with a default value of a blank array
  export let items: ItemInterface[] = []
  // expose a property to pass our selectItem event to the parent component
  export let selectItem: (event: CustomEvent<{ item: ItemInterface }>) => void

  // private
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
          on:selectItem={selectItem}
        />
      {/each}
    </ul>
  {/if}
</div>
