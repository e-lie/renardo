# webclient_fresh - Renardo Blog

Application Svelte 5 suivant les principes de design de `svelte_archi`.

## 🎯 Architecture

Cette application suit une architecture scalable basée sur:
- **Atomic Design** - Composants primitives réutilisables
- **Domain-Driven Design** - Organisation par domaine (posts, authors)
- **Actions/Getters Pattern** - State management centralisé et type-safe
- **GraphQL with urql** - Queries optimisées
- **Svelte 5 runes** - API moderne et performante

📖 **Documentation complète:**
- [ARCHITECTURE.md](./ARCHITECTURE.md) - Structure détaillée
- [REFACTORING.md](./REFACTORING.md) - Migration guide
- [STRUCTURE_COMPARISON.md](./STRUCTURE_COMPARISON.md) - Before/After

## 🚀 Quick Start

```bash
# Install dependencies
npm install

# Run dev server
npm run dev

# Build for production
npm run build
```

## 📁 Project Structure

```
src/
├── models/              # TypeScript interfaces
├── api-client/          # GraphQL queries
├── components/
│   ├── primitives/      # ElButton, ElCard, ElText
│   ├── shared/          # Navbar
│   ├── posts/           # Posts domain components
│   └── authors/         # Authors domain components
├── store/               # State management (actions/getters)
│   ├── posts/
│   ├── authors/
│   └── root/
├── views/               # Page-level components
└── App.svelte
```

## 🎨 Key Patterns

### Primitives (Atomic Design)

```svelte
<script lang="ts">
  import { ElButton, ElCard } from './components/primitives'
</script>

<ElCard>
  <div class="card-body">
    <h2>Hello World</h2>
    <ElButton variant="primary" onclick={handleClick}>
      {#snippet children()}
        Click me
      {/snippet}
    </ElButton>
  </div>
</ElCard>
```

### Store Pattern (Actions/Getters)

```svelte
<script lang="ts">
  import { useAppStore } from './store'

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

### Navigation

```svelte
<script lang="ts">
  import { currentPage } from './store/root/Root.store'

  function goToPosts() {
    currentPage.set('posts')
  }
</script>
```

## 🧩 Components

### Primitives

- `ElButton` - Button with variants (primary, secondary, ghost)
- `ElCard` - Card wrapper for content
- `ElText` - Flexible text component

### Domain Components

**Posts:**
- `PostsList.component.svelte` - List of posts
- `PostCard.component.svelte` - Individual post card

**Authors:**
- `AuthorsList.component.svelte` - List of authors
- `AuthorCard.component.svelte` - Individual author card

### Views

- `Posts.view.svelte` - Posts page
- `Authors.view.svelte` - Authors page
- `PostDetail.view.svelte` - Post detail page

## 📦 Store Structure

Each domain has its own store with:
- **Actions** - Methods to modify state
- **Getters** - Derived stores to read state
- **Interfaces** - TypeScript types

```typescript
// store/posts/Posts.store.ts
export function usePostsStore(): PostsStoreInterface {
  return {
    actions: {
      loadPosts: async () => { /* ... */ },
      selectPost: (post) => { /* ... */ }
    },
    getters: {
      loading: Readable<boolean>,
      posts: Readable<PostInterface[]>,
      selectedPost: Readable<PostInterface | null>
    }
  }
}
```

## 🎯 Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| Primitives | `El` prefix | `ElButton.svelte` |
| Components | `.component.svelte` | `PostCard.component.svelte` |
| Views | `.view.svelte` | `Posts.view.svelte` |
| Stores | `.store.ts` | `Posts.store.ts` |
| Interfaces | `.interface.ts` | `Post.interface.ts` |

## 🔄 Adding a New Domain

1. Create model: `models/comments/Comment.interface.ts`
2. Add GraphQL query: `api-client/graphql/queries.ts`
3. Create store: `store/comments/Comments.store.ts`
4. Create component: `components/comments/CommentsList.component.svelte`
5. Create view: `views/Comments.view.svelte`
6. Add to root store: `store/root/Root.store.ts`

## 🛠️ Tech Stack

- **Svelte 5** - Framework with runes
- **TypeScript** - Type safety
- **urql** - GraphQL client
- **DaisyUI** - Component library (TailwindCSS)
- **Vite** - Build tool

## 📚 Learn More

- [Svelte 5 Documentation](https://svelte.dev/docs/svelte/overview)
- [urql Documentation](https://formidable.com/open-source/urql/docs/)
- [svelte_archi Guide](../svelte_archi/svelte_app_scalable.md)

## ✨ Features

- ✅ Type-safe state management
- ✅ GraphQL with urql
- ✅ Atomic design primitives
- ✅ Domain-driven structure
- ✅ Responsive design (DaisyUI)
- ✅ Code editor integration (FlokEditor)
- ✅ Clean navigation pattern

---

Built with ❤️ for **Renardo** - Modern architecture, scalable code
