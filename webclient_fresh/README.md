# Renardo Webclient Fresh

Un client web moderne pour Renardo, construit avec **Svelte 5**, suivant les principes d'une architecture scalable.

## 🎯 Vue d'ensemble

Cette application est un exemple d'architecture Svelte 5 bien structurée, utilisant:

- **Svelte 5** avec les runes (`$props`, `$state`, `$derived`, `$effect`)
- **TypeScript** pour la sûreté du typage
- **GraphQL** via `@urql/svelte` pour l'API
- **TailwindCSS + DaisyUI** pour le styling
- **Atomic Design** pour l'organisation des composants
- **Flux-like State Management** avec pattern actions/getters

## 📚 Documentation

### 📖 [ARCHITECTURE_GUIDE.md](./ARCHITECTURE_GUIDE.md)

**Documentation complète** de l'architecture et des conventions de l'application, incluant:

- 🏗️ Structure des dossiers détaillée
- 📝 Conventions de nommage
- 🧩 Composants primitifs (Atomic Design)
- 🔄 Gestion d'état (State Management)
- 🌐 Intégration GraphQL avec urql
- 📊 **4 diagrammes Mermaid compilés en SVG**

### 🎨 Diagrammes d'architecture

Tous les diagrammes sont disponibles dans [`docs/diagrams/`](./docs/diagrams/):

| Diagramme | Description |
|-----------|-------------|
| ![component-hierarchy](./docs/diagrams/component-hierarchy.svg) | **Hiérarchie des composants** - De App jusqu'aux primitives |
| ![state-management-flow](./docs/diagrams/state-management-flow.svg) | **Flux du State Management** - Actions → Store → Getters |
| ![graphql-flow](./docs/diagrams/graphql-flow.svg) | **Flux GraphQL** - De la vue à l'API et retour |
| ![primitives-hierarchy](./docs/diagrams/primitives-hierarchy.svg) | **Hiérarchie des primitives** - Atomic Design en détail |

## 🚀 Démarrage rapide

### Installation

```bash
npm install
```

### Développement

```bash
npm run dev
```

L'application sera disponible sur [http://localhost:3001](http://localhost:3001)

### Build de production

```bash
npm run build
```

### Prévisualisation du build

```bash
npm run preview
```

## 📁 Structure du projet

```
src/
├── api-client/          # Client GraphQL
│   └── graphql/
│       └── queries.ts   # Queries & mutations
├── components/
│   ├── primitives/      # Composants atomiques (ElButton, ElCard, ElText)
│   ├── posts/           # Domaine: Posts
│   ├── authors/         # Domaine: Authors
│   └── shared/          # Composants partagés
├── models/              # Interfaces TypeScript
│   ├── posts/
│   └── authors/
├── store/               # State Management
│   ├── root/            # Store racine
│   ├── posts/           # Store posts
│   └── authors/         # Store authors
├── views/               # Pages/Vues
│   ├── Posts.view.svelte
│   ├── Authors.view.svelte
│   └── PostDetail.view.svelte
├── App.svelte           # Composant racine
└── main.ts              # Point d'entrée
```

## 🎨 Principes d'architecture

### 1. Atomic Design

Les composants sont organisés en **primitives** réutilisables (atomes) qui composent des **composants de domaine** (molécules/organismes):

```
Primitives (ElButton, ElCard)
  → Domain Components (PostCard, AuthorCard)
    → Views (Posts.view, Authors.view)
```

### 2. State Management (Flux-like)

Chaque domaine possède son store avec:

- **Actions**: Fonctions qui modifient le state (write)
- **Getters**: Derived stores en lecture seule (read)

```typescript
const { postsStore } = useAppStore()
const { loading, posts } = postsStore.getters

// Appel d'action
postsStore.actions.loadPosts()
```

### 3. GraphQL avec urql

Toutes les données proviennent d'une API GraphQL:

```typescript
// Définir la query
export const GET_POSTS = gql`
  query GetPosts {
    posts { id title content }
  }
`

// Utiliser dans le store
const result = await client.query(GET_POSTS, {})
```

### 4. TypeScript partout

Interfaces strictes pour tous les modèles:

```typescript
export interface PostInterface {
  id: string
  title: string
  content: string
  author: AuthorInterface
}
```

## 🔧 Conventions de nommage

| Type | Convention | Exemple |
|------|-----------|---------|
| Primitives | `El{Name}.svelte` | `ElButton.svelte` |
| Composants | `{Name}.component.svelte` | `PostCard.component.svelte` |
| Vues | `{Name}.view.svelte` | `Posts.view.svelte` |
| Interfaces | `{Name}.interface.ts` | `Post.interface.ts` |
| Stores | `{Domain}.store.ts` | `Posts.store.ts` |

## 🧪 Scripts disponibles

```bash
npm run dev           # Serveur de développement
npm run build         # Build de production
npm run preview       # Prévisualiser le build
npm run check         # Vérification TypeScript
npm test              # Tests unitaires
npm run test:watch    # Tests en mode watch
npm run format        # Formater le code (Prettier)
npm run lint          # Linter (ESLint)
```

## 📝 Svelte 5 Runes

Cette application utilise les nouveaux **runes** de Svelte 5:

```svelte
<script lang="ts">
  // Props
  let { post, onselect } = $props()

  // State local
  let count = $state(0)

  // Computed
  const doubled = $derived(count * 2)

  // Effects
  $effect(() => {
    console.log('Post changed:', post)
  })
</script>
```

## 🎓 Ressources

- [ARCHITECTURE_GUIDE.md](./ARCHITECTURE_GUIDE.md) - Guide complet d'architecture
- [svelte_archi](../svelte_archi/svelte_app_scalable.md) - Guide original des principes
- [Svelte 5 Documentation](https://svelte.dev/docs/svelte/overview)
- [urql Documentation](https://formidable.com/open-source/urql/)
- [TailwindCSS](https://tailwindcss.com/)
- [DaisyUI](https://daisyui.com/)

## 🤝 Contribution

Ce projet suit des conventions strictes. Avant de contribuer:

1. Lire [ARCHITECTURE_GUIDE.md](./ARCHITECTURE_GUIDE.md)
2. Respecter les conventions de nommage
3. Utiliser TypeScript pour tous les nouveaux fichiers
4. Tester localement avant de commit

## 📄 Licence

Ce projet fait partie de Renardo - voir la licence du projet principal.

---

**Note**: Cette architecture est conçue pour être scalable. Pour ajouter un nouveau domaine (ex: "comments"), il suffit de:

1. Créer `models/comments/Comment.interface.ts`
2. Créer `store/comments/Comments.store.ts`
3. Créer `components/comments/CommentCard.component.svelte`
4. Créer `views/Comments.view.svelte`
5. Ajouter le store dans `store/root/index.ts`

Consultez [ARCHITECTURE_GUIDE.md](./ARCHITECTURE_GUIDE.md) pour les détails complets.
