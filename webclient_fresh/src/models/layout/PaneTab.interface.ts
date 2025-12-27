export type PaneComponentType = 'ColorPicker' | 'TextArea' | 'CodeEditor' | 'TopMenu' | 'ClockDisplay' | 'ProjectExplorerTab' | 'TutorialTab'

export interface PaneTabInterface {
  id: string
  title: string
  componentType: PaneComponentType
  componentId: string
  closable: boolean
  active: boolean
}
