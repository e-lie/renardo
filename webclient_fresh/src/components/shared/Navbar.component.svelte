<script lang="ts">
  import { ElButton } from '../primitives'
  import { currentPage } from '../../store/root/Root.store'

  function navigateTo(page: 'posts' | 'authors' | 'editor' | 'logs') {
    currentPage.set(page)
  }
</script>

<div class="navbar bg-base-300">
  <div class="flex-1">
    <a class="btn btn-ghost text-xl">Renardo Blog</a>
  </div>
  <div class="flex-none">
    <ul class="menu menu-horizontal px-1">
      <li>
        <ElButton variant="ghost" onclick={() => navigateTo('posts')}>
          Posts
        </ElButton>
      </li>
      <li>
        <ElButton variant="ghost" onclick={() => navigateTo('authors')}>
          Authors
        </ElButton>
      </li>
      <li>
        <ElButton variant="ghost" onclick={() => navigateTo('editor')}>
          Editor
        </ElButton>
      </li>
      <li>
        <ElButton variant="ghost" onclick={() => navigateTo('logs')}>
          Logs
        </ElButton>
      </li>
    </ul>
  </div>
</div>
