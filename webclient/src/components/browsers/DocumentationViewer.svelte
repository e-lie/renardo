<script>
  import { onMount } from 'svelte';
  
  export let documentContent = '';
  
  // Process links to make them work with the documentation system
  function processLinks(content) {
    // Replace relative markdown links with JavaScript event handlers
    // For example: [Link Text](./relative/path.md) becomes <a href="javascript:void(0)" data-doc-path="relative/path.md">Link Text</a>
    return content.replace(
      /<a href="([^"]+\.md)(?:#([^"]+))?">(.*?)<\/a>/g, 
      (match, path, anchor, text) => {
        // Handle absolute URLs (leave them as-is)
        if (path.startsWith('http://') || path.startsWith('https://')) {
          return match;
        }
        
        // Convert relative path to absolute
        let docPath = path;
        if (path.startsWith('./')) {
          docPath = path.substring(2);
        }
        
        // Create the custom link with data attributes
        let result = `<a href="javascript:void(0)" data-doc-path="${docPath}"`;
        if (anchor) {
          result += ` data-doc-anchor="${anchor}"`;
        }
        result += `>${text}</a>`;
        
        return result;
      }
    );
  }
  
  // Handle link clicks to load new documentation files
  function handleDocLinkClick(event) {
    const target = event.target.closest('a[data-doc-path]');
    if (!target) return;
    
    event.preventDefault();
    
    const docPath = target.getAttribute('data-doc-path');
    const docAnchor = target.getAttribute('data-doc-anchor');
    
    // Dispatch event to parent component to load the new document
    const customEvent = new CustomEvent('doclink', {
      detail: { path: docPath, anchor: docAnchor }
    });
    document.dispatchEvent(customEvent);
  }
  
  // Initialize event handlers
  onMount(() => {
    document.addEventListener('click', handleDocLinkClick);
    
    return () => {
      document.removeEventListener('click', handleDocLinkClick);
    };
  });
  
  // Process the content whenever it changes
  $: processedContent = processLinks(documentContent);
</script>

<div class="documentation-viewer prose prose-sm max-w-none dark:prose-invert">
  {@html processedContent}
</div>

<style>
  .documentation-viewer {
    padding: 1rem;
    overflow-y: auto;
    height: 100%;
  }
  
  .documentation-viewer :global(h1) {
    font-size: 1.8rem;
    margin-top: 0;
    margin-bottom: 1rem;
    font-weight: 600;
  }
  
  .documentation-viewer :global(h2) {
    font-size: 1.5rem;
    margin-top: 1.5rem;
    margin-bottom: 0.75rem;
    font-weight: 600;
  }
  
  .documentation-viewer :global(h3) {
    font-size: 1.25rem;
    margin-top: 1.25rem;
    margin-bottom: 0.5rem;
    font-weight: 600;
  }
  
  .documentation-viewer :global(p) {
    margin-bottom: 1rem;
  }
  
  .documentation-viewer :global(ul), 
  .documentation-viewer :global(ol) {
    margin-bottom: 1rem;
    padding-left: 1.5rem;
  }
  
  .documentation-viewer :global(li) {
    margin-bottom: 0.25rem;
  }
  
  .documentation-viewer :global(a) {
    color: #4299e1;
    text-decoration: none;
  }
  
  .documentation-viewer :global(a:hover) {
    text-decoration: underline;
  }
  
  .documentation-viewer :global(code) {
    background-color: rgba(0,0,0,0.05);
    padding: 0.2em 0.4em;
    border-radius: 3px;
    font-family: monospace;
    font-size: 0.9em;
  }
  
  .documentation-viewer :global(pre) {
    background-color: rgba(0,0,0,0.05);
    padding: 1rem;
    border-radius: 4px;
    overflow-x: auto;
    margin-bottom: 1rem;
  }
  
  .documentation-viewer :global(pre code) {
    background-color: transparent;
    padding: 0;
    font-size: 0.9em;
  }
  
  .documentation-viewer :global(blockquote) {
    border-left: 4px solid #e2e8f0;
    padding-left: 1rem;
    color: #718096;
    margin-left: 0;
    margin-right: 0;
  }
  
  .documentation-viewer :global(hr) {
    border: 0;
    border-top: 1px solid #e2e8f0;
    margin: 1.5rem 0;
  }
  
  .documentation-viewer :global(table) {
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 1rem;
  }
  
  .documentation-viewer :global(th), 
  .documentation-viewer :global(td) {
    border: 1px solid #e2e8f0;
    padding: 0.5rem;
    text-align: left;
  }
  
  .documentation-viewer :global(th) {
    background-color: rgba(0,0,0,0.05);
  }
</style>