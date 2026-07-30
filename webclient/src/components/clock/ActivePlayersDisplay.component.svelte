<script lang="ts">
  import { useAppStore } from '../../store/root/Root.store'
  import type { ActivePlayerInterface } from '../../models/websocket'

  let {
    componentId = 'active-players-display',
    title = 'Active Players'
  }: {
    componentId?: string
    title?: string
  } = $props()

  const appStore = useAppStore()
  const { activePlayers } = appStore.webSocketBackendStore.getters

  const playingPlayers = $derived($activePlayers.filter((p: ActivePlayerInterface) => p.isplaying))
</script>

<div class="h-full flex flex-col bg-surface-100 dark:bg-surface-900 overflow-y-auto p-2">
  {#if playingPlayers.length === 0}
    <div class="h-full flex items-center justify-center text-sm text-surface-500">
      No active players
    </div>
  {:else}
    <ul class="flex flex-col gap-1">
      {#each playingPlayers as player (player.id)}
        <li class="flex items-center justify-between px-2 py-1 rounded bg-surface-200 dark:bg-surface-800">
          <span class="font-mono font-semibold text-primary-500">{player.id}</span>
          <span class="text-sm text-surface-500">{player.instrument_name}</span>
        </li>
      {/each}
    </ul>
  {/if}
</div>
