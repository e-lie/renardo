# Svelte 5 Architecture - Source Code Examples

This directory contains partial implementation examples demonstrating the architecture patterns described in `../svelte_app_scalable.md`.

## Directory Structure

```
src/
├── api-client/              # API communication layer
│   └── graphql/            # GraphQL queries and mutations
│       └── queries.ts      # Item queries (GET_ITEMS, TOGGLE_ITEM)
├── components/             # UI components
│   ├── primitives/         # Basic UI elements (Atoms)
│   │   ├── buttons/        # Button components
│   │   ├── text/           # Text components (ElText)
│   │   ├── toggles/        # Toggle components (ElToggle)
│   │   ├── modals/         # Modal components
│   │   ├── icons/          # Icon components
│   │   └── inputs/         # Input components
│   ├── shared/             # Shared components (Loader, etc.)
│   └── items/              # Domain-specific components
│       ├── ItemsList.component.svelte
│       └── children/
│           └── Item.component.svelte
├── models/                 # TypeScript interfaces
│   └── items/
│       └── Item.interface.ts
├── store/                  # State management
│   ├── root/               # Root store and routing
│   │   └── Root.store.ts   # currentPage, selectedItem stores
│   └── items/              # Items domain store
│       ├── Items.store.ts          # REST version
│       ├── Items.store.graphql.ts  # GraphQL version
│       └── models/         # Store interfaces
└── views/                  # Page-level components
    ├── Home.view.svelte
    ├── Items.view.svelte
    └── Primitives.view.svelte
```

## Key Patterns Implemented

### 1. Svelte 5 Runes

All components use Svelte 5 runes:
- `$props()` for component props
- `$derived()` for computed values
- `$effect()` for side effects/lifecycle
- `$state()` for local reactive state

### 2. Primitives (Atomic Design)

Components in `components/primitives/` are prefixed with `El` (for "element"):
- `ElText.svelte` - Text rendering component
- `ElToggle.svelte` - Toggle/switch component
- `ElButton.svelte` - Button component

### 3. State Management

The store pattern uses:
- **writable stores** for state
- **derived stores** for computed values
- **useXStore() hooks** to access stores
- **actions/getters** pattern for organization

Two implementations provided:
- `Items.store.ts` - REST API version
- `Items.store.graphql.ts` - GraphQL version

### 4. Event Handling

Svelte 5 uses callback props instead of event dispatchers:
- **Old (Svelte 4):** `on:click` with `createEventDispatcher()`
- **New (Svelte 5):** `onclick` prop with callback function

### 5. GraphQL Integration

GraphQL queries defined in `api-client/graphql/queries.ts`:
- Query: `GET_ITEMS`
- Mutation: `TOGGLE_ITEM`

Used with `@urql/svelte` for GraphQL client.

### 6. Routing

Simple store-based routing in `store/root/Root.store.ts`:
- `currentPage` - which view to show
- `selectedItem` - selected item state

## Usage Examples

### Using a Primitive Component

```svelte
<script lang="ts">
  import ElToggle from './components/primitives/toggles/ElToggle.svelte'

  function handleToggle(event: { id: string }) {
    console.log('Toggled:', event.id)
  }
</script>

<ElToggle
  id="my-toggle"
  checked={true}
  onclick={handleToggle}
/>
```

### Using the Items Store

```svelte
<script lang="ts">
  import { useAppStore } from './store'

  const { itemsStore } = useAppStore()
  const { loading, items } = itemsStore.getters

  $effect(() => {
    itemsStore.actions.loadItems()
  })
</script>

{#if $loading}
  <p>Loading...</p>
{:else}
  <ul>
    {#each $items as item}
      <li>{item.name}</li>
    {/each}
  </ul>
{/if}
```

### Navigation with Routing Stores

```svelte
<script lang="ts">
  import { currentPage } from './store/root/Root.store'

  function goToItems() {
    currentPage.set('items')
  }
</script>

<button onclick={goToItems}>View Items</button>
```

## Notes

- All components are TypeScript-enabled
- Components use TailwindCSS for styling
- Store pattern is modular and scalable
- GraphQL and REST versions coexist as examples
