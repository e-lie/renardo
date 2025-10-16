// file: src/components/primitives/modals/ModalProps.interface.ts
/**
 * @name ModalProps
 * @desrciption Interface that represents the public properties of the Modal component
 */
export interface ModalProps {
  testid?: string // optional
  cancelLabel: string
  confirmLabel: string
  title?: string
  longDesc?: string // optional
  primaryButtonType?: string // optional, defaults to 'primary'
  icon?: any // the icon and iconAddCss props are optional
  iconAddCss?: string
}
