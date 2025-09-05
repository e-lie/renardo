// This is a JavaScript file that uses our TypeScript classes
// Shows how to progressively migrate while keeping JS compatibility

import { TabManager } from './TabManager';
import { get } from 'svelte/store';
import { sendDebugLog } from '../websocket.js';

// Create the global tab manager instance
export const tabManager = new TabManager();

/**
 * Helper functions that wrap TabManager for easier use in Svelte components
 * These can be used in existing JavaScript code without any TypeScript
 */

export function createNewTab(name = 'Untitled', content = '', source = 'manual') {
  sendDebugLog('INFO', 'Creating new tab via TabManager', {
    name,
    contentLength: content.length,
    source
  });
  
  return tabManager.createTab({
    title: name,
    content,
    source
  });
}

export function switchToTab(tabId) {
  sendDebugLog('INFO', 'Switching tab via TabManager', {
    targetTabId: tabId
  });
  
  tabManager.switchToTab(tabId, () => {
    sendDebugLog('INFO', 'Tab switch completed', {
      tabId
    });
  });
}

export function closeTab(tabId) {
  sendDebugLog('INFO', 'Closing tab via TabManager', {
    tabId
  });
  
  const success = tabManager.closeTab(tabId);
  
  if (success) {
    sendDebugLog('INFO', 'Tab closed successfully', {
      tabId
    });
  } else {
    sendDebugLog('WARN', 'Tab close failed', {
      tabId
    });
  }
  
  return success;
}

export function loadContentInTab(name, content, source = 'manual') {
  sendDebugLog('INFO', 'Loading content in tab via TabManager', {
    name,
    contentLength: content.length,
    source
  });
  
  return tabManager.loadContent(name, content, source);
}

export function updateCurrentTabContent(content) {
  if (tabManager.isTabSwitching()) {
    sendDebugLog('DEBUG', 'Skipping content update during tab switch');
    return;
  }
  
  const activeBuffer = get(tabManager.activeBuffer);
  if (activeBuffer) {
    const oldContent = activeBuffer.getContent();
    if (oldContent !== content) {
      sendDebugLog('DEBUG', 'Updating buffer content', {
        bufferId: activeBuffer.getMetadata().id,
        bufferName: activeBuffer.getMetadata().name,
        oldLength: oldContent.length,
        newLength: content.length
      });
      
      tabManager.updateActiveBufferContent(content);
    }
  }
}

export function getActiveTabContent() {
  return tabManager.getActiveBufferContent();
}

export function saveSession() {
  const sessionData = tabManager.toJSON();
  localStorage.setItem('editor-session', JSON.stringify(sessionData));
  
  sendDebugLog('INFO', 'Session saved', {
    bufferCount: sessionData.buffers.length,
    tabCount: sessionData.tabs.length
  });
}

export function loadSession() {
  const saved = localStorage.getItem('editor-session');
  if (saved) {
    try {
      const sessionData = JSON.parse(saved);
      const newManager = TabManager.fromJSON(sessionData);
      
      // Copy state to existing manager
      tabManager._state.set(get(newManager._state));
      
      sendDebugLog('INFO', 'Session loaded', {
        bufferCount: sessionData.buffers.length,
        tabCount: sessionData.tabs.length
      });
      
      return true;
    } catch (error) {
      sendDebugLog('ERROR', 'Failed to load session', {
        error: error.message
      });
      return false;
    }
  }
  return false;
}

// Export for use in components
export default tabManager;