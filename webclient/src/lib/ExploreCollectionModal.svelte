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
  let currentView = 'banks'; // 'banks', 'sections', 'categories', 'resources', 'resource_detail'
  let selectedBank = null;
  let selectedSection = null;
  let selectedCategory = null;
  let selectedResource = null;
  let resourceContent = null;
  let isLoadingResource = false;
  
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
      
      // Initialize navigation with banks
      banks = structure.banks || [];
      console.log('Banks:', banks);
      
      // Skip banks view - directly go to sections view using the first bank
      if (banks.length > 0) {
        selectedBank = banks[0];
        console.log('Auto-selecting bank:', selectedBank);
        
        // Create sections from the selected bank
        sections = [
          { id: 'instruments', name: 'Instruments', items: selectedBank.instruments || [] },
          { id: 'effects', name: 'Effects', items: selectedBank.effects || [] }
        ];
        
        console.log('Sections created:', sections);
        currentView = 'sections';
        currentPath = [structure.name, selectedBank.name];
      } else {
        // If no banks are available, still stay at the banks view
        currentView = 'banks';
        currentPath = [structure.name];
      }
      
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
  
  // Function to load and view resource details
  async function navigateToResource(resource) {
    selectedResource = resource;
    resourceContent = null;
    isLoadingResource = true;
    currentView = 'resource_detail';
    currentPath = [...currentPath, resource.name];
    
    try {
      // Fetch the resource content
      console.log(`Fetching resource details for ${resource.name}`);
      const response = await fetch(`/api/collections/${collectionType}/${collectionName}/resource/${selectedCategory.name}/${resource.name}`);
      
      if (!response.ok) {
        throw new Error(`Failed to fetch resource: ${response.status} ${response.statusText}`);
      }
      
      const data = await response.json();
      console.log('Resource data:', data);
      
      if (!data.success) {
        throw new Error(data.message || 'Failed to fetch resource');
      }
      
      resourceContent = data;
    } catch (err) {
      console.error('Error loading resource:', err);
      error = err.message;
    } finally {
      isLoadingResource = false;
    }
  }
  
  function navigateBack() {
    if (currentView === 'resource_detail') {
      // Go back to resources list
      currentView = 'resources';
      selectedResource = null;
      resourceContent = null;
      currentPath.pop();
    } else if (currentView === 'resources') {
      // Go back to categories
      currentView = 'categories';
      currentPath.pop();
    } else if (currentView === 'categories') {
      // Go back to sections
      currentView = 'sections';
      currentPath.pop();
    } else if (currentView === 'sections') {
      // Instead of going back to banks, just close the modal
      onClose();
    } else {
      // Close the modal if we're at the top level
      onClose();
    }
  }
  
  function navigateTo(index) {
    // Navigate to a specific level by clicking on the breadcrumb
    if (index === 0) {
      // Collection name clicked - keep at sections view
      // We don't show banks view anymore
      currentView = 'sections';
      selectedSection = null;
      selectedCategory = null;
      selectedResource = null;
      resourceContent = null;
      currentPath = currentPath.slice(0, 2);
    } else if (index === 1 && currentPath.length > 1) {
      // Bank level - show sections
      currentView = 'sections';
      selectedSection = null;
      selectedCategory = null;
      selectedResource = null;
      resourceContent = null;
      currentPath = currentPath.slice(0, 2);
    } else if (index === 2 && currentPath.length > 2) {
      // Section level - show categories
      currentView = 'categories';
      selectedCategory = null;
      selectedResource = null;
      resourceContent = null;
      currentPath = currentPath.slice(0, 3);
    } else if (index === 3 && currentPath.length > 3) {
      // Category level - show resources
      currentView = 'resources';
      selectedResource = null;
      resourceContent = null;
      currentPath = currentPath.slice(0, 4);
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
                <button 
                  type="button"
                  class="card bg-base-100 shadow-md hover:shadow-lg transition-shadow cursor-pointer text-left"
                  on:click={() => navigateToResource(resource)}
                  on:keydown={(e) => e.key === 'Enter' && navigateToResource(resource)}
                >
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
                </button>
              {/each}
              
              {#if resources.length === 0}
                <div class="col-span-3 text-center py-12 text-base-content/50 italic">
                  No resources available in this category.
                </div>
              {/if}
            </div>
          {/if}
          
          <!-- Resource Detail View -->
          {#if currentView === 'resource_detail'}
            <div class="p-4">
              {#if isLoadingResource}
                <div class="flex justify-center py-12">
                  <span class="loading loading-spinner loading-lg text-primary"></span>
                </div>
              {:else if resourceContent}
                <div class="card bg-base-100 shadow-md">
                  <div class="card-body">
                    <div class="flex justify-between items-center mb-4">
                      <h3 class="card-title text-xl">
                        {selectedResource.name}
                        <div class="badge badge-secondary ml-2">
                          {selectedResource.type || 'resource'}
                        </div>
                      </h3>
                    </div>

                    {#if resourceContent.content}
                      <div class="divider">File Content</div>
                      <div class="mockup-code bg-base-300 text-base-content overflow-x-auto max-h-96">
                        <pre data-prefix=""><code>{resourceContent.content}</code></pre>
                      </div>
                    {/if}

                    {#if resourceContent.metadata}
                      <div class="divider">Metadata</div>
                      <div class="overflow-x-auto">
                        <table class="table table-sm">
                          <tbody>
                            {#each Object.entries(resourceContent.metadata) as [key, value]}
                              <tr>
                                <td class="font-semibold">{key}</td>
                                <td>{typeof value === 'object' ? JSON.stringify(value) : value}</td>
                              </tr>
                            {/each}
                          </tbody>
                        </table>
                      </div>
                    {/if}
                  </div>
                </div>
              {:else}
                <div class="alert alert-warning">
                  <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>
                  <span>Failed to load resource details.</span>
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
            {currentView === 'banks' || currentView === 'sections' ? 'Close' : 'Back'}
          </button>
        </div>
      {/if}
    </div>
  </div>
{/if}