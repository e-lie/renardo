import type { PaneInterface, PaneTabInterface } from '../../../models/layout'

export interface PaneSetVisibility {
  left: boolean
  right: boolean
  bottom: boolean
}

export interface HoverStates {
  left: boolean
  right: boolean
  bottom: boolean
}

export interface PaneSizes {
  'left-top': number
  'left-middle': number
  'left-bottom': number
  'right-top': number
  'right-middle': number
  'right-bottom': number
  'bottom-left': number
  'bottom-right': number
}

export interface ContainerSizes {
  'left-column': number
  'right-column': number
  'bottom-area': number
}

export interface LayoutStateInterface {
  panes: Map<string, PaneInterface>
  paneTabConfigs: Map<string, PaneTabInterface[]>
  paneVisibility: Map<string, boolean>
  paneSetVisibility: PaneSetVisibility
  hoverStates: HoverStates
  paneSizes: PaneSizes
  containerSizes: ContainerSizes
  isResizing: boolean
  hideAppNavbar: boolean
}
