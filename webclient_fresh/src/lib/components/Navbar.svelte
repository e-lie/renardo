<script lang="ts">
  import { currentPage, selectedPost } from '../stores'

  function navigateTo(page: string) {
    currentPage.set(page)
    if (page !== 'post-detail') {
      selectedPost.set(null)
    }
  }
</script>

<div class="navbar bg-primary text-primary-content">
  <div class="navbar-start">
    <div class="dropdown">
      <div tabindex="0" role="button" class="btn btn-ghost lg:hidden">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
        </svg>
      </div>
      <ul class="menu menu-sm dropdown-content mt-3 z-[1] p-2 shadow bg-base-100 rounded-box w-52">
        <li><button class="text-base-content" on:click={() => navigateTo('posts')}>Posts</button></li>
        <li><button class="text-base-content" on:click={() => navigateTo('authors')}>Authors</button></li>
        <li><button class="text-base-content" on:click={() => navigateTo('editor')}>Code Editor</button></li>
      </ul>
    </div>
    <button class="btn btn-ghost text-xl" on:click={() => navigateTo('posts')}>Renardo Blog</button>
  </div>
  <div class="navbar-center hidden lg:flex">
    <ul class="menu menu-horizontal px-1">
      <li><button on:click={() => navigateTo('posts')}>Posts</button></li>
      <li><button on:click={() => navigateTo('authors')}>Authors</button></li>
      <li><button on:click={() => navigateTo('editor')}>Code Editor</button></li>
    </ul>
  </div>
  <div class="navbar-end">
    <div class="flex-none">
      <div class="dropdown dropdown-end">
        <div tabindex="0" role="button" class="btn btn-ghost btn-circle">
          <div class="indicator">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
            </svg>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>