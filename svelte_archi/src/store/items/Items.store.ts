// file: src/store/items/Items.store.ts

import { writable, derived } from 'svelte/store'
import { getContextClient } from '@urql/svelte'
import { GET_ITEMS, TOGGLE_ITEM } from '../../api-client/graphql/queries'
import type {
  ItemsStateInterface,
  ItemsStoreInterface,
  ItemsStoreActionsInterface,
  ItemsStoreGettersInterface
} from './models'
import type { ItemInterface } from '../../models/items/Item.interface'

// Create the private writable store
const writableItemsStore = writable<ItemsStateInterface>({
  loading: false,
  items: []
})

// Hook to use the store in components
export function useItemsStore(): ItemsStoreInterface {
  const client = getContextClient()

  // Actions implementation
  const actions: ItemsStoreActionsInterface = {
    loadItems: async () => {
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

    toggleItemSelected: async (item: ItemInterface) => {
      console.log('ItemsStore: action: toggleItemSelected', item)

      // Call GraphQL mutation
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
