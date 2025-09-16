import { sendMessage, sendDebugLog } from './websocket.js';

export interface EditorPosition {
  line: number;
  ch: number;
}

export interface EditorSelection {
  text: string;
  from: EditorPosition;
  to: EditorPosition;
}

export interface EditorContent {
  text: string;
  from: EditorPosition;
  to: EditorPosition;
}

export interface EditorInstance {
  getSelection?(): EditorSelection | null;
  getCurrentParagraph?(): EditorContent | null;
  getCurrentLine?(): EditorContent | null;
  getAllText?(): EditorContent | null;
}

export type ExecutionType = 'line' | 'paragraph' | 'selection' | 'all';

export type HighlightCallback = (from: EditorPosition, to: EditorPosition, requestId: number) => void;
export type RemoveHighlightCallback = (requestId: number) => void;

export interface CodeExecutionEvent {
  detail?: {
    requestId?: number;
    success?: boolean;
    error?: string;
  };
}

/**
 * Send code to the backend for execution
 * @param codeToExecute - The code to execute
 * @param executionType - Type of execution ('line', 'paragraph', 'selection', 'all')
 * @param from - Start position {line, ch}
 * @param to - End position {line, ch}
 * @param highlightCallback - Optional callback to highlight the executed code
 * @returns requestId - The request ID for tracking
 */
export function sendCodeToExecute(
  codeToExecute: string, 
  executionType: ExecutionType = 'paragraph', 
  from: EditorPosition | null = null, 
  to: EditorPosition | null = null, 
  highlightCallback: HighlightCallback | null = null
): number | null {
  if (!codeToExecute || !codeToExecute.trim()) {
    sendDebugLog('WARNING', 'Empty code execution attempted');
    return null;
  }

  const requestId = Date.now();

  // Log the execution
  sendDebugLog('INFO', `Executing code: ${codeToExecute.substring(0, 50)}${codeToExecute.length > 50 ? '...' : ''}`, {
    executionType,
    codeLength: codeToExecute.length,
    from,
    to,
    requestId
  });

  // Highlight the code if callback provided
  if (from && to && highlightCallback) {
    highlightCallback(from, to, requestId);
  }

  // Send the code to backend for execution
  sendMessage({
    type: 'execute_code',
    data: {
      code: codeToExecute,
      requestId: requestId
    }
  });

  return requestId;
}

/**
 * Execute code based on editor state (selection or paragraph)
 * @param editor - The editor instance with getSelection() and getCurrentParagraph() methods
 * @param highlightCallback - Optional callback to highlight the executed code
 */
export function executeCode(editor: EditorInstance, highlightCallback: HighlightCallback | null = null): void {
  if (!editor) {
    console.error("Editor not initialized!");
    sendDebugLog('ERROR', 'Code execution failed: Editor not initialized');
    return;
  }
  
  let codeToExecute: string;
  let executionType: ExecutionType;
  let from: EditorPosition, to: EditorPosition;
  
  // Check for selection first
  const selection = editor.getSelection ? editor.getSelection() : null;
  if (selection && selection.text) {
    codeToExecute = selection.text;
    executionType = 'selection';
    from = selection.from;
    to = selection.to;
  } else {
    // Fall back to paragraph
    const paragraph = editor.getCurrentParagraph ? editor.getCurrentParagraph() : null;
    if (paragraph) {
      codeToExecute = paragraph.text;
      executionType = 'paragraph';
      from = paragraph.from;
      to = paragraph.to;
    } else {
      return;
    }
  }
  
  if (codeToExecute) {
    sendCodeToExecute(codeToExecute, executionType, from, to, highlightCallback);
  }
}

/**
 * Execute the current line where cursor is positioned
 * @param editor - The editor instance with getCurrentLine() method
 * @param highlightCallback - Optional callback to highlight the executed code
 */
export function executeCurrentLine(editor: EditorInstance, highlightCallback: HighlightCallback | null = null): void {
  if (!editor) {
    console.error("Editor not initialized!");
    sendDebugLog('ERROR', 'Line execution failed: Editor not initialized');
    return;
  }
  
  const line = editor.getCurrentLine ? editor.getCurrentLine() : null;
  if (line && line.text) {
    sendCodeToExecute(line.text, 'line', line.from, line.to, highlightCallback);
  } else {
    sendDebugLog('WARNING', 'No line to execute');
  }
}

/**
 * Execute all code in the editor
 * @param editor - The editor instance with getAllText() method
 * @param highlightCallback - Optional callback to highlight the executed code
 */
export function executeAllCode(editor: EditorInstance, highlightCallback: HighlightCallback | null = null): void {
  if (!editor) {
    console.error("Editor not initialized!");
    sendDebugLog('ERROR', 'Execute all failed: Editor not initialized');
    return;
  }
  
  const allText = editor.getAllText ? editor.getAllText() : null;
  if (allText && allText.text) {
    sendCodeToExecute(allText.text, 'all', allText.from, allText.to, highlightCallback);
  } else {
    sendDebugLog('WARNING', 'No code to execute');
  }
}

/**
 * Stop all music playback
 */
export function stopMusic(): void {
  sendDebugLog('INFO', 'Stopping all music');
  sendMessage({
    type: 'execute_code',
    data: {
      code: 'Clock.clear()',
      requestId: Date.now()
    }
  });
}

/**
 * Handle code execution completion
 * @param event - The completion event with detail.requestId
 * @param removeHighlightCallback - Optional callback to remove highlight
 */
export function handleCodeExecutionComplete(
  event: CodeExecutionEvent, 
  removeHighlightCallback: RemoveHighlightCallback | null = null
): void {
  const { requestId, success, error } = event.detail || {};
  
  if (removeHighlightCallback && requestId) {
    removeHighlightCallback(requestId);
  }
  
  if (success) {
    sendDebugLog('INFO', 'Code execution completed successfully', { requestId });
  } else if (error) {
    sendDebugLog('ERROR', 'Code execution failed', { requestId, error });
  }
}