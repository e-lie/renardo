<script lang="ts">
  let {
    testid = 'not-set',
    tag = 'span',
    text = '',
    addCss = ''
  }: {
    testid?: string
    tag?: 'h1' | 'h2' | 'h3' | 'h4' | 'h5' | 'h6' | 'p' | 'span' | 'div'
    text?: string
    addCss?: string
  } = $props()

  const cssClass = $derived(() => {
    const baseClasses: string[] = []

    if (addCss) {
      baseClasses.push(addCss)
    }

    return baseClasses.join(' ')
  })

  const render = $derived(() => {
    return `<${tag} data-testid="${testid}" class="${cssClass()}">${text}</${tag}>`
  })
</script>

{@html render()}
