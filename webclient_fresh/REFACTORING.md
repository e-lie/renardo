# webclient_fresh Refactoring Summary

## Vue d'ensemble

Le projet `webclient_fresh` a été complètement refactoré pour suivre les principes de design de `svelte_archi`.

## Changements majeurs

### 📁 Nouvelle structure de dossiers

**Avant:**
```
src/lib/
  ├── components/
  │   ├── PostList.svelte
  │   ├── PostCard.svelte
  │   ├── AuthorList.svelte
  │   ├── AuthorCard.svelte
  │   ├── PostDetail.svelte
  │   ├── Navbar.svelte
  │   └── FlokEditor.svelte
  ├── types.ts
  ├── queries.ts
  └── stores.ts
```

**Après:**
```
src/
  ├── models/                    # Interfaces TypeScript organisées
  ├── api-client/graphql/        # Queries GraphQL centralisées
  ├── components/
  │   ├── primitives/            # ElButton, ElCard, ElText
  │   ├── shared/                # Navbar
  │   ├── posts/                 # Domaine Posts
  │   └── authors/               # Domaine Authors
  ├── store/                     # State management avec actions/getters
  │   ├── posts/
  │   ├── authors/
  │   └── root/
  └── views/                     # Vues/Pages
```

### 🎨 Naming Conventions appliquées

| Type | Convention | Exemple |
|------|------------|---------|
| Primitives | `El` prefix | `ElButton.svelte` |
| Components | `.component.svelte` suffix | `PostCard.component.svelte` |
| Views | `.view.svelte` suffix | `Posts.view.svelte` |
| Stores | `.store.ts` suffix | `Posts.store.ts` |
| Interfaces | `.interface.ts` suffix | `Post.interface.ts` |

### 🏗️ Architecture Pattern

#### Ancien (stores simples)

```typescript
// lib/stores.ts
export const currentPage = writable('posts')
export const selectedPost = writable(null)
```

```svelte
<!-- lib/components/PostList.svelte -->
<script lang="ts">
  import { queryStore, getContextClient } from '@urql/svelte'
  import { GET_POSTS } from '../queries'

  const client = getContextClient()
  const posts = queryStore({ client, query: GET_POSTS })
</script>
```

#### Nouveau (pattern actions/getters)

```typescript
// store/posts/Posts.store.ts
const writablePostsStore = writable<PostsStateInterface>({
  loading: false,
  posts: [],
  selectedPost: null
})

export function usePostsStore(): PostsStoreInterface {
  const client = getContextClient()

  const actions = {
    loadPosts: async () => { /* ... */ },
    selectPost: (post) => { /* ... */ }
  }

  const getters = {
    loading: derived(writablePostsStore, $s => $s.loading),
    posts: derived(writablePostsStore, $s => $s.posts),
    selectedPost: derived(writablePostsStore, $s => $s.selectedPost)
  }

  return { getters, actions }
}
```

```svelte
<!-- views/Posts.view.svelte -->
<script lang="ts">
  import { useAppStore } from '../store'

  const { postsStore } = useAppStore()
  const { loading, posts } = postsStore.getters

  $effect(() => {
    postsStore.actions.loadPosts()
  })
</script>
```

### 📦 Nouveaux composants créés

#### Primitives (nouveaux)

1. **ElButton.svelte**
   - Props: `variant`, `disabled`, `onclick`, `children`
   - Variants: `primary`, `secondary`, `ghost`

2. **ElCard.svelte**
   - Props: `testid`, `addCss`, `children`
   - Wrapper réutilisable pour cartes

3. **ElText.svelte**
   - Props: `tag`, `text`, `addCss`, `testid`
   - Texte flexible avec HTML dynamique

#### Components refactorés

1. **PostCard.component.svelte** (était `PostCard.svelte`)
   - Utilise `ElCard`, `ElButton`
   - Props: `post`, `onselect`
   - Pattern callback au lieu d'events

2. **PostsList.component.svelte** (était `PostList.svelte`)
   - Props: `loading`, `posts`, `onselect`
   - États: loading, empty, list

3. **AuthorCard.component.svelte** (était `AuthorCard.svelte`)
   - Utilise `ElCard`
   - Affiche posts count et preview

