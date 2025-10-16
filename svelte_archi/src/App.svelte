<script lang="ts">
  // import { SampleComp, Counter } from 'my-component-library' // not sure why yet but this gives runtime error "ncaught TypeError: Cannot read properties of undefined (reading '$$')"
  import { SampleComp, Counter } from '../../my-component-library/src/components'

  import {
    randomid
  } from '@largescaleapps/my-js-helpers'

  // import a reference to our ItemsView component
  import ItemsView from '@/views/Items.view.svelte'
  import LocaleSelector from '@/components/shared/LocaleSelector.component.svelte'
  import DebugFormatters from '@/components/shared/DebugFormatters.component.svelte'
  import PrimitivesView from '@/views/Primitives.view.svelte'

  // import a reference to useLocalization
  import { useLocalization } from '@/localization'
  // get what we need from useLocalization:
  const { locales, currentLocale, getUserPreferredLocale, changeLocale, isLoadingLocale, isLocaleLoaded, t } =
    useLocalization()

  // on load, check if locale has been set. If not invoke changeLocale
  $: if (!$isLocaleLoaded) {
    changeLocale(getUserPreferredLocale())
  }

  // an event handler from changing the locale from our locale-selector
  const onLocaleClick = (lcid: string) => {
    changeLocale(lcid)
  }

  //
  //    <SampleComp text="I ama sample comp instance from my-component-library" />
</script>

<main>
  <div class="home m-2 p-2 border-2 border-red-500">
    <p>[randomid() result (from my-js-helpers): { randomid() }]</p>
    <SampleComp text={`This is a sample component from my-component-library: ${ randomid() }`} />
    <Counter />

    {#if $isLocaleLoaded && !$isLoadingLocale}
      <LocaleSelector {locales} currentLocale={$currentLocale} {onLocaleClick} t={$t} />
      <h1>{$t('home.welcome')}</h1>
      <ItemsView />
      <PrimitivesView />
      <DebugFormatters show={false} />
    {:else}
      <p>Loading...</p>
    {/if}
  </div>
</main>
