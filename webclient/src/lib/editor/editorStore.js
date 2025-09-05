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

export async function saveSessionToServer(sessionName) {
  try {
    const success = await tabManager.saveSession(sessionName);
    
    if (success) {
      sendDebugLog('INFO', 'Session saved to server', {
        sessionName,
        bufferCount: get(tabManager.buffers).length
      });
    } else {
      sendDebugLog('ERROR', 'Failed to save session to server', {
        sessionName
      });
    }
    
    return success;
  } catch (error) {
    sendDebugLog('ERROR', 'Error saving session to server', {
      sessionName,
      error: error.message
    });
    return false;
  }
}

export function loadSessionFromContent(content) {
  try {
    tabManager.loadSessionFromContent(content);
    
    sendDebugLog('INFO', 'Session loaded from content', {
      bufferCount: get(tabManager.buffers).length,
      tabCount: get(tabManager.tabs).length
    });
    
    return true;
  } catch (error) {
    sendDebugLog('ERROR', 'Failed to load session from content', {
      error: error.message
    });
    return false;
  }
}

export function exportSessionContent() {
  try {
    const content = tabManager.exportSessionContent();
    
    sendDebugLog('INFO', 'Session content exported', {
      contentLength: content.length,
      bufferCount: get(tabManager.buffers).length
    });
    
    return content;
  } catch (error) {
    sendDebugLog('ERROR', 'Failed to export session content', {
      error: error.message
    });
    return '';
  }
}

export function renameBuffer(bufferId, newName) {
  tabManager.renameBuffer(bufferId, newName);
  
  sendDebugLog('INFO', 'Buffer renamed', {
    bufferId,
    newName
  });
}

export function startEditingTabName(tabId) {
  const state = get(tabManager);
  const tab = state.tabs.get(tabId);
  if (tab) {
    tab.startEditing();
    
    sendDebugLog('INFO', 'Started editing tab name', {
      tabId
    });
  }
}

export function stopEditingTabName(tabId) {
  const state = get(tabManager);
  const tab = state.tabs.get(tabId);
  if (tab) {
    tab.stopEditing();
    
    sendDebugLog('INFO', 'Stopped editing tab name', {
      tabId
    });
  }
}

export function finishEditingTabName(tabId, newName) {
  const state = get(tabManager);
  const tab = state.tabs.get(tabId);
  if (tab) {
    const tabState = tab.getState();
    const buffer = state.buffers.get(tabState.bufferId);
    
    if (buffer && newName.trim()) {
      // Rename the buffer (which will update tab titles)
      tabManager.renameBuffer(tabState.bufferId, newName.trim());
    }
    
    tab.stopEditing();
    
    sendDebugLog('INFO', 'Finished editing tab name', {
      tabId,
      newName: newName.trim()
    });
  }
}

export function createNewSession() {
  // Save current startup buffer content if exists
  const startupBuffer = get(tabManager.startupBuffer);
  let startupContent = '# Renardo startup file\n# This file is loaded when Renardo starts\n# Add your custom code here\n';
  
  if (startupBuffer) {
    startupContent = startupBuffer.getContent();
  }
  
  // Clear all tabs and buffers, then recreate with startup + untitled
  const state = get(tabManager);
  tabManager._state.set({
    buffers: new Map(),
    tabs: new Map(),
    activeTabId: null,
    nextBufferId: 1,
    nextTabId: 1,
    isTabSwitching: false
  });
  
  // Ensure startup tab
  tabManager.ensureStartupTab();
  
  // Set startup content
  const newStartupBuffer = get(tabManager.startupBuffer);
  if (newStartupBuffer) {
    newStartupBuffer.setContent(startupContent);
  }
  
  // Create untitled tab
  const untitledTabId = tabManager.createTab({
    title: 'Untitled',
    content: '',
    source: 'manual'
  });
  
  // Switch to untitled tab
  tabManager.switchToTab(untitledTabId);
  
  sendDebugLog('INFO', 'New session created', {
    startupContentPreserved: startupContent.length > 0
  });
}

// Export for use in components
export default tabManager;