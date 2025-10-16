<script lang="ts">
  import type { ItemInterface } from '@/models/items/Item.interface'
  import ItemsListComponent from '@/components/items/ItemsList.component.svelte'
  import { useAppStore } from '@/store'

  // Get a reference to our itemsStore instance using our useAppStore() hook
  const { itemsStore } = useAppStore()

  // Get a reference to the items state data through our itemsStore getters
  const { loading, items } = itemsStore.getters

  // Item select event handler
  function onSelectItem(event: { item: ItemInterface }) {
    const item = event.item
    // Invoke our store action to toggle the item.selected property
    itemsStore.actions.toggleItemSelected(item)
  }

  // Svelte 5: Use $effect instead of onMount for lifecycle
  $effect(() => {
    // Invoke our store action to load the items
    itemsStore.actions.loadItems()
  })
</script>

<div>
  <ItemsListComponent loading={$loading} items={$items} onselectitem={onSelectItem} />
</div>
