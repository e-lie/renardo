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

export const GET_HISTORICAL_LOGS = gql`
  query GetHistoricalLogs($limit: Int = 1000) {
    historicalLogs(limit: $limit) {
      id
      timestamp
      level
      logger
      source
      message
      extra
    }
  }
`

export const SUBSCRIBE_TO_LOGS = gql`
  subscription SubscribeToLogs($filterLevel: String) {
    logs(filterLevel: $filterLevel) {
      id
      timestamp
      level
      logger
      source
      message
      extra
    }
  }
`

export const EXECUTE_CODE = gql`
  mutation ExecuteCode($code: String!) {
    executeCode(code: $code) {
      success
      message
      output
    }
  }
`

export const SEND_FRONTEND_LOG = gql`
  mutation SendFrontendLog($timestamp: String!, $level: String!, $component: String!, $message: String!, $data: String) {
    sendFrontendLog(timestamp: $timestamp, level: $level, component: $component, message: $message, data: $data) {
      success
      message
    }
  }
`
