// file: src/store/items/Items.store.ts

// import a reference to Svelte's writable from 'svelte/store'
import * as SvelteStore from 'svelte/store'

// import references to our itesms tore and actions interfaces
import {
  ItemsStateInterface,
  ItemsStoreInterface,
  ItemsStoreActionsInterface,
  ItemsStoreGettersInterface
} from './models'
// import a reference to our ItemInterface
import { ItemInterface } from '../../models/items/Item.interface'

// import a reference to our apiClient instance
import { apiClient } from '../../api-client'

const writableItemsStore = SvelteStore.writable<ItemsStateInterface>({
  loading: false,
  items: []
})

// hook to allows us to consume the ItemsStore instance in our components
export function useItemsStore(): ItemsStoreInterface {
  // our items store actions implementation:
  const actions: ItemsStoreActionsInterface = {
    // action that we invoke to load the items from an api:
    loadItems: async () => {
      // set loading to true and clear current data:
      writableItemsStore.update((state) => {
        state.loading = true
        state.items = []
        return state
      })

      // invoke our API cient fetchItems to load the data from an API end-point
      const data = await apiClient.items.fetchItems()

      // set items data and loading to false
      writableItemsStore.update((state) => {
        state.items = data
        state.loading = false
        return state
      })
    },
    // action we invoke to toggle an item.selected property
    toggleItemSelected: async (item: ItemInterface) => {
      console.log('ItemsStore: action: toggleItemSelected', item)
      // update our state
      writableItemsStore.update((state) => {
        const itemIndex = (state.items || []).findIndex((a) => a.id === item.id)
        if (itemIndex < 0) {
          console.warn('ItemsStore: action: toggleItemSelected: Could not find item in our state')
          return
        }
        // toggle selected
        state.items[itemIndex].selected = !state.items[itemIndex].selected
        // keep current loading value
        state.loading = state.loading
        return state
      })
    }
  }

  // our items store getters implementation:
  const loading = SvelteStore.derived(writableItemsStore, ($state) => $state.loading)
  const items = SvelteStore.derived(writableItemsStore, ($state) => $state.items)

  const getters: ItemsStoreGettersInterface = {
    loading,
    items
  }

  // return our store intance implementation
  return {
    getters,
    actions
  }
}
