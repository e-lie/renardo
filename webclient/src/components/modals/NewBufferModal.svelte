<script>
  import { fade } from 'svelte/transition';
  import { createEventDispatcher } from 'svelte';
  
  export let show = false;
  export let creating = false;
  
  const dispatch = createEventDispatcher();
  
  let bufferName = '';
  let inputElement;
  
  function handleCreate() {
    if (bufferName.trim()) {
      dispatch('create', { name: bufferName.trim() });
    }
  }
  
  function handleCancel() {
    bufferName = '';
    dispatch('cancel');
  }
  
  function handleKeydown(e) {
    if (e.key === 'Enter' && bufferName.trim()) {
      handleCreate();
    } else if (e.key === 'Escape') {
      handleCancel();
    }
  }
  
  let previousShow = false;
  
  // Focus input when modal opens
  $: if (show && inputElement && !previousShow) {
    bufferName = '';
    setTimeout(() => inputElement?.focus(), 100);
    previousShow = true;
  } else if (!show) {
    previousShow = false;
  }
</script>

{#if show}
  <div class="modal modal-open" transition:fade={{ duration: 200 }}>
    <div class="modal-box">
      <h3 class="font-bold text-lg mb-4">New Buffer</h3>
      
      <div class="form-control">
        <label for="new-buffer-name-input" class="label">
          <span class="label-text">Buffer Name</span>
        </label>
        <input 
          id="new-buffer-name-input"
          type="text" 
          placeholder="Enter buffer name" 
          class="input input-bordered w-full"
          bind:value={bufferName}
          bind:this={inputElement}
          on:keydown={handleKeydown}
          disabled={creating}
        />
      </div>
      
      <div class="modal-action">
        <button 
          class="btn btn-primary"
          on:click={handleCreate}
          disabled={!bufferName.trim() || creating}
        >
          Create
        </button>
        <button 
          class="btn btn-outline"
          on:click={handleCancel}
          disabled={creating}
        >
          Cancel
        </button>
      </div>
    </div>
  </div>
{/if}