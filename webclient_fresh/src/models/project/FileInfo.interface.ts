export interface FileInfo {
  path: string
  name: string
  is_directory: boolean
  size: number | null
  extension: string | null
}
