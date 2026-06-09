/* FinanceIQ — frontend app.js */
(function () {
  'use strict';

  /* ── Theme ──────────────────────────────────────── */
  const root = document.documentElement;
  const themeBtn = document.getElementById('themeToggle');
  const saved = localStorage.getItem('fiq-theme') || 'dark';
  root.setAttribute('data-theme', saved);

  themeBtn?.addEventListener('click', () => {
    const next = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
    root.setAttribute('data-theme', next);
    localStorage.setItem('fiq-theme', next);
  });

  /* ── Tab switching ──────────────────────────────── */
  const tabBtns  = document.querySelectorAll('.tab-btn');
  const panels   = { stock: document.getElementById('panel-stock'), general: document.getElementById('panel-general') };

  function activateTab(name) {
    tabBtns.forEach(b => b.classList.toggle('active', b.dataset.tab === name));
    Object.entries(panels).forEach(([k, el]) => {
      if (!el) return;
      el.classList.toggle('active', k === name);
    });
    localStorage.setItem('fiq-tab', name);
  }

  tabBtns.forEach(btn => btn.addEventListener('click', () => activateTab(btn.dataset.tab)));

  // Restore active tab, or activate the one that has results
  const hasStock   = document.querySelector('.quote-card');
  const hasGeneral = document.querySelector('.answer-card');
  const savedTab   = localStorage.getItem('fiq-tab') || 'stock';

  if (hasGeneral) activateTab('general');
  else if (hasStock) activateTab('stock');
  else activateTab(savedTab);

  /* ── Loading state on form submit ───────────────── */
  function attachLoadingState(form, btnSelector) {
    const btn = form?.querySelector(btnSelector || '.search-btn');
    if (!form || !btn) return;
    form.addEventListener('submit', () => {
      btn.classList.add('btn-loading');
      btn.disabled = true;
    });
  }
  attachLoadingState(document.getElementById('stockForm'));
  attachLoadingState(document.getElementById('generalForm'));

  /* ── Quick-lookup chips ──────────────────────────── */
  const companyInput = document.getElementById('company');
  const stockForm    = document.getElementById('stockForm');

  document.querySelectorAll('.chip').forEach(chip => {
    chip.addEventListener('click', () => {
      if (!companyInput || !stockForm) return;
      companyInput.value = chip.dataset.symbol;
      activateTab('stock');
      stockForm.submit();
    });
  });

  /* ── Markdown-lite renderer for answer body ─────── */
  const answerBody = document.getElementById('answerBody');
  if (answerBody) {
    let md = answerBody.textContent || '';
    md = escapeHtml(md);
    md = md
      // Headers
      .replace(/^### (.+)$/gm, '<h3>$1</h3>')
      .replace(/^## (.+)$/gm, '<h2>$1</h2>')
      .replace(/^# (.+)$/gm, '<h1>$1</h1>')
      // Bold + italic
      .replace(/\*\*\*(.+?)\*\*\*/g, '<strong><em>$1</em></strong>')
      .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.+?)\*/g, '<em>$1</em>')
      // Inline code
      .replace(/`([^`]+)`/g, '<code>$1</code>')
      // Unordered lists
      .replace(/^[\-\*] (.+)$/gm, '<li>$1</li>')
      .replace(/(<li>.*<\/li>\n?)+/g, m => '<ul>' + m + '</ul>')
      // Line breaks
      .replace(/\n{2,}/g, '</p><p>')
      .replace(/\n/g, '<br>');

    answerBody.innerHTML = '<p>' + md + '</p>';
  }

  function escapeHtml(str) {
    return str
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  /* ── Auto-grow textarea ──────────────────────────── */
  const textarea = document.querySelector('.query-input');
  if (textarea) {
    textarea.addEventListener('input', () => {
      textarea.style.height = 'auto';
      textarea.style.height = textarea.scrollHeight + 'px';
    });
  }

  /* ── Keyboard shortcut: / to focus search ─────────── */
  document.addEventListener('keydown', e => {
    if (e.key === '/' && document.activeElement.tagName !== 'INPUT' && document.activeElement.tagName !== 'TEXTAREA') {
      e.preventDefault();
      const activePanel = document.querySelector('.panel.active');
      const input = activePanel?.querySelector('input, textarea');
      input?.focus();
    }
  });

})();
