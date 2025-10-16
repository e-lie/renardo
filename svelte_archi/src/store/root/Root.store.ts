// file: src/store/root/Root.store.ts

import type { RootStoreInterface } from './models'
import { useItemsStore } from '../items/'

// Hook that returns our root store instance and will allow us to consume our app store from our components
export function useAppStore(): RootStoreInterface {
  return {
    itemsStore: useItemsStore()
    // additional domain store modules will be eventually added here
  }
}
