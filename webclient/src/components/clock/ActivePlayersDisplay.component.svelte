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
  const { actions: editorActions } = appStore.editorStore

  const playingPlayers = $derived(
    $activePlayers
      .filter((p: ActivePlayerInterface) => p.isplaying)
      .map((p: ActivePlayerInterface, index: number) => ({
        ...p,
        // Players registered without a namespace name have a null id; build a
        // stable, unique key so the keyed #each block does not collide on `null`.
        key: p.id != null ? `id:${p.id}` : `idx:${index}`
      }))
  )

  function stopPlayer(id: string) {
    editorActions.executeCode(`${id}.stop()`)
  }
</script>

<div class="h-full flex flex-col bg-surface-100 dark:bg-surface-900 overflow-y-auto p-2">
  {#if playingPlayers.length === 0}
    <div class="h-full flex items-center justify-center text-sm text-surface-500">
      No active players
    </div>
  {:else}
    <ul class="flex flex-col gap-1">
      {#each playingPlayers as player (player.key)}
        <li class="flex items-center justify-between px-2 py-1 rounded bg-surface-200 dark:bg-surface-800">
          <span class="font-mono font-semibold text-primary-500">{player.id ?? '(unnamed)'}</span>
          <span class="text-sm text-surface-500">{player.instrument_name}</span>
          {#if player.id != null}
            <button
              class="btn btn-sm variant-filled-error px-2 py-0.5 text-xs"
              onclick={() => stopPlayer(player.id)}
              title={`Stop ${player.id}`}
            >
              ■ Stop
            </button>
          {/if}
        </li>
      {/each}
    </ul>
  {/if}
</div>
