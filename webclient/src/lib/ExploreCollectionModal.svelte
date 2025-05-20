<script>
  import { onMount } from 'svelte';
  
  // Props
  export let show = false;
  export let collectionType = '';
  export let collectionName = '';
  export let onClose = () => {};
  
  // State
  let isLoading = true;
  let error = null;
  let structure = null;
  let isInstalled = false;
  
  // Navigation state
  let currentPath = [];
  let currentView = 'banks'; // 'banks', 'sections', 'categories', 'resources'
  let selectedBank = null;
  let selectedSection = null;
  let selectedCategory = null;
  
  // Content display state
  let banks = [];
  let sections = [];
  let categories = [];
  let resources = [];
  
  // Load collection structure
  async function loadCollectionStructure() {
    isLoading = true;
    error = null;
    
    try {
      console.log(`Fetching structure for ${collectionType}/${collectionName}`);
      const response = await fetch(`/api/collections/${collectionType}/${collectionName}/structure`);
      
      if (!response.ok) {
        throw new Error(`Failed to fetch collection structure: ${response.status} ${response.statusText}`);
      }
      
      const data = await response.json();
      console.log('Response data:', data);
      
      if (!data.success) {
        throw new Error(data.message || 'Failed to fetch collection structure');
      }
      
      structure = data.structure;
      isInstalled = data.is_installed;
      
      console.log('Structure:', structure);
      
      // Initialize navigation
      banks = structure.banks || [];
      console.log('Banks:', banks);
      currentView = 'banks';
      currentPath = [structure.name];
      
    } catch (err) {
      console.error('Error loading collection structure:', err);
      error = err.message;
    } finally {
      isLoading = false;
    }
  }
  
  // Navigation functions
  function navigateToBank(bank) {
    console.log('Navigating to bank:', bank);
    selectedBank = bank;
    
    // Add detail about what we're finding in the bank data
    console.log(' - Bank instruments:', bank.instruments);
    console.log(' - Bank effects:', bank.effects);
    
    sections = [
      { id: 'instruments', name: 'Instruments', items: bank.instruments || [] },
      { id: 'effects', name: 'Effects', items: bank.effects || [] }
    ];
    
    console.log('Sections created:', sections);
    currentView = 'sections';
    currentPath = [...currentPath, bank.name];
  }
  
  function navigateToSection(section) {
    console.log('Navigating to section:', section);
    selectedSection = section;
    categories = section.items;
    console.log('Categories loaded:', categories);
    currentView = 'categories';
    currentPath = [...currentPath, section.name];
  }
  
  function navigateToCategory(category) {
    selectedCategory = category;
    resources = category.resources || [];
    currentView = 'resources';
    currentPath = [...currentPath, category.name];
  }
  
  function navigateBack() {
    if (currentView === 'resources') {
      // Go back to categories
      currentView = 'categories';
      currentPath.pop();
    } else if (currentView === 'categories') {
      // Go back to sections
      currentView = 'sections';
      currentPath.pop();
    } else if (currentView === 'sections') {
      // Go back to banks
      currentView = 'banks';
      selectedBank = null;
      currentPath.pop();
    } else {
      // Close the modal if we're at the top level
      onClose();
    }
  }
  
  function navigateTo(index) {
    // Navigate to a specific level by clicking on the breadcrumb
    if (index === 0) {
      // Top level - show banks
      currentView = 'banks';
      selectedBank = null;
      selectedSection = null;
      selectedCategory = null;
      currentPath = [currentPath[0]];
    } else if (index === 1 && currentPath.length > 1) {
      // Bank level - show sections
      currentView = 'sections';
      selectedSection = null;
      selectedCategory = null;
      currentPath = currentPath.slice(0, 2);
    } else if (index === 2 && currentPath.length > 2) {
      // Section level - show categories
      currentView = 'categories';
      selectedCategory = null;
      currentPath = currentPath.slice(0, 3);
    }
  }
  
  // When the component is shown or collection changes, load the structure
  $: if (show && collectionType && collectionName) {
    loadCollectionStructure();
  }
</script>

