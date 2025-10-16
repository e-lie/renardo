
# Svelte 5 App Design Guideline

A scalable architecture guide for Svelte 5 applications with modern patterns and GraphQL integration.

The implementation examples are inside `./src` next to this file. 

## data model interfaces

To lay the foundation for building large-scale applications, we will start by creating a new
sub-directory under src called models. The organization of files and directories plays a
critical role in the success of large-scale code bases. As such, it’s essential to establish a
consistent naming convention and directory structure from the outset. This will help ensure
that the code remains organized, easy to understand, and maintainable as the application
grows and the number of source files and directories increases.

`src/models/items/index.ts` :

```ts
export * from './Item.interface'
```

`src/models/items/Item.interface.ts` :

```ts
export interface ItemInterface {
  id: number
  name: string
  selected: boolean
}
```

interface utilisé ensuite dans les composants "primitives" ou composants de plus haut niveau

## Atomic design primitives

The way you can think of and organize your components might follow one or more
methodologies. One methodology that has seen an increase in adoption recently is Atomic
Design originally introduced by Brad Frost⁴³. You are free to follow this or other
methodologies either strictly or more losely, as well as chose to implement your own or even
use a mix of ideas from different ones.
In my personal and pragmatical way, I found over the years that all I really need is a
foundation of the most primitive elements like buttons/textboxes/dropdowns/etc. These
primitives should be as simple as possible, even though in some cases the might contain
quite a bit of logic to determine how they render. In my world, primitives are more or less
the same as the Atoms in Atomic Design

One of the convention we will follow is to put all our primitive components under the
directory `src/components/primitives`

We’ll follow also a naming convention where each .vue file that represents a primitive will
start with the El prefix. I.e. ElText.svelte, ElIcon.svelte, etc. In this case El is for “element”.
You are of course free to decide your own naming convention. But I strongly suggest using
some kind of prefix to more quickly identify a primitive by just looking at its file name
when it is open in your editor.
Create the following 5 sub-directories to get started:
• src/components/primitives/buttons
• src/components/primitives/text

`ElText.svelte`:

```svelte
<script lang="ts">
  // Use $props() rune to define props
  let {
    testid = 'not-set',
    id = 'id-not-set',
    tag = 'span',
    text = 'text-not-set',
    addCss = ''
  }: {
    testid?: string
    id?: string
    tag?: string
    text?: string
    addCss?: string
  } = $props()

  // Use $derived rune for computed values
  const cssClass = $derived(() => {
    const cssClasses = ['p-1']
    if ((addCss || '').trim().length > 0) {
      cssClasses.push(addCss.trim())
    }
    return cssClasses.join(' ').trim()
  })

  const render = $derived(() => {
    return `<${tag} id="${id}" data-testid="${testid}" class="${cssClass()}">${text}</${tag}>`
  })
</script>

{@html render()}
```

• src/components/primitives/modals
• src/components/primitives/inputs
• src/components/primitives/icons
• src/components/primitives/toggles

`ElToggle.svelte`:

```svelte
<script lang="ts">
  let {
    testid = 'not-set',
    id = 'not-set',
    checked = false,
    disabled = false,
    addCss = '',
    onclick
  }: {
    testid?: string
    id?: string
    checked?: boolean
    disabled?: boolean
    addCss?: string
    onclick?: (event: { id: string }) => void
  } = $props()

  const cssClass = $derived(() => {
    const result = [
      'relative inline-flex flex-shrink-0 h-6 w-12 border-1 rounded-full cursor-pointer transition-colors duration-200 focus:outline-none'
    ]
    if (checked) {
      result.push('bg-green-400')
    } else {
      result.push('bg-gray-300')
    }
    if (disabled) {
      result.push('opacity-40 cursor-not-allowed')
    }
    if ((addCss || '').trim().length > 0) {
      result.push(addCss.trim())
    }
    return result.join(' ').trim()
  })

  const innerCssClass = $derived(() => {
    const result = [
      'bg-white shadow pointer-events-none inline-block h-6 w-6 rounded-full transform ring-0 transition duration-200'
    ]
    if (checked) {
      result.push('translate-x-6')
    } else {
      result.push('translate-x-0')
    }
    return result.join(' ').trim()
  })

  function handleClick() {
    if (!disabled && onclick) {
      onclick({ id })
    }
  }
</script>

<button
  type="button"
  role="checkbox"
  data-testid={testid}
  aria-checked={checked}
  {disabled}
  class={cssClass()}
  onclick={handleClick}
>
  <span class={innerCssClass()} />
</button>
```

