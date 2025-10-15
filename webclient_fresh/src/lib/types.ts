export interface Author {
  id: string
  name: string
  email: string
  posts?: Post[]
}

export interface Post {
  id: string
  title: string
  content: string
  createdAt: string
  author: Author
}