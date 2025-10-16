// file: src/store/items/Items.store.graphql.ts
// Alternative implementation using GraphQL instead of REST

import { writable, derived } from 'svelte/store'
import type {
  ItemsStateInterface,
  ItemsStoreInterface,
  ItemsStoreActionsInterface,
  ItemsStoreGettersInterface
} from './models'
import type { ItemInterface } from '../../models/items/Item.interface'
import { getContextClient } from '@urql/svelte'
import { GET_ITEMS, TOGGLE_ITEM } from '../../api-client/graphql/queries'

// Create the private writable store
const writableItemsStore = writable<ItemsStateInterface>({
  loading: false,
  items: []
})

// Hook to use the store in components
export function useItemsStoreGraphQL(): ItemsStoreInterface {
  const client = getContextClient()

  // Actions implementation
  const actions: ItemsStoreActionsInterface = {
    // Action to load items from GraphQL API
    loadItems: async () => {
      // Set loading to true and clear current data
      writableItemsStore.update((state) => ({
        ...state,
        loading: true,
        items: []
      }))

      // Fetch data from GraphQL
      const result = await client.query(GET_ITEMS, {})

      if (result.data?.items) {
        writableItemsStore.update((state) => ({
          ...state,
          items: result.data.items,
          loading: false
        }))
      }
    },

    // Action to toggle an item's selected property via GraphQL mutation
    toggleItemSelected: async (item: ItemInterface) => {
      const result = await client.mutation(TOGGLE_ITEM, { id: item.id })

      if (result.data?.toggleItem) {
        writableItemsStore.update((state) => {
          const itemIndex = state.items.findIndex((a) => a.id === item.id)
          if (itemIndex >= 0) {
            const updatedItems = [...state.items]
            updatedItems[itemIndex] = result.data.toggleItem
            return { ...state, items: updatedItems }
          }
          return state
        })
      }
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