One of the things we are going to consistently need in each primitive is the main CSS class
property. Often, this will have to be a computed property that returns the appropriate value
based on other conditions. For example, a Button might have to render with an additional
“disabled” CSS class if its disabled property is true.
For consistency, every time a primitive needs a dynamic CSS class, we’ll add a computed
property called cssClass that will return the appropriate value based on various conditions.
Here is a code example for an hypotethical Button component:

```svelte
<script lang="ts">
  let { disabled = false, label = '' } = $props()

  const cssClass = $derived(() => {
    const cssClasses = ['p-6'] // in TailwindCSS this means we want a padding of 6
    if (disabled) {
      cssClasses.push('disabled')
    }
    return cssClasses.join(' ')
  })
</script>

<button type="button" class={cssClass()}>
  <span class="name">{label}</span>
</button>
```

### Primitives View

Let’s create a view where we can consume our primitives so that we can visually debug and
prototype them as we develop them. This view can become apoint of reference for our basic
library of primitives from which we will build more complex components later.
Create the following file:
• src/views/Primitives.view.svelte

```svelte
<script lang="ts">
// import a reference to the ElText primitive
import ElText from '@/components/primitives/text/ElText.svelte'
</script>
<div>
<div class="about">
<ElText tag="h1" addCss="text-gray-500" text="Primitives"/>
<ElText tag="h2" addCss="text-gray-500" text="ElText examples:"/>
<div class="p-6 border">
<ElText tag="h2" addCss="text-red-500" text="Here ElText will render a &lth2&g\
t element"/>
<ElText tag="p" addCss="text-red-700" text="Here ElText will render a &ltp&gt \
element"/>
</div>
</div>
</div>
```

### Composant de plus haut niveau

Let’s now consume the primitives we created so far within the Item component.
As we do this, we’ll make any additional adjustment we discover necessary.
Finally, if needed, we might be creating additional primitives that we do not have yet (i.e. a
list)

opening the file `src/components/items/children/Item.component.svelte` and
observe the example :

```svelte
<script lang="ts">
  import type { ItemInterface } from '@/models'
  import ElText from '../../primitives/text/ElText.svelte'
  import ElToggle from '../../primitives/toggles/ElToggle.svelte'

  let {
    testid = 'not-set',
    isLast = false,
    item = {
      id: -1,
      name: '',
      selected: false
    },
    onselectitem
  }: {
    testid?: string
    isLast?: boolean
    item?: ItemInterface
    onselectitem?: (event: { item: ItemInterface }) => void
  } = $props()

  const cssClass = $derived(() => {
    let css = 'item flex items-center justify-between cursor-pointer border border-l-4 list-none rounded-sm px-3 py-3'
    if (item.selected) {
      css += ' font-bold bg-pink-200 hover:bg-pink-100 selected'
    } else {
      css += ' text-gray-500 hover:bg-gray-100'
    }
    if (!isLast) {
      css += ' border-b-0'
    }
    return css.trim()
  })

  function handleClick() {
    if (onselectitem) {
      onselectitem({ item })
    }
  }
</script>

<li role="button" data-testid={testid} class={cssClass()} onclick={handleClick}>
  <ElText testid={`${testid}-text`} tag="div" text={item.name} />
  <ElToggle testid={`${testid}-toggle`} checked={item.selected} />
</li>
```

Et puis `src/components/items/ItemsList.component.svelte`

```svelte
<script lang="ts">
  import { useLocalization } from '../../localization'
  import type { ItemInterface } from '../../models/items/Item.interface'
  import ItemComponent from './children/Item.component.svelte'
  import Loader from '../shared/Loader.component.svelte'

  let {
    loading = false,
    items = [],
    onselectitem
  }: {
    loading?: boolean
    items?: ItemInterface[]
    onselectitem?: (event: { item: ItemInterface }) => void
  } = $props()

  const { t } = useLocalization()
</script>

<div>
  <h3>{$t('items.list.header')}:</h3>
  {#if loading}
    <Loader />
  {/if}
  {#if !loading}
    <ul>
      {#each items as item, index}
        <ItemComponent
          testid={`items.list.item.${item.id}`}
          {item}
          isLast={index === items.length - 1}
          {onselectitem}
        />
      {/each}
    </ul>
  {/if}
</div>
```

