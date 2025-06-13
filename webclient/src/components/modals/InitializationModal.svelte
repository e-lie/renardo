<script>
  import { fade } from 'svelte/transition';
  import { createEventDispatcher } from 'svelte';
  
  export let show = false;
  export let initStatus = {
    sclangCode: false,
    samples: false,
    instruments: false,
    reaperPack: false
  };
  
  const dispatch = createEventDispatcher();
  
  function dismiss() {
    dispatch('dismiss');
  }
  
  function goToInit() {
    dispatch('goToInit');
  }
</script>

{#if show}
  <div class="modal modal-open" transition:fade={{ duration: 200 }}>
    <div class="modal-box">
      <h3 class="font-bold text-lg mb-4">Setup Required</h3>
      <div class="flex flex-col items-center mb-6">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 text-warning mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <p class="text-center mb-4">Some initialization steps are not complete.</p>
        
        <div class="w-full space-y-2 mb-4">
          
          <div class="flex items-center">
            <div class="w-6 h-6 mr-2">
              {#if initStatus.sclangCode}
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-success" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              {:else}
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-error" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              {/if}
            </div>
            <span class="{initStatus.sclangCode ? 'text-success' : 'text-error'}">SCLang Code</span>
          </div>
          
          <div class="flex items-center">
            <div class="w-6 h-6 mr-2">
              {#if initStatus.samples}
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-success" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              {:else}
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-error" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              {/if}
            </div>
            <span class="{initStatus.samples ? 'text-success' : 'text-error'}">Sample Packs</span>
          </div>
          
          <div class="flex items-center">
            <div class="w-6 h-6 mr-2">
              {#if initStatus.instruments}
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-success" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              {:else}
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-error" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              {/if}
            </div>
            <span class="{initStatus.instruments ? 'text-success' : 'text-error'}">Instruments & Effects</span>
          </div>
          
          <div class="flex items-center">
            <div class="w-6 h-6 mr-2">
              {#if initStatus.reaperPack}
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-success" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              {:else}
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-error" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              {/if}
            </div>
            <span class="{initStatus.reaperPack ? 'text-success' : 'text-error'}">Reaper Resources</span>
          </div>
        </div>
        
        <p class="text-center text-sm opacity-75">Complete the initialization steps to ensure Renardo works properly.</p>
      </div>
      <div class="flex flex-col gap-2">
        <button class="btn btn-primary" on:click={goToInit}>Go to Initialize Page</button>
        <button class="btn btn-outline" on:click={dismiss}>Continue Anyway</button>
      </div>
    </div>
  </div>
{/if}