4. **AuthorsList.component.svelte** (était `AuthorList.svelte`)
   - Props: `loading`, `authors`
   - Grid layout responsive

#### Views créées

1. **Posts.view.svelte**
   - Charge les posts via store
   - Navigation vers détail

2. **Authors.view.svelte**
   - Charge les authors via store

3. **PostDetail.view.svelte**
   - Affiche post sélectionné
   - Bouton retour

### 🔄 Flux de données

**Ancien (direct GraphQL dans composants):**
```
Component → urql queryStore → GraphQL → Affichage
```

**Nouveau (via stores avec actions/getters):**
```
View → Store Action → GraphQL → Store State → Getter → Affichage
       ↓
     Component (affichage seulement)
```

### 📝 Interfaces TypeScript

Toutes les données ont maintenant des interfaces propres:

```typescript
// models/posts/Post.interface.ts
export interface PostInterface {
  id: string
  title: string
  content: string
  createdAt: string
  author: {
    id: string
    name: string
    email: string
  }
}

// models/authors/Author.interface.ts
export interface AuthorInterface {
  id: string
  name: string
  email: string
  posts?: {
    id: string
    title: string
    createdAt: string
  }[]
}
```

### 🎯 Migration path

| Ancien fichier | Nouveau fichier | Status |
|----------------|-----------------|--------|
| `lib/types.ts` | `models/*/` | ✅ Migré |
| `lib/queries.ts` | `api-client/graphql/queries.ts` | ✅ Migré |
| `lib/stores.ts` | `store/root/Root.store.ts` | ⚠️ Partiel (currentSession reste) |
| `lib/components/PostList.svelte` | `views/Posts.view.svelte` + `components/posts/PostsList.component.svelte` | ✅ Migré |
| `lib/components/PostCard.svelte` | `components/posts/children/PostCard.component.svelte` | ✅ Migré |
| `lib/components/AuthorList.svelte` | `views/Authors.view.svelte` + `components/authors/AuthorsList.component.svelte` | ✅ Migré |
| `lib/components/AuthorCard.svelte` | `components/authors/children/AuthorCard.component.svelte` | ✅ Migré |
| `lib/components/PostDetail.svelte` | `views/PostDetail.view.svelte` | ✅ Migré |
| `lib/components/Navbar.svelte` | `components/shared/Navbar.component.svelte` | ✅ Migré |
| `lib/components/FlokEditor.svelte` | `lib/components/FlokEditor.svelte` | ⏸️ Non migré (keep as is) |

## Bénéfices immédiats

✅ **Code plus organisé** - Structure claire par domaine
✅ **Type safety** - Interfaces complètes partout
✅ **Testabilité** - Stores isolés et testables
✅ **Maintenabilité** - Conventions claires
✅ **Scalabilité** - Facile d'ajouter de nouveaux domaines
✅ **Réutilisabilité** - Primitives et composants modulaires

## Usage rapide

### Ajouter un nouveau domaine (ex: Comments)

1. Créer `models/comments/Comment.interface.ts`
2. Ajouter queries dans `api-client/graphql/queries.ts`
3. Créer `store/comments/Comments.store.ts` avec actions/getters
4. Créer `components/comments/CommentsList.component.svelte`
5. Créer `views/Comments.view.svelte`
6. Ajouter dans `Root.store.ts`

### Créer une primitive

```svelte
<!-- components/primitives/badges/ElBadge.svelte -->
<script lang="ts">
  let {
    variant = 'primary',
    text = '',
    addCss = ''
  }: {
    variant?: 'primary' | 'secondary' | 'accent'
    text?: string
    addCss?: string
  } = $props()

  const cssClass = $derived(() => {
    const classes = ['badge']
    if (variant) classes.push(`badge-${variant}`)
    if (addCss) classes.push(addCss)
    return classes.join(' ')
  })
</script>

<span class={cssClass()}>{text}</span>
```

## Documentation

- **Architecture complète:** Voir `ARCHITECTURE.md`
- **Guide svelte_archi:** Voir `../svelte_archi/svelte_app_scalable.md`

## Notes

- Les anciens fichiers dans `lib/` sont conservés pour FlokEditor
- La migration est progressive et peut coexister
- WebSocket subscriptions ont été simplifiées (fetchExchange seulement pour l'instant)
