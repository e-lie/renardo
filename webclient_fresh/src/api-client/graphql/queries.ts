import { gql } from 'graphql-tag'

export const EXECUTE_CODE = gql`
  mutation ExecuteCode($code: String!) {
    executeCode(code: $code) {
      success
      message
      output
    }
  }
`
