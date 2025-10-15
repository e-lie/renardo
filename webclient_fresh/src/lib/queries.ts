import { gql } from 'graphql-tag'

export const GET_POSTS = gql`
  query GetPosts {
    posts {
      id
      title
      content
      createdAt
      author {
        id
        name
        email
      }
    }
  }
`

export const GET_AUTHORS = gql`
  query GetAuthors {
    authors {
      id
      name
      email
      posts {
        id
        title
        createdAt
      }
    }
  }
`