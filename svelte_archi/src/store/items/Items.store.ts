// file: src/store/items/Items.store.ts

import { writable, derived } from 'svelte/store'
import type {
  ItemsStateInterface,
  ItemsStoreInterface,
  ItemsStoreActionsInterface,
  ItemsStoreGettersInterface
} from './models'
import type { ItemInterface } from '../../models/items/Item.interface'
import { apiClient } from '../../api-client'

// Create the private writable store
const writableItemsStore = writable<ItemsStateInterface>({
  loading: false,
  items: []
})

// Hook to use the store in components
export function useItemsStore(): ItemsStoreInterface {
  // Actions implementation
  const actions: ItemsStoreActionsInterface = {
    // Action to load items from API
    loadItems: async () => {
      // Set loading to true and clear current data
      writableItemsStore.update((state) => {
        state.loading = true
        state.items = []
        return state
      })

      // Fetch data from API (REST or GraphQL)
      const data = await apiClient.items.fetchItems()

      // Update state with fetched data
      writableItemsStore.update((state) => {
        state.items = data
        state.loading = false
        return state
      })
    },

    // Action to toggle an item's selected property
    toggleItemSelected: async (item: ItemInterface) => {
      console.log('ItemsStore: action: toggleItemSelected', item)
      // Update state
      writableItemsStore.update((state) => {
        const itemIndex = (state.items || []).findIndex((a) => a.id === item.id)
        if (itemIndex < 0) {
          console.warn('ItemsStore: action: toggleItemSelected: Could not find item in state')
          return state
        }
        // Toggle selected
        state.items[itemIndex].selected = !state.items[itemIndex].selected
        return state
      })
    }
  }

  // Getters implementation using derived stores
  const loading = derived(writableItemsStore, ($state) => $state.loading)
  const items = derived(writableItemsStore, ($state) => $state.items)

  const getters: ItemsStoreGettersInterface = {
    loading,
    items
  }

  // Return store interface
  return {
    getters,
    actions
  }
}
