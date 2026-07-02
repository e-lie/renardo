<script lang="ts">
  import { ElButton } from '../primitives';
  import { currentPage } from '../../store/root/Root.store';

  function navigateTo(page: 'editor') {
    currentPage.set(page);
  }
</script>

<div class="navbar bg-base-300">
  <div class="flex-1">
    <a class="btn btn-ghost text-xl">Renardo</a>
  </div>
  <div class="flex-none">
    <ul class="menu menu-horizontal px-1">
      <li>
        <ElButton variant="ghost" onclick={() => navigateTo('editor')}>Editor</ElButton>
      </li>
    </ul>
  </div>
</div>
