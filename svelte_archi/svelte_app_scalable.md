
# This document is a app design guideline for svelte app

the partial result it refers to is inside `./src` next to this file 

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

`ElText.svelte` :

```svelte
<script lang="ts">
  // expose a property called testid
  export let testid: string = 'not-set'
  // expose a property called testid
  export let id: string = 'id-not-set'
  // expose a property called tag
  export let tag: string = 'span'
  // expose a property called text
  export let text: string = 'text-not-set'
  // expose a property called addCss
  export let addCss: string = ''

  // a computed property that returns the css class value
  $: cssClass = (): string => {
    const cssClasses = ['p-1']
    if ((addCss || '').trim().length > 0) {
      cssClasses.push(addCss.trim())
    }
    return cssClasses.join(' ').trim()
  }

  const render = () => {
    return `<${tag} id="${id}"" data-testid="${testid}" class="${cssClass()}">${text}</${tag}>`
  }
</script>

{@html render()}
```

• src/components/primitives/modals
• src/components/primitives/inputs
• src/components/primitives/icons
• src/components/primitives/toggles

`ElToggle.svelte` :

```svelte
<script lang="ts">
  // import createEventDispatcher from Svelte:
  import { createEventDispatcher } from 'svelte'

  // expose a property called testid
  export let testid: string = 'not-set'
  // expose a property called id
  export let id: string = 'not-set'
  // expose a property called checked
  export let checked = false
  // expose a property called disabled
  export let disabled = false
  // expose a property called addCss
  export let addCss: string = ''

  // create an instance of Svelte event dispatcher
  const dispatch = createEventDispatcher()

  // a computed property that returns the css class of the outer element
  $: cssClass = (): string => {
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
  }

  $: innerCssClass = (): string => {
    const result = [
      'bg-white shadow pointer-events-none inline-block h-6 w-6 rounded-full transform ring-0 transition duration-200'
    ]
    if (checked) {
      result.push('translate-x-6')
    } else {
      result.push('translate-x-0')
    }
    return result.join(' ').trim()
  }

  // click handler
  const handleClick = () => {
    // proceed only if the button is not disabled, otherwise ignore the click
    if (!disabled) {
      // dispatch a 'clicked' even through Svelte dispatch
      dispatch('clicked', {
        id
      })
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
  on:click={() => handleClick()}
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
// a computed property to return a different css class based on the selected value
$: cssClass = (): string => {
// here we concatenate the default CSS with 'disabled' only if disabled is true
const defaultClasses = 'p-6' // in TailwindCSS this means we want a padding of 6
return `${ defaultClasses } ${ this.disabled ? 'disabled' : '' }`.trim()
// alternativately you could use an array that is initialized with
// the default CSS, and if disabled is true, then add 'disabled'
// and return the result by joining the array with space as the separator
// (I usually feavor this approach especially when there
// is more than one check and additional logic)
const cssClasses = ['p-6']
if (this.disabled) {
cssClasses.push('disabled')
}
return cssClasses.join(' ')
}
</script>
<button type="button" class={cssClass()}>
<span class="name">{ label }</span>
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
  // import createEventDispatcher from Svelte:
  import { createEventDispatcher } from 'svelte'
  // import a reference to our ItemInterace
  import type { ItemInterface } from '@/models'
  // add the following two lines:
  import ElText from '../../primitives/text/ElText.svelte'
  import ElToggle from '../../primitives/toggles/ElToggle.svelte'

  // expose a property called testid
  export let testid: string = 'not-set'
  // expose a property called isLast
  export let isLast: boolean = false
  // expose a property called item
  export let item: ItemInterface = {
    id: -1,
    name: '',
    selected: false
  }

  // create an instance of Svelte event dispatcher
  const dispatch = createEventDispatcher()

  // a computed property to return a different css class based on the selected value
  $: cssClass = (): string => {
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
  }

  // item click handler
  function handleClick(item: ItemInterface) {
    // dispatch a 'selectItem' even through Svelte dispatch
    dispatch('selectItem', {
      item
    })
  }
</script>

<li role="button" data-testid={testid} class={cssClass()} on:click={() => handleClick(item)}>
  <ElText testid={`${testid}-text`} tag="div" text={item.name} />
  <ElToggle testid={`${testid}-toggle`} checked={item.selected} />
</li>
```

Et puis `src/components/items/children/Item.component.svelte`

```svelte
<script lang="ts">
  // import localization
  import { useLocalization } from '../../localization'
  // import a reference to our ItemInterace
  import type { ItemInterface } from '../../models/items/Item.interface'
  // import a reference to our Item component
  import ItemComponent from './children/Item.component.svelte'
  // import a reference to our Loader component:
  import Loader from '../shared/Loader.component.svelte'

  // expose loading property:
  export let loading = false
  // expose a property called items with a default value of a blank array
  export let items: ItemInterface[] = []
  // expose a property to pass our selectItem event to the parent component
  export let selectItem: (event: CustomEvent<{ item: ItemInterface }>) => void

  // private
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
          on:selectItem={selectItem}
        />
      {/each}
    </ul>
  {/if}
</div>
```

## i18n

look at `./src` example

## State management

One of the most important part of an app that will grow large is to decided how to manage
its state.
For many years in MV* frameworks like React²⁰ or Vue²¹ etc. that meant using a state
manager that usually implemented the Flux²² State Management pattern.

Flux offers an architectural pattern that is a slight modification of the observer-observable
pattern and it is not a library or a framework.
Single source of truth:
The most important reason to implement a centralized state manager is to have a “single
source of truth” for the application state/data. This simply means that our application state
has only one global, centralized source. The responsibility of changing that state is only in
the hand of our state manager. That means you can expect a consistent behavior in your app
as the source of your data cannot be changed outside the state manager.

One thing I learned from my past experience using React, Angular, Vue.js, Svelte, and more,
is that there are some advantages adopting a certain flow that is closer to Flux, but does not
have to follow it to the letter. We definitely won’t need this in every component, as in some
cases using just local state is the right thing to do. But we’ll need it for global state changes
on which many components within the same app will depend on.


Let’s try to implement a state manager that follow more or less this pattern:
• we will invoke an action on our state manager from a component
• the state manager will perform some tasks within that action
• the state manager will commit a change to our state
• the state manager will be organized into modules (each module will represent a
odmain/area of the application. I.e. items, authors, companies, projects, products,
categories, etc)

(to agent : look at the `src` dir next to this markdown for example)