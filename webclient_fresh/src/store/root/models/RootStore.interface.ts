import type { TutorialStoreInterface } from '../../tutorial/models'
import type { MusicExampleStoreInterface } from '../../music-example/models'
import type { UserDirectoryStoreInterface } from '../../user-directory/models'
import type { WebSocketBackendStoreInterface } from '../../websocket/models'
import type { EditorStoreInterface } from '../../editor/models'

export interface RootStoreInterface {
  tutorialStore: TutorialStoreInterface
  musicExampleStore: MusicExampleStoreInterface
  userDirectoryStore: UserDirectoryStoreInterface
  webSocketBackendStore: WebSocketBackendStoreInterface
  editorStore: EditorStoreInterface
}
