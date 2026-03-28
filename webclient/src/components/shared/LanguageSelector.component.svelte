<script lang="ts">
  import { useI18nStore } from '../../store/i18n/I18n.store'
  import type { Language } from '../../i18n/translations'

  const { getters, actions } = useI18nStore()
  const { currentLanguage, translate } = getters

  const languages: { code: Language; name: string; flag: string }[] = [
    { code: 'en', name: 'English', flag: '🇬🇧' },
    { code: 'fr', name: 'Français', flag: '🇫🇷' },
    { code: 'es', name: 'Español', flag: '🇪🇸' },
    { code: 'de', name: 'Deutsch', flag: '🇩🇪' }
  ]

  function handleLanguageChange(lang: Language) {
    actions.setLanguage(lang)
  }
</script>

<div class="space-y-3">
  <h3 class="h3">{$translate('language')}</h3>
  <div class="grid grid-cols-2 gap-2">
    {#each languages as lang}
      <button
        class="btn variant-ghost-surface {$currentLanguage === lang.code ? 'variant-filled-primary' : ''}"
        onclick={() => handleLanguageChange(lang.code)}
      >
        <span class="mr-2">{lang.flag}</span>
        <span>{lang.name}</span>
      </button>
    {/each}
  </div>
</div>
