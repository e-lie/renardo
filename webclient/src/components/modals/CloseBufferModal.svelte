<script>
  import { fade } from 'svelte/transition';
  import { createEventDispatcher } from 'svelte';
  
  export let show = false;
  export let bufferName = '';
  
  const dispatch = createEventDispatcher();
  
  function handleClose() {
    dispatch('close');
  }
  
  function handleCancel() {
    dispatch('cancel');
  }
</script>

{#if show}
  <div class="modal modal-open" transition:fade={{ duration: 200 }}>
    <div class="modal-box">
      <h3 class="font-bold text-lg mb-4">Close Buffer</h3>
      
      <p class="mb-4">
        Are you sure you want to close the buffer "{bufferName}"?
      </p>
      
      <div class="alert alert-warning mb-4">
        <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>
        <span>Any unsaved changes will be lost.</span>
      </div>
      
      <div class="modal-action">
        <button 
          class="btn btn-error"
          on:click={handleClose}
        >
          Close Buffer
        </button>
        <button 
          class="btn btn-outline"
          on:click={handleCancel}
        >
          Cancel
        </button>
      </div>
    </div>
  </div>
{/if}