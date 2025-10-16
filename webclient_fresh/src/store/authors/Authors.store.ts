import { writable, derived } from 'svelte/store'
import { getContextClient } from '@urql/svelte'
import { GET_AUTHORS } from '../../api-client/graphql/queries'
import type {
  AuthorsStateInterface,
  AuthorsStoreInterface,
  AuthorsStoreActionsInterface,
  AuthorsStoreGettersInterface
} from './models'

const writableAuthorsStore = writable<AuthorsStateInterface>({
  loading: false,
  authors: []
})

export function useAuthorsStore(): AuthorsStoreInterface {
  const client = getContextClient()

  const actions: AuthorsStoreActionsInterface = {
    loadAuthors: async () => {
      writableAuthorsStore.update((state) => ({
        ...state,
        loading: true,
        authors: []
      }))

      const result = await client.query(GET_AUTHORS, {})

      if (result.data?.authors) {
        writableAuthorsStore.update((state) => ({
          ...state,
          authors: result.data.authors,
          loading: false
        }))
      }
    }
  }

  const loading = derived(writableAuthorsStore, ($state) => $state.loading)
  const authors = derived(writableAuthorsStore, ($state) => $state.authors)

  const getters: AuthorsStoreGettersInterface = {
    loading,
    authors
  }

  return {
    getters,
    actions
  }
}
