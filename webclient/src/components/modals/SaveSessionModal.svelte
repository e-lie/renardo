<script>
  import { fade } from 'svelte/transition';
  import { createEventDispatcher, onMount } from 'svelte';
  
  export let show = false;
  export let saving = false;
  
  const dispatch = createEventDispatcher();
  
  let sessionName = '';
  let inputElement;
  let wasShown = false;
  
  function handleSave() {
    if (sessionName.trim()) {
      dispatch('save', { name: sessionName });
    }
  }
  
  function handleCancel() {
    sessionName = '';
    dispatch('cancel');
  }
  
  function handleKeydown(e) {
    if (e.key === 'Enter' && sessionName.trim()) {
      handleSave();
    } else if (e.key === 'Escape') {
      handleCancel();
    }
  }
  
  // Focus input when modal opens (only clear input on first open)
  $: if (show && inputElement) {
    if (!wasShown) {
      sessionName = '';
      wasShown = true;
    }
    setTimeout(() => inputElement?.focus(), 100);
  }
  
  // Reset wasShown when modal closes
  $: if (!show) {
    wasShown = false;
  }
</script>

{#if show}
  <div class="modal modal-open" transition:fade={{ duration: 200 }}>
    <div class="modal-box">
      <h3 class="font-bold text-lg mb-4">Save Session</h3>
      
      <div class="form-control">
        <label for="session-name-input" class="label">
          <span class="label-text">Session Name</span>
        </label>
        <input 
          id="session-name-input"
          type="text" 
          placeholder="my_session.py" 
          class="input input-bordered w-full"
          bind:value={sessionName}
          bind:this={inputElement}
          on:keydown={handleKeydown}
          disabled={saving}
        />
        <label for="session-name-input" class="label">
          <span class="label-text-alt">The .py extension will be added automatically if not provided</span>
        </label>
      </div>
      
      <div class="modal-action">
        <button 
          class="btn btn-primary"
          on:click={handleSave}
          disabled={!sessionName.trim() || saving}
        >
          {#if saving}
            <span class="loading loading-spinner loading-sm"></span>
            Saving...
          {:else}
            Save
          {/if}
        </button>
        <button 
          class="btn btn-outline"
          on:click={handleCancel}
          disabled={saving}
        >
          Cancel
        </button>
      </div>
    </div>
  </div>
{/if}