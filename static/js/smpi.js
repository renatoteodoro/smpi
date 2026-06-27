/**
 * SMPI — Main JavaScript
 * Sidebar toggle, notifications, alerts auto-dismiss, floating chatbot.
 */

document.addEventListener('DOMContentLoaded', function () {
  // ── Sidebar toggle (mobile) ──────────────────────────────────────────────
  const sidebarToggle = document.getElementById('sidebar-toggle');
  if (sidebarToggle) {
    sidebarToggle.addEventListener('click', toggleSidebar);
  }

  // ── Auto-dismiss alerts after 5 s ────────────────────────────────────────
  document.querySelectorAll('.smpi-alert[data-auto-dismiss]').forEach(function (el) {
    setTimeout(function () {
      el.style.transition = 'opacity .4s';
      el.style.opacity = '0';
      setTimeout(function () { el.remove(); }, 400);
    }, 5000);
  });

  // ── Notification dropdown — close when clicking outside ──────────────────
  document.addEventListener('click', function (e) {
    const dropdown = document.getElementById('notif-dropdown');
    if (!dropdown) return;
    const trigger = document.querySelector('[aria-controls="notif-dropdown"]') ||
                    document.querySelector('[onclick*="notif-dropdown"]');
    if (dropdown.classList.contains('open') &&
        !dropdown.contains(e.target) &&
        (!trigger || !trigger.contains(e.target))) {
      dropdown.classList.remove('open');
    }
  });

  // ── Mark single notification as read ─────────────────────────────────────
  document.querySelectorAll('[data-notif-read]').forEach(function (el) {
    el.addEventListener('click', function () {
      const id = this.dataset.notifRead;
      fetch('/notifications/' + id + '/read/', {
        method: 'POST',
        headers: { 'X-CSRFToken': getCsrf() },
      });
    });
  });

  // ── Mark all notifications as read ───────────────────────────────────────
  const markAllBtn = document.getElementById('mark-all-read');
  if (markAllBtn) {
    markAllBtn.addEventListener('click', function () {
      fetch('/notifications/read-all/', {
        method: 'POST',
        headers: { 'X-CSRFToken': getCsrf() },
      }).then(function () {
        location.reload();
      });
    });
  }

  // ── Chatbot Enter-key support ─────────────────────────────────────────────
  const chatInput = document.getElementById('chatbot-input');
  if (chatInput) {
    chatInput.addEventListener('keydown', function (e) {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendChatbotMessage();
      }
    });
  }
});

// ── Sidebar toggle ───────────────────────────────────────────────────────────
function toggleSidebar() {
  const sidebar = document.querySelector('.smpi-sidebar');
  const overlay = document.getElementById('sidebar-overlay');
  const btn = document.getElementById('sidebar-toggle');
  if (!sidebar) return;
  const isOpen = sidebar.classList.toggle('open');
  if (overlay) overlay.classList.toggle('open', isOpen);
  if (btn) btn.setAttribute('aria-expanded', isOpen);
}

// ── Utilities ────────────────────────────────────────────────────────────────

/**
 * Returns the CSRF token from the meta tag injected by base.html.
 * @returns {string}
 */
function getCsrf() {
  const meta = document.querySelector('meta[name="csrf-token"]');
  return meta ? meta.content : '';
}

// ── Floating chatbot ─────────────────────────────────────────────────────────

/**
 * Toggle the chatbot panel open/closed.
 */
function toggleChatbot() {
  const panel = document.getElementById('chatbot-panel');
  const btn   = document.querySelector('.smpi-chatbot-btn');
  if (!panel) return;
  const isOpen = panel.classList.toggle('open');
  if (btn) btn.setAttribute('aria-expanded', isOpen);
  if (isOpen) {
    const input = document.getElementById('chatbot-input');
    if (input) input.focus();
  }
}

/**
 * Send a message via the floating chatbot.
 * POSTs to /ai/chatbot/stream/ and reads the SSE response body directly.
 */
function sendChatbotMessage() {
  const input    = document.getElementById('chatbot-input');
  const messages = document.getElementById('chatbot-messages');
  if (!input || !messages) return;

  const text = input.value.trim();
  if (!text) return;

  input.value = '';
  input.disabled = true;

  // User bubble
  const userBubble = document.createElement('div');
  userBubble.className = 'smpi-chat-msg smpi-chat-msg--user';
  userBubble.textContent = text;
  messages.appendChild(userBubble);

  // Assistant loading bubble
  const asstBubble = document.createElement('div');
  asstBubble.className = 'smpi-chat-msg smpi-chat-msg--assistant';
  asstBubble.innerHTML = '<span class="smpi-spinner" aria-label="Processando..."></span>';
  messages.appendChild(asstBubble);
  messages.scrollTop = messages.scrollHeight;

  const formData = new FormData();
  formData.append('message', text);
  formData.append('csrfmiddlewaretoken', getCsrf());

  fetch('/ai/chatbot/stream/', { method: 'POST', body: formData })
    .then(function(response) {
      if (!response.ok) throw new Error('HTTP ' + response.status);

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let sseBuffer = '';
      let fullText = '';

      function readChunk() {
        return reader.read().then(function(result) {
          if (result.done) return;
          sseBuffer += decoder.decode(result.value, { stream: true });
          const lines = sseBuffer.split('\n');
          sseBuffer = lines.pop();

          for (let i = 0; i < lines.length; i++) {
            const line = lines[i];
            if (!line.startsWith('data: ')) continue;
            const token = line.slice(6);
            if (token === '[DONE]') return;
            if (token.startsWith('[ERROR]')) {
              asstBubble.textContent = 'Erro: ' + token.slice(8);
              return;
            }
            fullText += token.replace(/\\n/g, '\n');
            if (window.marked) {
              asstBubble.innerHTML = window.marked.parse(fullText);
            } else {
              asstBubble.textContent = fullText;
            }
            messages.scrollTop = messages.scrollHeight;
          }
          return readChunk();
        });
      }
      return readChunk();
    })
    .catch(function(err) {
      asstBubble.textContent = 'Erro de conexão: ' + err.message;
    })
    .finally(function() {
      input.disabled = false;
      input.focus();
    });
}

/**
 * Toggle notification dropdown open/closed.
 * Called from the button's onclick in base.html.
 */
function toggleNotifDropdown() {
  const dropdown = document.getElementById('notif-dropdown');
  if (dropdown) dropdown.classList.toggle('open');
}

/**
 * Show a loading state on an async-action button.
 * @param {HTMLButtonElement} btn
 */
function smpiButtonLoading(btn) {
  btn.disabled = true;
  const label = btn.querySelector('[data-label]') || btn;
  btn.dataset.originalText = label.textContent;
  label.innerHTML = '<span class="smpi-spinner"></span> Processando...';
}

/**
 * Restore an async-action button to its original state.
 * @param {HTMLButtonElement} btn
 */
function smpiButtonRestore(btn) {
  btn.disabled = false;
  const label = btn.querySelector('[data-label]') || btn;
  if (btn.dataset.originalText) {
    label.textContent = btn.dataset.originalText;
  }
}
