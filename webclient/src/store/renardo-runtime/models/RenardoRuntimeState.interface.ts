export interface RenardoRuntimeStatusInterface {
  running: boolean
  status: string   // "stopped" | "starting" | "running" | "stopping" | "error" | "crashed"
  pid: number | null
}

export interface RenardoRuntimeStateInterface {
  status: RenardoRuntimeStatusInterface
  isLoading: boolean
  error: string | null
}
