<script lang="ts">
  import type { ItemInterface } from '@/models/items/Item.interface'
  import ItemsListComponent from '@/components/items/ItemsList.component.svelte'
  import { useAppStore } from '@/store'

  const { itemsStore } = useAppStore()
  const { loading, items } = itemsStore.getters

  function onSelectItem(event: { item: ItemInterface }) {
    itemsStore.actions.toggleItemSelected(event.item)
  }

  $effect(() => {
    itemsStore.actions.loadItems()
  })
</script>

<div>
  <ItemsListComponent loading={$loading} items={$items} onselectitem={onSelectItem} />
</div>
