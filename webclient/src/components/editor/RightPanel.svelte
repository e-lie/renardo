<script>
  import { fade } from 'svelte/transition';
  import { createEventDispatcher } from 'svelte';
  import TutorialBrowser from '../browsers/TutorialBrowser.svelte';
  import SessionsManager from '../browsers/SessionsManager.svelte';
  import StartupFilesManager from '../browsers/StartupFilesManager.svelte';
  import MusicExamplesBrowser from '../browsers/MusicExamplesBrowser.svelte';
  import DocumentationViewer from '../browsers/DocumentationViewer.svelte';
  
  export let activeTab = 'tutorial';
  export let width = 384;
  export let open = true;
  
  // Tutorial props
  export let tutorialFiles = [];
  export let loadingTutorials = false;
  export let selectedLanguage = 'en';
  export let availableLanguages = [];
  
  // Sessions props
  export let sessionFiles = [];
  export let loadingSessions = false;
  
  // Startup files props
  export let startupFiles = [];
  export let loadingStartupFiles = false;
  export let selectedStartupFile = null;
  export let currentSessionStartupFile = null;
  
  // Music examples props
  export let musicExampleFiles = [];
  export let loadingMusicExamples = false;
  
  // Documentation props
  export let documentationFiles = [];
  export let loadingDocumentation = false;
  export let currentDocumentationContent = '';
  export let selectedDocumentationFile = null;
  
  const dispatch = createEventDispatcher();
  
  function switchTab(tab) {
    activeTab = tab;
    dispatch('switchTab', { tab });
  }
  
  function close() {
    dispatch('close');
  }
  
  function startResize(e) {
    e.preventDefault();
    dispatch('startResize');
  }
</script>

{#if open}
  <div 
    transition:fade={{ duration: 200 }} 
    class="flex flex-col border-l border-base-300 bg-base-100 transition-all" 
    style="width: {width}px;"
  >
    <!-- Panel header with tabs and close button -->
    <div class="bg-base-300 p-2">
      <div class="flex justify-between items-center mb-2">
        <div class="tabs tabs-boxed">
          <button 
            class="tab {activeTab === 'tutorial' ? 'tab-active' : ''}" 
            on:click={() => switchTab('tutorial')}
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M12.316 3.051a1 1 0 01.633 1.265l-4 12a1 1 0 11-1.898-.632l4-12a1 1 0 011.265-.633zM5.707 6.293a1 1 0 010 1.414L3.414 10l2.293 2.293a1 1 0 11-1.414 1.414l-3-3a1 1 0 010-1.414l3-3a1 1 0 011.414 0zm8.586 0a1 1 0 011.414 0l3 3a1 1 0 010 1.414l-3 3a1 1 0 11-1.414-1.414L16.586 10l-2.293-2.293a1 1 0 010-1.414z" clip-rule="evenodd" />
            </svg>
            Tutorial
          </button>
          <button 
            class="tab {activeTab === 'sessions' ? 'tab-active' : ''}" 
            on:click={() => switchTab('sessions')}
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M4 4a2 2 0 00-2 2v8a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-5L9 2H4z" clip-rule="evenodd" />
            </svg>
            Sessions
          </button>
          <button 
            class="tab {activeTab === 'startupFiles' ? 'tab-active' : ''}" 
            on:click={() => switchTab('startupFiles')}
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M6.267 3.455a3.066 3.066 0 001.745-.723 3.066 3.066 0 013.976 0 3.066 3.066 0 001.745.723 3.066 3.066 0 012.812 2.812c.051.643.304 1.254.723 1.745a3.066 3.066 0 010 3.976 3.066 3.066 0 00-.723 1.745 3.066 3.066 0 01-2.812 2.812 3.066 3.066 0 00-1.745.723 3.066 3.066 0 01-3.976 0 3.066 3.066 0 00-1.745-.723 3.066 3.066 0 01-2.812-2.812 3.066 3.066 0 00-.723-1.745 3.066 3.066 0 010-3.976 3.066 3.066 0 00.723-1.745 3.066 3.066 0 012.812-2.812zm7.44 5.252a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
            </svg>
            Startup Files
          </button>
          <button 
            class="tab {activeTab === 'musicExamples' ? 'tab-active' : ''}" 
            on:click={() => switchTab('musicExamples')}
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" viewBox="0 0 20 20" fill="currentColor">
              <path d="M18 3a1 1 0 00-1.196-.98l-10 2A1 1 0 006 5v9.114A4.369 4.369 0 005 14c-1.657 0-3 .895-3 2s1.343 2 3 2 3-.895 3-2V7.82l8-1.6v5.894A4.37 4.37 0 0015 12c-1.657 0-3 .895-3 2s1.343 2 3 2 3-.895 3-2V3z" />
            </svg>
            Music Examples
          </button>
          <button 
            class="tab {activeTab === 'documentation' ? 'tab-active' : ''}" 
            on:click={() => switchTab('documentation')}
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" viewBox="0 0 20 20" fill="currentColor">
              <path d="M9 4.804A7.968 7.968 0 005.5 4c-1.255 0-2.443.29-3.5.804v10A7.969 7.969 0 015.5 14c1.669 0 3.218.51 4.5 1.385A7.962 7.962 0 0114.5 14c1.255 0 2.443.29 3.5.804v-10A7.968 7.968 0 0014.5 4c-1.255 0-2.443.29-3.5.804V12a1 1 0 11-2 0V4.804z" />
            </svg>
            Documentation
          </button>
        </div>
        <button
          class="btn btn-sm btn-ghost btn-square"
          on:click={close}
          title="Close panel"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
          </svg>
        </button>
      </div>
    </div>

    <!-- Tab content -->
    <div class="flex-1 overflow-y-auto p-4">
      {#if activeTab === 'tutorial'}
        <TutorialBrowser
          {tutorialFiles}
          {loadingTutorials}
          {selectedLanguage}
          {availableLanguages}
          on:changeLanguage
          on:loadFile
        />
      {:else if activeTab === 'sessions'}
        <SessionsManager
          {sessionFiles}
          {loadingSessions}
          on:loadSession
          on:openFolder
        />
      {:else if activeTab === 'startupFiles'}
        <StartupFilesManager
          {startupFiles}
          {loadingStartupFiles}
          {selectedStartupFile}
          {currentSessionStartupFile}
          on:loadFile
          on:createNew
          on:openFolder
          on:setDefault
        />
      {:else if activeTab === 'musicExamples'}
        <MusicExamplesBrowser
          {musicExampleFiles}
          {loadingMusicExamples}
          on:loadFile
          on:reload
        />
      {:else if activeTab === 'documentation'}
        <DocumentationViewer
          {documentationFiles}
          {loadingDocumentation}
          {currentDocumentationContent}
          {selectedDocumentationFile}
          on:loadFile
          on:goHome
        />
      {/if}
    </div>
  </div>
  
  <!-- Resize handle (outside the panel) -->
  <div 
    class="w-1 hover:w-1 cursor-col-resize flex-shrink-0 bg-base-300 hover:bg-primary hover:opacity-50 transition-colors" 
    on:mousedown={startResize}
  ></div>
{/if}