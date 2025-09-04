<script>
  import { fade } from 'svelte/transition';
  import { createEventDispatcher } from 'svelte';
  
  export let show = false;
  
  const dispatch = createEventDispatcher();
  
  function handleNewSession() {
    dispatch('newSession');
  }
  
  function handleCancel() {
    dispatch('cancel');
  }
</script>

{#if show}
  <div class="modal modal-open" transition:fade={{ duration: 200 }}>
    <div class="modal-box max-w-lg">
      <h3 class="font-bold text-lg mb-4 text-error">⚠️ Start New Session</h3>
      
      <p class="mb-4">
        <strong>WARNING:</strong> You are about to start a completely new session!
      </p>
      
      <div class="alert alert-error mb-4">
        <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>
        <div>
          <h4 class="font-bold">This action will:</h4>
          <ul class="list-disc list-inside mt-2">
            <li>Close ALL current tabs/buffers</li>
            <li>Delete ALL unsaved work</li>
            <li>Reset to a single startup file</li>
            <li>Clear the current session</li>
          </ul>
        </div>
      </div>
      
      <div class="alert alert-warning mb-4">
        <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
        <span><strong>Make sure to save your current session first!</strong></span>
      </div>
      
      <div class="modal-action">
        <button 
          class="btn btn-error"
          on:click={handleNewSession}
        >
          🗑️ Start New Session (Delete Everything)
        </button>
        <button 
          class="btn btn-outline"
          on:click={handleCancel}
        >
          Cancel (Keep Current Session)
        </button>
      </div>
    </div>
  </div>
{/if}