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

  // ── Chatbot: restaura histórico da sessão do navegador ───────────────────
  _chatbotLoadHistory();

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

var CHATBOT_SESSION_KEY = 'smpi_chatbot_history';
var CHATBOT_MAX_MSGS    = 20;

function _chatbotLoadHistory() {
  var messages = document.getElementById('chatbot-messages');
  if (!messages) return;
  try {
    var stored = sessionStorage.getItem(CHATBOT_SESSION_KEY);
    if (!stored) return;
    var history = JSON.parse(stored);
    history.forEach(function(m) {
      var bubble = document.createElement('div');
      bubble.className = 'smpi-chat-msg smpi-chat-msg--' + m.role;
      if (m.role === 'assistant' && window.marked) {
        bubble.innerHTML = window.marked.parse(m.content);
      } else {
        bubble.textContent = m.content;
      }
      messages.appendChild(bubble);
    });
    messages.scrollTop = messages.scrollHeight;
  } catch (e) {}
}

function _chatbotSaveMessage(role, content) {
  try {
    var stored = sessionStorage.getItem(CHATBOT_SESSION_KEY);
    var history = stored ? JSON.parse(stored) : [];
    history.push({ role: role, content: content });
    if (history.length > CHATBOT_MAX_MSGS) {
      history = history.slice(history.length - CHATBOT_MAX_MSGS);
    }
    sessionStorage.setItem(CHATBOT_SESSION_KEY, JSON.stringify(history));
  } catch (e) {}
}

function toggleChatbot() {
  var panel = document.getElementById('chatbot-panel');
  var btn   = document.querySelector('.smpi-chatbot-btn');
  if (!panel) return;
  var isOpen = panel.classList.toggle('open');
  if (btn) btn.setAttribute('aria-expanded', isOpen);
  if (isOpen) {
    var input = document.getElementById('chatbot-input');
    if (input) input.focus();
  }
}

function sendChatbotMessage() {
  var input    = document.getElementById('chatbot-input');
  var messages = document.getElementById('chatbot-messages');
  if (!input || !messages) return;

  var text = input.value.trim();
  if (!text) return;

  input.value = '';
  input.disabled = true;

  var userBubble = document.createElement('div');
  userBubble.className = 'smpi-chat-msg smpi-chat-msg--user';
  userBubble.textContent = text;
  messages.appendChild(userBubble);
  _chatbotSaveMessage('user', text);

  var asstBubble = document.createElement('div');
  asstBubble.className = 'smpi-chat-msg smpi-chat-msg--assistant';
  asstBubble.innerHTML = '<span class="smpi-spinner" aria-label="Processando..."></span>';
  messages.appendChild(asstBubble);
  messages.scrollTop = messages.scrollHeight;

  var formData = new FormData();
  formData.append('message', text);
  formData.append('csrfmiddlewaretoken', getCsrf());

  fetch('/ai/chatbot/stream/', { method: 'POST', body: formData })
    .then(function(response) {
      if (!response.ok) throw new Error('HTTP ' + response.status);

      var reader = response.body.getReader();
      var decoder = new TextDecoder();
      var sseBuffer = '';
      var fullText = '';

      function readChunk() {
        return reader.read().then(function(result) {
          if (result.done) return;
          sseBuffer += decoder.decode(result.value, { stream: true });
          var lines = sseBuffer.split('\n');
          sseBuffer = lines.pop();

          for (var i = 0; i < lines.length; i++) {
            var line = lines[i];
            if (!line.startsWith('data: ')) continue;
            var token = line.slice(6);
            if (token === '[DONE]') {
              _chatbotSaveMessage('assistant', fullText);
              return;
            }
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
