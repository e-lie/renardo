<script lang="ts">
  // Svelte 5: use $props() rune instead of export let
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

  // Svelte 5: use $derived rune for computed properties
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

  // Svelte 5: regular function for event handling, call the prop callback
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
