/**
 * ChatGPT Web App Frontend Logic
 */

document.addEventListener('DOMContentLoaded', () => {
  // DOM Elements
  const sidebar = document.getElementById('sidebar');
  const sidebarOverlay = document.getElementById('sidebarOverlay');
  const toggleSidebarBtn = document.getElementById('toggleSidebarBtn');
  const closeSidebarBtn = document.getElementById('closeSidebarBtn');
  const newChatBtn = document.getElementById('newChatBtn');
  const clearChatsBtn = document.getElementById('clearChatsBtn');
  const chatHistoryList = document.getElementById('chatHistoryList');

  const modelSelectorBtn = document.getElementById('modelSelectorBtn');
  const modelMenu = document.getElementById('modelMenu');
  const currentModelLabel = document.getElementById('currentModelLabel');
  const themeToggleBtn = document.getElementById('themeToggleBtn');
  const themeIcon = document.getElementById('themeIcon');

  const welcomeScreen = document.getElementById('welcomeScreen');
  const chatMessagesContainer = document.getElementById('chatMessagesContainer');
  const chatViewport = document.getElementById('chatViewport');

  const userPromptInput = document.getElementById('userPromptInput');
  const sendPromptBtn = document.getElementById('sendPromptBtn');
  const stopGeneratingBtn = document.getElementById('stopGeneratingBtn');

  const openSettingsBtn = document.getElementById('openSettingsBtn');
  const closeSettingsBtn = document.getElementById('closeSettingsBtn');
  const settingsModal = document.getElementById('settingsModal');
  const saveSettingsBtn = document.getElementById('saveSettingsBtn');
  const resetSettingsBtn = document.getElementById('resetSettingsBtn');
  
  const openaiKeyInput = document.getElementById('openaiKeyInput');
  const geminiKeyInput = document.getElementById('geminiKeyInput');
  const personaPresetSelect = document.getElementById('personaPresetSelect');
  const typingSpeedInput = document.getElementById('typingSpeedInput');
  const speedDisplayValue = document.getElementById('speedDisplayValue');

  // Application State
  let conversations = JSON.parse(localStorage.getItem('chatgpt_conversations') || '[]');
  let activeChatId = null;
  let activeModel = 'smart-ai';
  let activeModelName = 'ChatGPT 4.0 Mini (Built-in)';
  let isGenerating = false;
  let currentAbortController = null;

  // Settings State
  let settings = JSON.parse(localStorage.getItem('chatgpt_settings') || JSON.stringify({
    openaiKey: '',
    geminiKey: '',
    personaPreset: 'default',
    typingSpeed: 25,
    theme: 'dark'
  }));

  // Configure Marked.js
  marked.setOptions({
    gfm: true,
    breaks: true,
    highlight: function(code, lang) {
      if (lang && hljs.getLanguage(lang)) {
        try {
          return hljs.highlight(code, { language: lang }).value;
        } catch (e) {}
      }
      return hljs.highlightAuto(code).value;
    }
  });

  // Custom Marked renderer to wrap code blocks with Copy Button
  const renderer = new marked.Renderer();
  renderer.code = function(code, language) {
    const validLang = language || 'code';
    const highlighted = (language && hljs.getLanguage(language))
      ? hljs.highlight(code, { language }).value
      : hljs.highlightAuto(code).value;
    
    return `
      <div class="code-wrapper">
        <div class="code-header">
          <span class="code-lang">${validLang}</span>
          <button class="copy-code-btn" data-code="${encodeURIComponent(code)}">
            <i class="fa-regular fa-copy"></i> Copy code
          </button>
        </div>
        <pre><code class="hljs language-${validLang}">${highlighted}</code></pre>
      </div>
    `;
  };
  marked.use({ renderer });

  // Initialize App
  function init() {
    applySettings();
    renderChatHistory();
    setupEventListeners();

    if (conversations.length > 0) {
      loadChat(conversations[0].id);
    } else {
      showWelcomeScreen();
    }
  }

  // Apply Settings & Theme
  function applySettings() {
    openaiKeyInput.value = settings.openaiKey || '';
    geminiKeyInput.value = settings.geminiKey || '';
    personaPresetSelect.value = settings.personaPreset || 'default';
    typingSpeedInput.value = settings.typingSpeed || 25;
    speedDisplayValue.textContent = `${settings.typingSpeed || 25} ms per token`;

    if (settings.theme === 'light') {
      document.body.classList.add('light-theme');
      themeIcon.className = 'fa-regular fa-sun';
    } else {
      document.body.classList.remove('light-theme');
      themeIcon.className = 'fa-regular fa-moon';
    }
  }

  // Event Listeners
  function setupEventListeners() {
    // Sidebar Toggles
    toggleSidebarBtn.addEventListener('click', () => {
      if (window.innerWidth <= 768) {
        sidebar.classList.toggle('mobile-open');
        sidebarOverlay.classList.toggle('mobile-open');
      } else {
        sidebar.classList.toggle('collapsed');
      }
    });

    closeSidebarBtn?.addEventListener('click', () => {
      sidebar.classList.remove('mobile-open');
      sidebarOverlay.classList.remove('mobile-open');
    });

    sidebarOverlay.addEventListener('click', () => {
      sidebar.classList.remove('mobile-open');
      sidebarOverlay.classList.remove('mobile-open');
    });

    // Theme Toggle
    themeToggleBtn.addEventListener('click', () => {
      if (document.body.classList.contains('light-theme')) {
        document.body.classList.remove('light-theme');
        themeIcon.className = 'fa-regular fa-moon';
        settings.theme = 'dark';
      } else {
        document.body.classList.add('light-theme');
        themeIcon.className = 'fa-regular fa-sun';
        settings.theme = 'light';
      }
      saveSettingsToStorage();
    });

    // Model Selector Dropdown
    modelSelectorBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      modelMenu.classList.toggle('hidden');
    });

    document.addEventListener('click', () => {
      modelMenu.classList.add('hidden');
    });

    document.querySelectorAll('.model-option').forEach(option => {
      option.addEventListener('click', (e) => {
        document.querySelectorAll('.model-option').forEach(o => o.classList.remove('selected'));
        option.classList.add('selected');
        activeModel = option.dataset.model;
        activeModelName = option.dataset.label;
        currentModelLabel.textContent = activeModelName;
        modelMenu.classList.add('hidden');
      });
    });

    // Prompt Textarea Input Handling
    userPromptInput.addEventListener('input', () => {
      // Auto-resize
      userPromptInput.style.height = 'auto';
      userPromptInput.style.height = Math.min(userPromptInput.scrollHeight, 200) + 'px';
      
      // Enable/Disable Send button
      sendPromptBtn.disabled = userPromptInput.value.trim() === '';
    });

    userPromptInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        if (!sendPromptBtn.disabled && !isGenerating) {
          submitUserPrompt();
        }
      }
    });

    sendPromptBtn.addEventListener('click', () => {
      if (!sendPromptBtn.disabled && !isGenerating) {
        submitUserPrompt();
      }
    });

    // Stop Generating Button
    stopGeneratingBtn.addEventListener('click', () => {
      if (currentAbortController) {
        currentAbortController.abort();
        setGeneratingState(false);
      }
    });

    // New Chat & Clear History
    newChatBtn.addEventListener('click', () => startNewChat());
    clearChatsBtn.addEventListener('click', () => clearAllChats());

    // Prompt Cards Click
    document.querySelectorAll('.prompt-card').forEach(card => {
      card.addEventListener('click', () => {
        const promptText = card.dataset.prompt;
        userPromptInput.value = promptText;
        userPromptInput.dispatchEvent(new Event('input'));
        submitUserPrompt();
      });
    });

    // Settings Modal
    openSettingsBtn.addEventListener('click', () => settingsModal.classList.remove('hidden'));
    closeSettingsBtn.addEventListener('click', () => settingsModal.classList.add('hidden'));
    settingsModal.addEventListener('click', (e) => {
      if (e.target === settingsModal) settingsModal.classList.add('hidden');
    });

    typingSpeedInput.addEventListener('input', () => {
      speedDisplayValue.textContent = `${typingSpeedInput.value} ms per token`;
    });

    saveSettingsBtn.addEventListener('click', () => {
      settings.openaiKey = openaiKeyInput.value.trim();
      settings.geminiKey = geminiKeyInput.value.trim();
      settings.personaPreset = personaPresetSelect.value;
      settings.typingSpeed = parseInt(typingSpeedInput.value);
      saveSettingsToStorage();
      settingsModal.classList.add('hidden');
    });

    resetSettingsBtn.addEventListener('click', () => {
      settings = { openaiKey: '', geminiKey: '', personaPreset: 'default', typingSpeed: 25, theme: 'dark' };
      applySettings();
      saveSettingsToStorage();
    });

    // Event delegation for code copy buttons
    document.addEventListener('click', (e) => {
      const copyBtn = e.target.closest('.copy-code-btn');
      if (copyBtn) {
        const code = decodeURIComponent(copyBtn.dataset.code);
        navigator.clipboard.writeText(code).then(() => {
          const originalHTML = copyBtn.innerHTML;
          copyBtn.innerHTML = `<i class="fa-solid fa-check"></i> Copied!`;
          setTimeout(() => { copyBtn.innerHTML = originalHTML; }, 2000);
        });
      }

      // Copy response text
      const copyMsgBtn = e.target.closest('.copy-msg-btn');
      if (copyMsgBtn) {
        const messageRow = copyMsgBtn.closest('.message-row');
        const textContent = messageRow.querySelector('.markdown-body')?.innerText || '';
        navigator.clipboard.writeText(textContent).then(() => {
          copyMsgBtn.innerHTML = `<i class="fa-solid fa-check"></i>`;
          setTimeout(() => { copyMsgBtn.innerHTML = `<i class="fa-regular fa-copy"></i>`; }, 2000);
        });
      }

      // Regenerate response
      const regenBtn = e.target.closest('.regenerate-msg-btn');
      if (regenBtn && !isGenerating) {
        regenerateLastMessage();
      }
    });
  }

  function saveSettingsToStorage() {
    localStorage.setItem('chatgpt_settings', JSON.stringify(settings));
  }

  function saveConversationsToStorage() {
    localStorage.setItem('chatgpt_conversations', JSON.stringify(conversations));
  }

  // Conversation Management
  function startNewChat() {
    if (isGenerating && currentAbortController) {
      currentAbortController.abort();
    }
    activeChatId = null;
    showWelcomeScreen();
    renderChatHistory();
    userPromptInput.focus();
  }

  function loadChat(chatId) {
    const chat = conversations.find(c => c.id === chatId);
    if (!chat) return;

    activeChatId = chatId;
    welcomeScreen.classList.add('hidden');
    chatMessagesContainer.classList.remove('hidden');
    chatMessagesContainer.innerHTML = '';

    chat.messages.forEach(msg => {
      appendMessageToUI(msg.role, msg.content, false);
    });

    renderChatHistory();
    scrollToBottom();
  }

  function clearAllChats() {
    if (confirm('Are you sure you want to delete all conversation history?')) {
      conversations = [];
      saveConversationsToStorage();
      startNewChat();
    }
  }

  function renderChatHistory() {
    chatHistoryList.innerHTML = '';
    if (conversations.length === 0) {
      chatHistoryList.innerHTML = `<div class="history-item-title" style="padding: 10px; color: var(--text-muted); font-size: 0.8rem;">No saved chats yet.</div>`;
      return;
    }

    conversations.forEach(chat => {
      const item = document.createElement('div');
      item.className = `history-item ${chat.id === activeChatId ? 'active' : ''}`;
      item.innerHTML = `
        <div class="history-item-content">
          <i class="fa-regular fa-message"></i>
          <span class="history-item-title">${escapeHtml(chat.title || 'New Chat')}</span>
        </div>
        <div class="history-item-actions">
          <i class="fa-regular fa-pen-to-square action-icon edit-chat-btn" data-id="${chat.id}"></i>
          <i class="fa-regular fa-trash-can action-icon delete-chat-btn" data-id="${chat.id}"></i>
        </div>
      `;

      item.addEventListener('click', (e) => {
        if (!e.target.classList.contains('action-icon')) {
          loadChat(chat.id);
        }
      });

      // Edit Chat Title
      const editBtn = item.querySelector('.edit-chat-btn');
      editBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        const newTitle = prompt('Enter new chat title:', chat.title);
        if (newTitle && newTitle.trim()) {
          chat.title = newTitle.trim();
          saveConversationsToStorage();
          renderChatHistory();
        }
      });

      // Delete Chat
      const deleteBtn = item.querySelector('.delete-chat-btn');
      deleteBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        conversations = conversations.filter(c => c.id !== chat.id);
        saveConversationsToStorage();
        if (activeChatId === chat.id) {
          startNewChat();
        } else {
          renderChatHistory();
        }
      });

      chatHistoryList.appendChild(item);
    });
  }

  function showWelcomeScreen() {
    welcomeScreen.classList.remove('hidden');
    chatMessagesContainer.classList.add('hidden');
    chatMessagesContainer.innerHTML = '';
  }

  // Chat Submission & Streaming logic
  async function submitUserPrompt() {
    const text = userPromptInput.value.trim();
    if (!text || isGenerating) return;

    // Clear input
    userPromptInput.value = '';
    userPromptInput.style.height = 'auto';
    sendPromptBtn.disabled = true;

    // Hide welcome screen
    welcomeScreen.classList.add('hidden');
    chatMessagesContainer.classList.remove('hidden');

    // Create or find current active conversation
    let chat = conversations.find(c => c.id === activeChatId);
    if (!chat) {
      chat = {
        id: 'chat_' + Date.now(),
        title: text.length > 30 ? text.substring(0, 30) + '...' : text,
        createdAt: new Date().toISOString(),
        messages: []
      };
      conversations.unshift(chat);
      activeChatId = chat.id;
    }

    // Append User Message
    chat.messages.push({ role: 'user', content: text });
    appendMessageToUI('user', text, false);
    saveConversationsToStorage();
    renderChatHistory();
    scrollToBottom();

    // Prepare Assistant Streaming Response
    await generateAssistantResponse(chat);
  }

  async function regenerateLastMessage() {
    let chat = conversations.find(c => c.id === activeChatId);
    if (!chat || chat.messages.length === 0) return;

    // If last message is assistant, pop it
    if (chat.messages[chat.messages.length - 1].role === 'assistant') {
      chat.messages.pop();
      chatMessagesContainer.lastElementChild?.remove();
    }

    saveConversationsToStorage();
    await generateAssistantResponse(chat);
  }

  async function generateAssistantResponse(chat) {
    setGeneratingState(true);

    // Create UI container for streaming assistant message
    const messageRow = document.createElement('div');
    messageRow.className = 'message-row assistant-row';
    messageRow.innerHTML = `
      <div class="message-avatar">
        <i class="fa-solid fa-robot"></i>
      </div>
      <div class="message-bubble">
        <div class="markdown-body"><span class="cursor-typing"></span></div>
        <div class="message-actions hidden">
          <button class="action-btn copy-msg-btn" title="Copy text"><i class="fa-regular fa-copy"></i></button>
          <button class="action-btn regenerate-msg-btn" title="Regenerate response"><i class="fa-solid fa-rotate-right"></i></button>
        </div>
      </div>
    `;
    chatMessagesContainer.appendChild(messageRow);
    scrollToBottom();

    const markdownBody = messageRow.querySelector('.markdown-body');
    const actionsDiv = messageRow.querySelector('.message-actions');

    currentAbortController = new AbortController();
    let accumulatedText = '';

    try {
      const response = await fetch('/api/chat/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        signal: currentAbortController.signal,
        body: JSON.stringify({
          model: activeModel,
          messages: chat.messages,
          settings: {
            openai_key: settings.openaiKey,
            gemini_key: settings.geminiKey,
            persona: settings.personaPreset,
            typing_speed: settings.typingSpeed
          }
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Server request failed');
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const dataStr = line.replace('data: ', '').trim();
            if (dataStr === '[DONE]') break;

            try {
              const parsed = JSON.parse(dataStr);
              if (parsed.content) {
                accumulatedText += parsed.content;
                markdownBody.innerHTML = marked.parse(accumulatedText) + `<span class="cursor-typing"></span>`;
                scrollToBottom();
              }
            } catch (err) {
              console.error('Failed to parse SSE data token:', err);
            }
          }
        }
      }

      // Complete message
      markdownBody.innerHTML = marked.parse(accumulatedText);
      actionsDiv.classList.remove('hidden');

      // Add to conversation history
      chat.messages.push({ role: 'assistant', content: accumulatedText });
      saveConversationsToStorage();

    } catch (err) {
      if (err.name === 'AbortError') {
        markdownBody.innerHTML = marked.parse(accumulatedText) + `\n\n*(Response stopped by user)*`;
        if (accumulatedText) {
          chat.messages.push({ role: 'assistant', content: accumulatedText });
          saveConversationsToStorage();
        }
      } else {
        markdownBody.innerHTML = `<div style="color: #ff6b6b;"><i class="fa-solid fa-triangle-exclamation"></i> Error: ${escapeHtml(err.message)}</div>`;
      }
      actionsDiv.classList.remove('hidden');
    } finally {
      setGeneratingState(false);
      currentAbortController = null;
    }
  }

  function appendMessageToUI(role, content, animate = false) {
    const messageRow = document.createElement('div');
    messageRow.className = `message-row ${role}-row`;

    if (role === 'user') {
      messageRow.innerHTML = `
        <div class="message-bubble">${escapeHtml(content)}</div>
        <div class="message-avatar">
          <i class="fa-solid fa-user"></i>
        </div>
      `;
    } else {
      messageRow.innerHTML = `
        <div class="message-avatar">
          <i class="fa-solid fa-robot"></i>
        </div>
        <div class="message-bubble">
          <div class="markdown-body">${marked.parse(content)}</div>
          <div class="message-actions">
            <button class="action-btn copy-msg-btn" title="Copy text"><i class="fa-regular fa-copy"></i></button>
            <button class="action-btn regenerate-msg-btn" title="Regenerate response"><i class="fa-solid fa-rotate-right"></i></button>
          </div>
        </div>
      `;
    }

    chatMessagesContainer.appendChild(messageRow);
  }

  function setGeneratingState(generating) {
    isGenerating = generating;
    if (generating) {
      stopGeneratingBtn.classList.remove('hidden');
      sendPromptBtn.disabled = true;
    } else {
      stopGeneratingBtn.classList.add('hidden');
      sendPromptBtn.disabled = userPromptInput.value.trim() === '';
    }
  }

  function scrollToBottom() {
    chatViewport.scrollTop = chatViewport.scrollHeight;
  }

  function escapeHtml(str) {
    return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#039;");
  }

  // Start Application
  init();
});
