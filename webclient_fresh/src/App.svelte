<script lang="ts">
  import { setContextClient, createClient, fetchExchange, subscriptionExchange } from '@urql/svelte'
  import { createClient as createWSClient } from 'graphql-ws'
  import { currentPage, selectedPost, currentSession, logModalOpen } from './lib/stores'
  import PostList from './lib/components/PostList.svelte'
  import AuthorList from './lib/components/AuthorList.svelte'
  import PostDetail from './lib/components/PostDetail.svelte'
  import FlokEditor from './lib/components/FlokEditor.svelte'
  import LogModal from './lib/components/LogModal.svelte'
  import Navbar from './lib/components/Navbar.svelte'

  // WebSocket client for subscriptions
  const wsClient = createWSClient({
    url: 'ws://localhost:8000/graphql',
  })

  const client = createClient({
    url: 'http://localhost:8000/graphql',
    exchanges: [
      fetchExchange,
      subscriptionExchange({
        forwardSubscription(operation) {
          return {
            subscribe: (sink) => {
              const dispose = wsClient.subscribe(operation, sink)
              return {
                unsubscribe: dispose,
              }
            },
          }
        },
      }),
    ],
  })

  setContextClient(client)
</script>

<div class="min-h-screen bg-base-100">
  <Navbar />

  {#if $currentPage === 'editor'}
    <!-- Full screen editor -->
    <FlokEditor sessionName={$currentSession} height="calc(100vh - 64px)" />
  {:else}
    <!-- Regular layout for other pages -->
    <main class="container mx-auto px-4 py-8">
      <div class="max-w-6xl mx-auto">
        {#if $currentPage === 'posts'}
          <h1 class="text-4xl font-bold text-center mb-8">Renardo Blog</h1>
          <PostList />
        {:else if $currentPage === 'authors'}
          <h1 class="text-4xl font-bold text-center mb-8">Authors</h1>
          <AuthorList />
        {:else if $currentPage === 'post-detail' && $selectedPost}
          <PostDetail post={$selectedPost} />
        {:else}
          <div class="text-center py-8">
            <h1 class="text-2xl font-bold mb-4">Page not found</h1>
            <button class="btn btn-primary" on:click={() => currentPage.set('posts')}>
              Go to Posts
            </button>
          </div>
        {/if}
      </div>
    </main>
  {/if}

  <!-- Log Modal -->
  <LogModal bind:isOpen={$logModalOpen} />
</div>