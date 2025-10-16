// file: src/store/items/models/ItemsState.interface.ts

import type { ItemInterface } from '@/models'

/**
 * @name ItemsStateInterface
 * @description Interface represnets our Items state
 */
export interface ItemsStateInterface {
  loading: boolean
  items: ItemInterface[]
}
