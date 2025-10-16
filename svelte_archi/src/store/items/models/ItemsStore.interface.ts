// file: src/store/items/models/ItemsStore.interface.ts

// import a reference to Svelte's writable from 'svelte/store'
import * as SvelteStore from 'svelte/store'
// import a reference to our ItemInterface:
import type { ItemInterface } from '@/models'

/**
 * @name ItemsStoreActionsInterface
 * @description Interface represents our Items state actions
 */
export interface ItemsStoreActionsInterface {
  loadItems(): Promise<void>
  toggleItemSelected(item: ItemInterface): Promise<void>
}

/**
 * @name ItemsStoreGettersInterface
 * @description Interface represents our store getters
 * Getters will be used to consume the data from the store.
 */
export interface ItemsStoreGettersInterface {
  // note: we have to use type SvelteStore.Readable on these properties
  loading: SvelteStore.Readable<boolean>
  items: SvelteStore.Readable<ItemInterface[]>
}

/**
 * @name ItemsStoreInterface
 * @description Interface represents our Items store module
 */
export interface ItemsStoreInterface {
  actions: ItemsStoreActionsInterface
  getters: ItemsStoreGettersInterface
}