<!-- Modal Overlay -->
{#if show}
  <div class="modal modal-open">
    <div class="modal-box w-11/12 max-w-5xl h-auto max-h-[90vh]">
      <div class="flex justify-between items-center mb-4">
        <h3 class="font-bold text-xl title-font">
          Explore {collectionName}
          {#if isInstalled}
            <div class="badge badge-success ml-2">Installed</div>
          {:else}
            <div class="badge badge-warning ml-2">Not Installed</div>
          {/if}
        </h3>
        
        <button 
          class="btn btn-sm btn-circle btn-ghost"
          on:click={onClose}
        >
          ✕
        </button>
      </div>
      
      <!-- Breadcrumbs Navigation -->
      <div class="text-sm breadcrumbs mb-4">
        <ul>
          {#each currentPath as path, i}
            <li>
              <button 
                type="button"
                on:click={() => navigateTo(i)}
                class={`text-left text-primary underline hover:text-primary-focus ${i === currentPath.length - 1 ? 'font-bold' : ''}`}
              >
                {path}
              </button>
            </li>
          {/each}
        </ul>
      </div>
      
      <!-- Error Display -->
      {#if error}
        <div class="alert alert-error mb-4">
          <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
          <div>
            <div class="font-medium">Error loading collection structure</div>
            <div class="text-sm">{error}</div>
          </div>
        </div>
      {/if}
      
      <!-- Loading Indicator -->
      {#if isLoading}
        <div class="flex justify-center py-12">
          <span class="loading loading-spinner loading-lg text-secondary"></span>
        </div>
      {:else}
        <!-- Content Area -->
        <div class="bg-base-200 rounded-lg p-4 h-[500px] overflow-y-auto">
          
          <!-- Banks View -->
          {#if currentView === 'banks'}
            <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
              {#each banks as bank}
                <button 
                  type="button"
                  class="card bg-base-100 shadow-md hover:shadow-lg transition-shadow cursor-pointer text-left"
                  on:click={() => navigateToBank(bank)}
                  on:keydown={(e) => e.key === 'Enter' && navigateToBank(bank)}
                >
                  <div class="card-body p-4">
                    <h4 class="card-title text-lg">
                      {bank.name}
                    </h4>
                    <div class="flex gap-2 mt-2">
                      <div class="badge badge-outline">
                        {bank.instruments.length} Instrument Categories
                      </div>
                      <div class="badge badge-outline">
                        {bank.effects.length} Effect Categories
                      </div>
                    </div>
                  </div>
                </button>
              {/each}
              
              {#if banks.length === 0}
                <div class="col-span-3 text-center py-12 text-base-content/50 italic">
                  No banks available in this collection.
                </div>
              {/if}
            </div>
          {/if}
          
          <!-- Sections View -->
          {#if currentView === 'sections'}
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {#each sections as section}
                <button 
                  type="button"
                  class="card bg-base-100 shadow-md hover:shadow-lg transition-shadow cursor-pointer text-left"
                  on:click={() => navigateToSection(section)}
                  on:keydown={(e) => e.key === 'Enter' && navigateToSection(section)}
                >
                  <div class="card-body p-4">
                    <h4 class="card-title text-lg">
                      {section.name}
                    </h4>
                    <div class="mt-2">
                      <div class="badge badge-outline">
                        {section.items.length} Categories
                      </div>
                    </div>
                  </div>
                </button>
              {/each}
              
              {#if sections.length === 0}
                <div class="col-span-2 text-center py-12 text-base-content/50 italic">
                  No sections available in this bank.
                </div>
              {/if}
            </div>
          {/if}
          
          <!-- Categories View -->
          {#if currentView === 'categories'}
            <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
              {#each categories as category}
                <button 
                  type="button"
                  class="card bg-base-100 shadow-md hover:shadow-lg transition-shadow cursor-pointer text-left"
                  on:click={() => navigateToCategory(category)}
                  on:keydown={(e) => e.key === 'Enter' && navigateToCategory(category)}
                >
                  <div class="card-body p-4">
                    <h4 class="card-title text-lg">
                      {category.name}
                    </h4>
                    <div class="mt-2">
                      <div class="badge badge-outline">
                        {category.resources ? category.resources.length : 0} Resources
                      </div>
                    </div>
                  </div>
                </button>
              {/each}
              
              {#if categories.length === 0}
                <div class="col-span-3 text-center py-12 text-base-content/50 italic">
                  No categories available in this section.
                </div>
              {/if}
            </div>
          {/if}
          
          <!-- Resources View -->
          {#if currentView === 'resources'}
            <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
              {#each resources as resource}
                <div class="card bg-base-100 shadow-md">
                  <div class="card-body p-4">
                    <h4 class="card-title text-lg">
                      {resource.name}
                    </h4>
                    <div class="mt-2">
                      <div class="badge badge-secondary">
                        {resource.type || 'resource'}
                      </div>
                    </div>
                  </div>
                </div>
              {/each}
              
              {#if resources.length === 0}
                <div class="col-span-3 text-center py-12 text-base-content/50 italic">
                  No resources available in this category.
                </div>
              {/if}
            </div>
          {/if}
          
        </div>
        
        <!-- Navigation Controls -->
        <div class="modal-action">
          <button 
            class="btn btn-outline btn-secondary"
            on:click={navigateBack}
          >
            {currentView === 'banks' ? 'Close' : 'Back'}
          </button>
        </div>
      {/if}
    </div>
  </div>
{/if}