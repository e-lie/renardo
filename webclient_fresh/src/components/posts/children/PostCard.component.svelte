<script lang="ts">
  import type { PostInterface } from '../../../models/posts/Post.interface'
  import { ElCard, ElButton } from '../../primitives'

  let {
    testid = 'not-set',
    post,
    onselect
  }: {
    testid?: string
    post: PostInterface
    onselect?: (post: PostInterface) => void
  } = $props()

  function handleViewDetails() {
    if (onselect) {
      onselect(post)
    }
  }
</script>

<ElCard {testid}>
  <div class="card-body">
    <h2 class="card-title">{post.title}</h2>
    <p class="text-sm text-base-content/60">
      By {post.author.name} • {new Date(post.createdAt).toLocaleDateString()}
    </p>
    <p class="line-clamp-3">{post.content}</p>
    <div class="card-actions justify-end">
      <ElButton variant="primary" onclick={handleViewDetails}>
        Read More
      </ElButton>
    </div>
  </div>
</ElCard>