## GraphQL Integration with urql

For applications that need to communicate with a GraphQL API, the `@urql/svelte` library provides an excellent solution with built-in support for queries, mutations, and subscriptions.

### Setting up urql client

First, install the required dependencies:

```bash
npm install @urql/svelte graphql graphql-tag graphql-ws
```

In your main `App.svelte`, configure the urql client:

```svelte
<script lang="ts">
  import { setContextClient, createClient, fetchExchange } from '@urql/svelte'

  // Create the urql client
  const client = createClient({
    url: 'http://localhost:8000/graphql',
    exchanges: [fetchExchange]
  })

  // Make the client available to all child components
  setContextClient(client)
</script>
```

### Defining GraphQL queries for Items

Create a `src/api-client/graphql/queries.ts` file to centralize your GraphQL queries:

```typescript
import { gql } from 'graphql-tag'

export const GET_ITEMS = gql`
  query GetItems {
    items {
      id
      name
      selected
    }
  }
`

export const TOGGLE_ITEM = gql`
  mutation ToggleItem($id: Int!) {
    toggleItem(id: $id) {
      id
      name
      selected
    }
  }
`
```

The types remain in `src/models/items/Item.interface.ts` as before:

```typescript
export interface ItemInterface {
  id: number
  name: string
  selected: boolean
}
```

### Using GraphQL in the Items Store

Update `src/store/items/Items.store.ts` to use GraphQL instead of REST:

```typescript
import { writable, derived } from 'svelte/store'
import type { ItemInterface } from '../../models/items/Item.interface'
import { getContextClient } from '@urql/svelte'
import { GET_ITEMS, TOGGLE_ITEM } from '../../api-client/graphql/queries'

interface ItemsState {
  loading: boolean
  items: ItemInterface[]
}

const writableItemsStore = writable<ItemsState>({
  loading: false,
  items: []
})

export function useItemsStore() {
  const client = getContextClient()

  const actions = {
    loadItems: async () => {
      writableItemsStore.update(state => ({
        ...state,
        loading: true,
        items: []
      }))

      const result = await client.query(GET_ITEMS, {})

      if (result.data?.items) {
        writableItemsStore.update(state => ({
          ...state,
          items: result.data.items,
          loading: false
        }))
      }
    },

    toggleItemSelected: async (item: ItemInterface) => {
      const result = await client.mutation(TOGGLE_ITEM, { id: item.id })

      if (result.data?.toggleItem) {
        writableItemsStore.update(state => {
          const itemIndex = state.items.findIndex(a => a.id === item.id)
          if (itemIndex >= 0) {
            const updatedItems = [...state.items]
            updatedItems[itemIndex] = result.data.toggleItem
            return { ...state, items: updatedItems }
          }
          return state
        })
      }
    }
  }

  const loading = derived(writableItemsStore, $state => $state.loading)
  const items = derived(writableItemsStore, $state => $state.items)

  return {
    loading,
    items,
    actions
  }
}
```

### Using the store in components (Svelte 5)

```svelte
<script lang="ts">
  import { useItemsStore } from '../../store/items/Items.store'
  import ItemComponent from './children/Item.component.svelte'
  import Loader from '../shared/Loader.component.svelte'

  const { loading, items, actions } = useItemsStore()

  // Load items on component mount using Svelte 5's $effect
  $effect(() => {
    actions.loadItems()
  })

  function handleSelectItem(event: { item: ItemInterface }) {
    actions.toggleItemSelected(event.item)
  }
</script>

<div>
  <h3>Items List:</h3>
  {#if $loading}
    <Loader />
  {:else}
    <ul>
      {#each $items as item, index}
        <ItemComponent
          {item}
          isLast={index === $items.length - 1}
          onselectitem={handleSelectItem}
        />
      {/each}
    </ul>
  {/if}
</div>
```

## i18n

look at `./src` example

## State management

One of the most important parts of an app that will grow large is to decide how to manage
its state.

**Single source of truth:**
The most important reason to implement a centralized state manager is to have a "single
source of truth" for the application state/data. This simply means that our application state
has only one global, centralized source. The responsibility of changing that state is only in
the hands of our state manager. This ensures consistent behavior across your app.

### State Management Pattern

Let's implement a state manager that follows this pattern:
• We invoke an action on our state manager from a component
• The state manager performs tasks within that action
• The state manager commits changes to our state
• The state manager is organized into modules (each module represents a domain/area
  of the application: items, authors, companies, projects, products, categories, etc.)

