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
