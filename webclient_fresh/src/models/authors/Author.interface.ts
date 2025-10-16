export interface AuthorInterface {
  id: string
  name: string
  email: string
  posts?: {
    id: string
    title: string
    createdAt: string
  }[]
}
