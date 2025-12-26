import type { TutorialStoreInterface } from '../../tutorial/models'
import type { WebSocketBackendStoreInterface } from '../../websocket/models'

export interface RootStoreInterface {
  tutorialStore: TutorialStoreInterface
  webSocketBackendStore: WebSocketBackendStoreInterface
}
