export interface DirectoryEntry {
  name: string
  path: string
  is_directory: boolean
  size: number | null
  modified_time: number | null
  has_children: boolean
}
