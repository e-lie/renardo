// file: src/store/root/Root.store.ts

import { writable } from 'svelte/store'
import type { RootStoreInterface } from './models'
import type { ItemInterface } from '../../models/items/Item.interface'
import { useItemsStore } from '../items/'

// Router stores for navigation
export const currentPage = writable<'home' | 'items' | 'primitives'>('home')
export const selectedItem = writable<ItemInterface | null>(null)

// Hook that returns our root store instance and will allow us to consume our app store from our components
export function useAppStore(): RootStoreInterface {
  return {
    itemsStore: useItemsStore()
    // additional domain store modules will be eventually added here
  }
}
