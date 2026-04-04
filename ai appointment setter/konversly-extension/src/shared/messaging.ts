import { MessageType } from './types';

export function sendToBackground(message: MessageType): Promise<unknown> {
  return chrome.runtime.sendMessage(message);
}

export function sendToContentScript(tabId: number, message: MessageType): Promise<unknown> {
  return chrome.tabs.sendMessage(tabId, message);
}

export function onMessage(callback: (message: MessageType, sender: chrome.runtime.MessageSender, sendResponse: (response?: unknown) => void) => void): void {
  chrome.runtime.onMessage.addListener(callback);
}
