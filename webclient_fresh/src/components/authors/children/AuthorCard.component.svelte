<script lang="ts">
  import type { AuthorInterface } from '../../../models/authors/Author.interface'
  import { ElCard } from '../../primitives'

  let {
    testid = 'not-set',
    author
  }: {
    testid?: string
    author: AuthorInterface
  } = $props()
</script>

<ElCard {testid}>
  <div class="card-body">
    <h2 class="card-title">{author.name}</h2>
    <p class="text-sm text-base-content/60">{author.email}</p>
    {#if author.posts && author.posts.length > 0}
      <div class="mt-2">
        <p class="text-sm font-semibold">Recent Posts:</p>
        <ul class="list-disc list-inside text-sm">
          {#each author.posts.slice(0, 3) as post}
            <li>{post.title}</li>
          {/each}
        </ul>
      </div>
    {/if}
    <div class="badge badge-primary">{author.posts?.length || 0} posts</div>
  </div>
</ElCard>
