<script lang="ts">
  // import createEventDispatcher from Svelte:
  import { createEventDispatcher } from 'svelte'
  import { buttonCssStrategy } from './ButtonCssStrategy'

  // expose a property called testid
  export let testid: string = 'not-set'
  // expose a property called id
  export let id: string = 'not-set'
  // expose a property called label
  export let label: string = 'label-not-set'
  // expose a property called disabled
  export let disabled = false
  // expose a property called addCss
  export let addCss: string = ''

  // the button type (primary, secondary, danger etc)
  export let buttonType = 'primary'

  // create an instance of Svelte event dispatcher
  const dispatch = createEventDispatcher()

  // a computed property to return a different css class based on the selected value
  $: cssClass = (): string => {
    const result = [
      'font-bold py-1 px-2 inline-flex justify-center rounded-md border shadow-sm focus:outline-none focus:ring-2 focus:ring-offset-2'
    ]
    if (disabled) {
      // these are the button CSS classes when disabled
      result.push('bg-gray-500 text-gray-300 opacity-50 cursor-not-allowed')
    } else {
      // these are the button CSS classes when enabled
      result.push(buttonCssStrategy.get(buttonType))
    }

    // addCss will have additional CSS classes
    // we want to apply from where we consume this component
    if ((addCss || '').trim().length > 0) {
      result.push(addCss.trim())
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
  aria-label={label}
  data-testid={testid}
  {disabled}
  class={cssClass()}
  on:click={() => handleClick()}
>
  <span class="name">{label}</span>
</button>
