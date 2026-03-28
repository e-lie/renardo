export interface LoadFileEventDetail {
  content: string
  title: string
  filePath?: string
  isStartupFile?: boolean
}

export type LoadFileEvent = CustomEvent<LoadFileEventDetail>

export function dispatchLoadFile(
  content: string,
  title: string,
  filePath?: string,
  isStartupFile?: boolean
) {
  const event = new CustomEvent('editor:loadFile', {
    detail: { content, title, filePath, isStartupFile }
  })
  window.dispatchEvent(event)
}
