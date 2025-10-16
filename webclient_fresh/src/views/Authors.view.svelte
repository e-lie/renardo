<script lang="ts">
  import AuthorsList from '../components/authors/AuthorsList.component.svelte'
  import { useAppStore } from '../store'

  const { authorsStore } = useAppStore()
  const { loading, authors } = authorsStore.getters

  $effect(() => {
    authorsStore.actions.loadAuthors()
  })
</script>

<div class="container mx-auto px-4 py-8">
  <h1 class="text-4xl font-bold text-center mb-8">Authors</h1>
  <AuthorsList loading={$loading} authors={$authors} />
</div>
