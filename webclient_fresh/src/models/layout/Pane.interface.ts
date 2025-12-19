export type PanePosition =
  | 'top-menu'
  | 'left-top' | 'left-middle' | 'left-bottom'
  | 'right-top' | 'right-middle' | 'right-bottom'
  | 'bottom-left' | 'bottom-right'
  | 'center'

export interface PaneDimensions {
  width?: number
  height?: number
  minWidth?: number
  minHeight?: number
}

export interface PaneInterface {
  id: string
  position: PanePosition
  title: string
  dimensions: PaneDimensions
  isVisible: boolean
  isResizable: boolean
}