### Svelte Stores with GraphQL

Svelte's built-in stores (`writable`, `derived`) provide reactive state management.

`src/store/items/Items.store.ts`:

```typescript
import { writable, derived } from 'svelte/store'
import { getContextClient } from '@urql/svelte'
import { GET_ITEMS, TOGGLE_ITEM } from '../../api-client/graphql/queries'
import type { ItemInterface } from '../../models/items/Item.interface'
import type {
  ItemsStateInterface,
  ItemsStoreInterface,
  ItemsStoreActionsInterface,
  ItemsStoreGettersInterface
} from './models'

// Create the private writable store
const writableItemsStore = writable<ItemsStateInterface>({
  loading: false,
  items: []
})

// Hook to use the store in components
export function useItemsStore(): ItemsStoreInterface {
  const client = getContextClient()

  // Actions implementation
  const actions: ItemsStoreActionsInterface = {
    loadItems: async () => {
      writableItemsStore.update((state) => ({
        ...state,
        loading: true,
        items: []
      }))

      // Fetch data from GraphQL
      const result = await client.query(GET_ITEMS, {})

      if (result.data?.items) {
        writableItemsStore.update((state) => ({
          ...state,
          items: result.data.items,
          loading: false
        }))
      }
    },

    toggleItemSelected: async (item: ItemInterface) => {
      // Call GraphQL mutation
      const result = await client.mutation(TOGGLE_ITEM, { id: item.id })

      if (result.data?.toggleItem) {
        writableItemsStore.update((state) => {
          const itemIndex = state.items.findIndex((a) => a.id === item.id)
          if (itemIndex >= 0) {
            const updatedItems = [...state.items]
            updatedItems[itemIndex] = result.data.toggleItem
            return { ...state, items: updatedItems }
          }
          return state
        })
      }
    }
  }

  // Getters implementation using derived stores
  const loading = derived(writableItemsStore, ($state) => $state.loading)
  const items = derived(writableItemsStore, ($state) => $state.items)

  const getters: ItemsStoreGettersInterface = {
    loading,
    items
  }

  // Return store interface
  return {
    getters,
    actions
  }
}
```

### Store interfaces and types

`src/store/items/models/ItemsState.interface.ts`:

```typescript
import type { ItemInterface } from '../../../models/items/Item.interface'

export interface ItemsStateInterface {
  loading: boolean
  items: ItemInterface[]
}
```

`src/store/items/models/ItemsStore.interface.ts`:

```typescript
import type { Readable } from 'svelte/store'
import type { ItemInterface } from '../../../models/items/Item.interface'

export interface ItemsStoreActionsInterface {
  loadItems: () => Promise<void>
  toggleItemSelected: (item: ItemInterface) => Promise<void>
}

export interface ItemsStoreGettersInterface {
  loading: Readable<boolean>
  items: Readable<ItemInterface[]>
}

export interface ItemsStoreInterface {
  getters: ItemsStoreGettersInterface
  actions: ItemsStoreActionsInterface
}
```

### Using stores in Svelte 5 components

```svelte
<script lang="ts">
  import { useItemsStore } from '../../store/items/Items.store'
  import ItemComponent from './children/Item.component.svelte'
  import Loader from '../shared/Loader.component.svelte'
  import type { ItemInterface } from '../../models/items/Item.interface'

  const itemsStore = useItemsStore()

  // Load items on component mount using Svelte 5's $effect
  $effect(() => {
    itemsStore.actions.loadItems()
  })

  function handleSelectItem(event: { item: ItemInterface }) {
    itemsStore.actions.toggleItemSelected(event.item)
  }
</script>

<div>
  <h3>Items List:</h3>
  {#if $itemsStore.getters.loading}
    <Loader />
  {:else}
    <ul>
      {#each $itemsStore.getters.items as item, index}
        <ItemComponent
          {item}
          isLast={index === $itemsStore.getters.items.length - 1}
          onselectitem={handleSelectItem}
        />
      {/each}
    </ul>
  {/if}
</div>
```

### Component-local state

For component-local state (not shared between components), use runes:

```svelte
<script lang="ts">
  let count = $state(0)
  let doubled = $derived(count * 2)

  function increment() {
    count++
  }
</script>

<button onclick={increment}>
  Count: {count} (doubled: {doubled})
</button>
```

(See the `src/store` directory next to this markdown for complete examples)