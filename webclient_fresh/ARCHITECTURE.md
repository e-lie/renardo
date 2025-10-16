# webclient_fresh Architecture

Ce projet suit les principes de design définis dans `svelte_archi/svelte_app_scalable.md`.

## Structure du projet

```
src/
├── models/                     # Interfaces TypeScript
│   ├── posts/
│   │   ├── Post.interface.ts
│   │   └── index.ts
│   ├── authors/
│   │   ├── Author.interface.ts
│   │   └── index.ts
│   └── index.ts
│
├── api-client/                 # API communication
│   └── graphql/
│       └── queries.ts          # GET_POSTS, GET_AUTHORS
│
├── components/
│   ├── primitives/             # Composants de base (Atoms)
│   │   ├── buttons/
│   │   │   └── ElButton.svelte
│   │   ├── cards/
│   │   │   └── ElCard.svelte
│   │   ├── text/
│   │   │   └── ElText.svelte
│   │   └── index.ts
│   │
│   ├── shared/                 # Composants partagés
│   │   └── Navbar.component.svelte
│   │
│   ├── posts/                  # Composants domaine Posts
│   │   ├── PostsList.component.svelte
│   │   └── children/
│   │       └── PostCard.component.svelte
│   │
│   └── authors/                # Composants domaine Authors
│       ├── AuthorsList.component.svelte
│       └── children/
│           └── AuthorCard.component.svelte
│
├── store/                      # State management
│   ├── root/
│   │   ├── Root.store.ts       # currentPage store + useAppStore()
│   │   └── models/
│   │       └── RootStore.interface.ts
│   │
│   ├── posts/
│   │   ├── Posts.store.ts      # usePostsStore()
│   │   └── models/
│   │       ├── PostsState.interface.ts
│   │       └── PostsStore.interface.ts
│   │
│   ├── authors/
│   │   ├── Authors.store.ts    # useAuthorsStore()
│   │   └── models/
│   │       ├── AuthorsState.interface.ts
│   │       └── AuthorsStore.interface.ts
│   │
│   └── index.ts
│
├── views/                      # Vues/Pages
│   ├── Posts.view.svelte
│   ├── Authors.view.svelte
│   └── PostDetail.view.svelte
│
├── lib/                        # Legacy (à migrer)
│   ├── components/
│   │   └── FlokEditor.svelte
│   ├── stores.ts               # currentSession
│   └── ...
│
└── App.svelte                  # Point d'entrée
```

## Principes de design appliqués

### 1. Naming Conventions

- **Primitives:** Préfixe `El` (ElButton, ElCard, ElText)
- **Components:** Suffixe `.component.svelte`
- **Views:** Suffixe `.view.svelte`
- **Stores:** Suffixe `.store.ts`
- **Interfaces:** Suffixe `.interface.ts`

### 2. Atomic Design

Les composants primitives sont dans `components/primitives/`:
- `ElButton` - Bouton réutilisable avec variants
- `ElCard` - Carte pour contenir du contenu
- `ElText` - Composant texte flexible

### 3. State Management Pattern

Chaque domaine (posts, authors) a son propre store avec:

**Structure:**
```typescript
// 1. État privé
const writableStore = writable<StateInterface>({...})

// 2. Hook public
export function useXStore(): XStoreInterface {
  // 3. Actions pour modifier l'état
  const actions = {
    loadData: async () => {...},
    updateData: (data) => {...}
  }

  // 4. Getters (derived) pour lire l'état
  const loading = derived(writableStore, $s => $s.loading)
  const data = derived(writableStore, $s => $s.data)

  const getters = { loading, data }

  return { getters, actions }
}
```

**Utilisation dans les composants:**
```svelte
<script lang="ts">
  import { useAppStore } from '../store'

  const { postsStore } = useAppStore()
  const { loading, posts } = postsStore.getters

  $effect(() => {
    postsStore.actions.loadPosts()
  })
</script>

{#if $loading}
  <p>Loading...</p>
{:else}
  {#each $posts as post}
    <div>{post.title}</div>
  {/each}
{/if}
```

### 4. GraphQL Integration

GraphQL queries centralisées dans `api-client/graphql/queries.ts`.

Les stores utilisent `@urql/svelte`:
```typescript
import { getContextClient } from '@urql/svelte'
import { GET_POSTS } from '../../api-client/graphql/queries'

const client = getContextClient()
const result = await client.query(GET_POSTS, {})
```

### 5. Component Architecture

**Hiérarchie:**
```
View (Posts.view.svelte)
  └── List Component (PostsList.component.svelte)
       └── Card Component (PostCard.component.svelte)
            └── Primitives (ElCard, ElButton, ElText)
```

**Props pattern (Svelte 5):**
```svelte
<script lang="ts">
  let {
    loading = false,
    posts = [],
    onselect
  }: {
    loading?: boolean
    posts?: PostInterface[]
    onselect?: (post: PostInterface) => void
  } = $props()
</script>
```

### 6. Navigation

Navigation simple avec store:
```typescript
import { currentPage } from './store/root/Root.store'

// Navigation
currentPage.set('posts')

// Dans le template
{#if $currentPage === 'posts'}
  <PostsView />
{/if}
```

## Migration depuis l'ancienne structure

L'ancienne structure dans `lib/` est progressivement migrée vers la nouvelle architecture:

**Ancien:**
```
src/lib/
  ├── components/
  │   ├── PostList.svelte
  │   └── PostCard.svelte
  ├── types.ts
  ├── queries.ts
  └── stores.ts
```

**Nouveau:**
```
src/
  ├── models/posts/Post.interface.ts
  ├── api-client/graphql/queries.ts
  ├── store/posts/Posts.store.ts
  ├── components/posts/
  └── views/Posts.view.svelte
```

## Avantages de cette architecture

✅ **Scalabilité** - Facile d'ajouter de nouveaux domaines (comments, likes, etc.)
✅ **Maintenabilité** - Code organisé par domaine et responsabilité
✅ **Réutilisabilité** - Primitives et composants modulaires
✅ **Type safety** - TypeScript partout avec interfaces claires
✅ **Testabilité** - Stores et composants isolés
✅ **Cohérence** - Conventions de nommage claires

## Prochaines étapes

- [ ] Migrer FlokEditor vers la nouvelle structure
- [ ] Ajouter tests unitaires pour les stores
- [ ] Ajouter tests de composants
- [ ] Documenter les primitives dans un Storybook
- [ ] Supprimer les anciens fichiers dans `lib/` une fois migrés
