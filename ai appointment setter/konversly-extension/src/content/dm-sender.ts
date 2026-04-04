import { onMessage } from '../shared/messaging';

async function sendDM(username: string, message: string): Promise<boolean> {
  try {
    // Navigate to DM thread if not already there
    if (!window.location.pathname.includes('/direct/')) {
      // We should already be on the DM page — the service worker navigates us
    }

    // Find the message input
    const textarea = document.querySelector('textarea[placeholder*="Message"]') ||
                     document.querySelector('[role="textbox"][contenteditable="true"]') ||
                     document.querySelector('[aria-label*="Message"]');

    if (!textarea) {
      console.error('Konversly: Could not find message input');
      return false;
    }

    // Focus the input
    (textarea as HTMLElement).focus();

    // Type the message with human-like delays
    if (textarea.tagName === 'TEXTAREA') {
      // Standard textarea
      const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
        window.HTMLTextAreaElement.prototype, 'value'
      )?.set;
      nativeInputValueSetter?.call(textarea, message);
      textarea.dispatchEvent(new Event('input', { bubbles: true }));
      textarea.dispatchEvent(new Event('change', { bubbles: true }));
    } else {
      // ContentEditable div (Instagram's newer editor)
      (textarea as HTMLElement).textContent = message;
      textarea.dispatchEvent(new InputEvent('input', { bubbles: true, data: message, inputType: 'insertText' }));
    }

    // Wait a moment for Instagram to process
    await new Promise(r => setTimeout(r, 500 + Math.random() * 500));

    // Find and click the Send button
    const sendBtn = document.querySelector('button[type="submit"]') ||
                    document.querySelector('[role="button"][tabindex="0"]');

    // Also try finding by text content
    const allButtons = document.querySelectorAll('button, [role="button"]');
    let sendButton: Element | null = sendBtn;
    allButtons.forEach(btn => {
      if (btn.textContent?.trim().toLowerCase() === 'send') {
        sendButton = btn;
      }
    });

    if (!sendButton) {
      console.error('Konversly: Could not find send button');
      return false;
    }

    (sendButton as HTMLElement).click();

    // Wait for message to be sent
    await new Promise(r => setTimeout(r, 1000 + Math.random() * 1000));

    return true;
  } catch (err) {
    console.error('Konversly: DM send error', err);
    return false;
  }
}

onMessage((message, _sender, sendResponse) => {
  if (message.type === 'SEND_DM') {
    sendDM(message.username, message.message).then(success => {
      sendResponse({ type: 'DM_SENT', username: message.username, success });
    });
    return true;
  }
});
