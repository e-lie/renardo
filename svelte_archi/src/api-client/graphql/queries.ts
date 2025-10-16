// file: src/api-client/graphql/queries.ts

import { gql } from 'graphql-tag'

export const GET_ITEMS = gql`
  query GetItems {
    items {
      id
      name
      selected
    }
  }
`

export const TOGGLE_ITEM = gql`
  mutation ToggleItem($id: Int!) {
    toggleItem(id: $id) {
      id
      name
      selected
    }
  }
`
