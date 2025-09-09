<script>
  import { onMount, onDestroy } from 'svelte';
  import { PaneComponent } from '../../lib/newEditor/PaneComponent';
  import { sendDebugLog } from '../../lib/websocket.js';

  // Props
  export let componentId = null;
  export let title = 'Text Area';

  // Component instance
  let component = null;
  let unsubscribe = null;

  // Local state synchronized with global state
  let content = '';
  let placeholder = 'Start typing...';
  let wordCount = 0;
  let charCount = 0;
  let lineCount = 1;
  let showStats = true;
  let fontSize = 14;
  let fontFamily = 'monospace';
  let isMarkdown = false;
  let autoSave = true;
  let lastSaved = null;

  // Font options
  const fontOptions = [
    { value: 'monospace', label: 'Monospace' },
    { value: 'serif', label: 'Serif' },
    { value: 'sans-serif', label: 'Sans-serif' },
    { value: 'Georgia', label: 'Georgia' },
    { value: 'Arial', label: 'Arial' }
  ];

  // Auto-save timer
  let saveTimer = null;

  onMount(() => {
    sendDebugLog('DEBUG', 'TextArea onMount', {
      componentId: componentId,
      title: title
    });

    // Create component instance
    component = new PaneComponent({
      id: componentId,
      type: 'TextArea',
      title: title,
      initialData: {
        content,
        placeholder,
        showStats,
        fontSize,
        fontFamily,
        isMarkdown,
        autoSave,
        lastSaved
      }
    });

    // Subscribe to global state changes
    unsubscribe = component.getGlobalState().subscribe((data) => {
      content = data.content || content;
      placeholder = data.placeholder || placeholder;
      showStats = data.showStats !== undefined ? data.showStats : showStats;
      fontSize = data.fontSize || fontSize;
      fontFamily = data.fontFamily || fontFamily;
      isMarkdown = data.isMarkdown !== undefined ? data.isMarkdown : isMarkdown;
      autoSave = data.autoSave !== undefined ? data.autoSave : autoSave;
      lastSaved = data.lastSaved || lastSaved;
      
      updateStats();
    });

    component.setActive(true);
    updateStats();
  });

  onDestroy(() => {
    if (unsubscribe) {
      unsubscribe();
    }
    if (component) {
      component.setActive(false);
    }
    if (saveTimer) {
      clearTimeout(saveTimer);
    }
  });

  function updateStats() {
    if (typeof content === 'string') {
      charCount = content.length;
      wordCount = content.trim() ? content.trim().split(/\s+/).length : 0;
      lineCount = content.split('\n').length;
    }
  }

  function onContentChange() {
    updateStats();
    
    if (component) {
      component.updateData({
        content,
        wordCount,
        charCount,
        lineCount
      });
    }

    // Auto-save functionality
    if (autoSave) {
      if (saveTimer) {
        clearTimeout(saveTimer);
      }
      saveTimer = setTimeout(() => {
        saveContent();
      }, 1000); // Save after 1 second of inactivity
    }
  }

  function saveContent() {
    lastSaved = new Date().toLocaleTimeString();
    if (component) {
      component.setDataProperty('lastSaved', lastSaved);
    }
  }

  function clearContent() {
    content = '';
    onContentChange();
  }

  function insertTemplate(template) {
    const templates = {
      markdown: '# Heading\n\n**Bold text** and *italic text*\n\n- List item 1\n- List item 2\n\n```javascript\n// Code block\nconsole.log("Hello, world!");\n```',
      todo: '# Todo List\n\n- [ ] Task 1\n- [ ] Task 2\n- [x] Completed task\n\n## Notes\n\nAdd your notes here...',
      meeting: '# Meeting Notes - ' + new Date().toLocaleDateString() + '\n\n## Attendees\n- \n\n## Agenda\n1. \n2. \n\n## Action Items\n- [ ] \n\n## Next Meeting\nDate: \nTime: '
    };
    
    content = templates[template] || '';
    onContentChange();
  }

  function toggleStats() {
    showStats = !showStats;
    if (component) {
      component.setDataProperty('showStats', showStats);
    }
  }

  function toggleMarkdown() {
    isMarkdown = !isMarkdown;
    if (component) {
      component.setDataProperty('isMarkdown', isMarkdown);
    }
  }

  function toggleAutoSave() {
    autoSave = !autoSave;
    if (component) {
      component.setDataProperty('autoSave', autoSave);
    }
  }

  function updateFontSize() {
    if (component) {
      component.setDataProperty('fontSize', fontSize);
    }
  }

  function updateFontFamily() {
    if (component) {
      component.setDataProperty('fontFamily', fontFamily);
    }
  }

  function exportText() {
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `text-export-${new Date().toISOString().split('T')[0]}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }
</script>

<div class="text-area-pane p-4 h-full flex flex-col">
  <!-- Header with controls -->
  <div class="flex items-center justify-between mb-4 flex-shrink-0">
    <h3 class="text-lg font-semibold">Text Area</h3>
    <div class="flex items-center gap-2">
      <div class="dropdown dropdown-end">
        <label tabindex="0" class="btn btn-xs btn-ghost">⚙️</label>
        <div tabindex="0" class="dropdown-content z-[1] menu p-2 shadow bg-base-100 rounded-box w-80">
          <!-- Font Size -->
          <div class="form-control mb-2">
            <label class="label py-1">
              <span class="label-text text-xs">Font Size: {fontSize}px</span>
            </label>
            <input 
              type="range" 
              min="10" 
              max="24" 
              bind:value={fontSize}
              on:input={updateFontSize}
              class="range range-xs"
            />
          </div>
          
          <!-- Font Family -->
          <div class="form-control mb-2">
            <label class="label py-1">
              <span class="label-text text-xs">Font Family</span>
            </label>
            <select 
              bind:value={fontFamily}
              on:change={updateFontFamily}
              class="select select-xs w-full"
            >
              {#each fontOptions as font}
                <option value={font.value}>{font.label}</option>
              {/each}
            </select>
          </div>
          
          <!-- Toggles -->
          <div class="form-control">
            <label class="cursor-pointer label py-1">
              <span class="label-text text-xs">Show Stats</span>
              <input 
                type="checkbox" 
                bind:checked={showStats}
                on:change={toggleStats}
                class="toggle toggle-xs"
              />
            </label>
          </div>
          
          <div class="form-control">
            <label class="cursor-pointer label py-1">
              <span class="label-text text-xs">Markdown Mode</span>
              <input 
                type="checkbox" 
                bind:checked={isMarkdown}
                on:change={toggleMarkdown}
                class="toggle toggle-xs"
              />
            </label>
          </div>
          
          <div class="form-control">
            <label class="cursor-pointer label py-1">
              <span class="label-text text-xs">Auto Save</span>
              <input 
                type="checkbox" 
                bind:checked={autoSave}
                on:change={toggleAutoSave}
                class="toggle toggle-xs"
              />
            </label>
          </div>
        </div>
      </div>
      
      <div class="dropdown dropdown-end">
        <label tabindex="0" class="btn btn-xs btn-ghost">📄</label>
        <ul tabindex="0" class="dropdown-content z-[1] menu p-2 shadow bg-base-100 rounded-box w-52">
          <li><button on:click={() => insertTemplate('markdown')} class="text-xs">Markdown Template</button></li>
          <li><button on:click={() => insertTemplate('todo')} class="text-xs">Todo List</button></li>
          <li><button on:click={() => insertTemplate('meeting')} class="text-xs">Meeting Notes</button></li>
          <li><hr class="my-1" /></li>
          <li><button on:click={exportText} class="text-xs">Export as .txt</button></li>
          <li><button on:click={clearContent} class="text-xs text-error">Clear All</button></li>
        </ul>
      </div>
    </div>
  </div>

  <!-- Main textarea -->
  <div class="flex-1 flex flex-col min-h-0">
    <textarea 
      bind:value={content}
      on:input={onContentChange}
      {placeholder}
      class="textarea textarea-bordered flex-1 resize-none font-mono leading-relaxed"
      style="font-size: {fontSize}px; font-family: {fontFamily};"
      class:markdown-mode={isMarkdown}
    ></textarea>
  </div>

  <!-- Stats footer -->
  {#if showStats}
    <div class="flex justify-between items-center mt-3 pt-2 border-t border-base-300 text-xs text-base-content/70 flex-shrink-0">
      <div class="flex gap-4">
        <span>Words: {wordCount}</span>
        <span>Characters: {charCount}</span>
        <span>Lines: {lineCount}</span>
      </div>
      <div class="flex items-center gap-2">
        {#if autoSave}
          <span class="text-success">●</span>
          <span>Auto-save</span>
        {/if}
        {#if lastSaved}
          <span>Saved: {lastSaved}</span>
        {/if}
      </div>
    </div>
  {/if}
</div>

<style>
  .text-area-pane {
    min-height: 300px;
  }
  
  .textarea {
    font-family: 'SF Mono', 'Monaco', 'Inconsolata', 'Fira Code', 'Fira Mono', 'Droid Sans Mono', 'Consolas', 'DejaVu Sans Mono', monospace;
  }
  
  .markdown-mode {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, sans-serif;
    line-height: 1.6;
  }
  
  .dropdown:focus-within .dropdown-content {
    display: block;
  }
</style>