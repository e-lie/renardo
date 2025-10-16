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
