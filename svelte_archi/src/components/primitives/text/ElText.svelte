<script lang="ts">
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
