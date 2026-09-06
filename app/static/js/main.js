/* ── Global Floating Popup Toast Manager ── */
window.pgToast = function (message, category = 'info', title = '') {
  let container = document.querySelector('.pg-popup-toast-container');
  if (!container) {
    container = document.createElement('div');
    container.className = 'pg-popup-toast-container';
    document.body.appendChild(container);
  }

  const icons = {
    success: 'bi-check-circle-fill',
    danger: 'bi-exclamation-octagon-fill',
    warning: 'bi-exclamation-triangle-fill',
    info: 'bi-info-circle-fill'
  };
  const titles = {
    success: 'Action Successful',
    danger: 'Security Notice',
    warning: 'Warning',
    info: 'System Intelligence'
  };

  const iconClass = icons[category] || icons.info;
  const displayTitle = title || titles[category] || 'Notification';

  const toast = document.createElement('div');
  toast.className = `pg-popup-toast toast-${category}`;
  toast.innerHTML = `
    <i class="bi ${iconClass} toast-icon"></i>
    <div class="toast-body-content">
      <div class="toast-title">${displayTitle}</div>
      <div class="toast-msg">${message}</div>
    </div>
    <button type="button" class="toast-close-btn" aria-label="Close">&times;</button>
  `;

  toast.querySelector('.toast-close-btn').onclick = () => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(-10px) scale(0.95)';
    setTimeout(() => toast.remove(), 300);
  };

  container.appendChild(toast);

  // Auto-dismiss after 4.5 seconds
  setTimeout(() => {
    if (toast.parentElement) {
      toast.style.opacity = '0';
      toast.style.transform = 'translateY(-10px) scale(0.95)';
      setTimeout(() => toast.remove(), 300);
    }
  }, 4500);
};

// Automatically manage server rendered toasts on DOM load
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.pg-popup-toast').forEach(toast => {
    const closeBtn = toast.querySelector('.toast-close-btn');
    if (closeBtn) {
      closeBtn.onclick = () => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateY(-10px) scale(0.95)';
        setTimeout(() => toast.remove(), 300);
      };
    }
    setTimeout(() => {
      if (toast.parentElement) {
        toast.style.opacity = '0';
        toast.style.transform = 'translateY(-10px) scale(0.95)';
        setTimeout(() => toast.remove(), 300);
      }
    }, 4500);
  });
});

/* ── Dark / Light Mode Toggle & Dynamic Chart Sync ── */
window.PhishGuardTheme = (function () {
  const root = document.documentElement;
  let lastToggleTime = 0;

  function getTheme() {
    return localStorage.getItem('pg_theme') || 'dark';
  }

  function setTheme(theme) {
    root.setAttribute('data-theme', theme);
    localStorage.setItem('pg_theme', theme);

    // Update all theme toggle buttons across the page
    document.querySelectorAll('.theme-switch-btn').forEach(btn => {
      const icon = btn.querySelector('i') || btn;
      if (theme === 'light') {
        icon.className = 'bi bi-sun-fill text-warning';
        btn.setAttribute('title', 'Switch to Dark Mode');
        btn.setAttribute('aria-label', 'Switch to Dark Mode');
      } else {
        icon.className = 'bi bi-moon-stars-fill text-cyan';
        btn.setAttribute('title', 'Switch to Light Mode');
        btn.setAttribute('aria-label', 'Switch to Light Mode');
      }
    });

    // Notify any active charts or canvas to re-render with new colors
    window.dispatchEvent(new CustomEvent('pg_theme_changed', { detail: { theme } }));
  }

  function toggleTheme(e) {
    if (e && e.preventDefault) e.preventDefault();
    if (e && e.stopPropagation) e.stopPropagation();

    const now = Date.now();
    if (now - lastToggleTime < 300) return; // Prevent double-trigger within 300ms
    lastToggleTime = now;

    const current = getTheme();
    const next = current === 'light' ? 'dark' : 'light';
    setTheme(next);
  }

  // Initialize on DOM load
  document.addEventListener('DOMContentLoaded', () => {
    const initialTheme = getTheme();
    setTheme(initialTheme);

    document.querySelectorAll('.theme-switch-btn, .theme-toggle-switch, #themeToggle').forEach(btn => {
      btn.onclick = (e) => {
        toggleTheme(e);
      };
    });
  });

  return { getTheme, setTheme, toggleTheme };
})();

/* ── Interactive Mail & URL Bar Recommendations on Click/Focus ── */
document.addEventListener('DOMContentLoaded', () => {
  // Mail recommendation dropdown toggler
  document.querySelectorAll('.mail-bar-input').forEach(input => {
    const dropdown = input.closest('.input-recommendation-wrapper')?.querySelector('.bar-recommendation-dropdown');
    if (!dropdown) return;

    input.addEventListener('focus', () => {
      dropdown.classList.add('show');
    });

    input.addEventListener('click', () => {
      dropdown.classList.add('show');
    });

    // Close when clicking outside
    document.addEventListener('click', (e) => {
      if (!input.contains(e.target) && !dropdown.contains(e.target)) {
        dropdown.classList.remove('show');
      }
    });
  });

  // URL recommendation dropdown toggler
  document.querySelectorAll('.url-bar-input-field').forEach(input => {
    const dropdown = input.closest('.input-recommendation-wrapper')?.querySelector('.bar-recommendation-dropdown');
    if (!dropdown) return;

    input.addEventListener('focus', () => {
      dropdown.classList.add('show');
    });

    input.addEventListener('click', () => {
      dropdown.classList.add('show');
    });

    document.addEventListener('click', (e) => {
      if (!input.contains(e.target) && !dropdown.contains(e.target)) {
        dropdown.classList.remove('show');
      }
    });
  });
});

/* ── Global Ctrl+K Shortcut → Focus URL input ── */
document.addEventListener('keydown', e => {
  if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
    e.preventDefault();
    const inp = document.getElementById('urlInput') ||
                document.querySelector('.url-main-input') ||
                document.querySelector('input[name="url"]');
    if (inp) {
      inp.focus();
      inp.select();
    }
  }
});

/* ── Confetti Burst (Safe verdict) ── */
window.pgConfetti = function(count = 70) {
  const colors = ['#00E5FF', '#2563EB', '#22C55E', '#38BDF8', '#FFFFFF'];
  const canvas = document.createElement('canvas');
  canvas.style.cssText = 'position:fixed;inset:0;z-index:99999;pointer-events:none;';
  canvas.width = innerWidth;
  canvas.height = innerHeight;
  document.body.appendChild(canvas);
  const ctx = canvas.getContext('2d');

  const pieces = Array.from({ length: count }, () => ({
    x: Math.random() * innerWidth,
    y: Math.random() * (innerHeight * 0.4) - 20,
    r: Math.random() * 6 + 3,
    color: colors[Math.floor(Math.random() * colors.length)],
    dx: (Math.random() - 0.5) * 3.5,
    dy: Math.random() * 3 + 1.5,
    rot: Math.random() * 360,
    drot: (Math.random() - 0.5) * 6,
    life: 1,
  }));

  let frame;
  (function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    let alive = false;
    pieces.forEach(p => {
      p.x += p.dx;
      p.y += p.dy;
      p.rot += p.drot;
      p.life -= 0.014;
      if (p.life <= 0) return;
      alive = true;
      ctx.save();
      ctx.globalAlpha = p.life;
      ctx.translate(p.x, p.y);
      ctx.rotate(p.rot * Math.PI / 180);
      ctx.fillStyle = p.color;
      ctx.fillRect(-p.r / 2, -p.r / 2, p.r, p.r * 0.6);
      ctx.restore();
    });
    if (alive) {
      frame = requestAnimationFrame(draw);
    } else {
      cancelAnimationFrame(frame);
      canvas.remove();
    }
  })();
};

/* ── Live URL Risk Score Preview ── */
window.pgUrlRisk = function(val) {
  let score = 0;
  if (!val) return 0;
  if (val.length > 75) score += 18;
  if (val.length > 110) score += 12;
  if (/@/.test(val)) score += 25;
  if (/\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/.test(val)) score += 30;
  const suspicious = ['login','verify','secure','account','update','confirm','banking','paypal','ebay','amazon','signin','password','credential','auth','recover'];
  suspicious.forEach(k => {
    if (val.toLowerCase().includes(k)) score += 7;
  });
  const dots = (val.match(/\./g) || []).length;
  if (dots > 4) score += 15;
  const specials = (val.match(/[-_~%@!]/g) || []).length;
  if (specials > 3) score += 10;
  if (!/^https/i.test(val)) score += 15;
  return Math.min(score, 100);
};

/* ── Password visibility toggle ── */
window.togglePass = function(id, btn) {
  const el = document.getElementById(id);
  if (!el) return;
  el.type = el.type === 'password' ? 'text' : 'password';
  if (btn) {
    const icon = btn.querySelector('i');
    if (icon) {
      icon.className = el.type === 'password' ? 'bi bi-eye' : 'bi bi-eye-slash';
    }
  }
};

/* ── Interactive 3D Card Parallax Tilt & Scroll Reveal ── */
document.addEventListener('DOMContentLoaded', () => {
  const tiltCards = document.querySelectorAll('.spotlight-card, .stat-card, .tilt-card-3d');

  tiltCards.forEach(card => {
    card.addEventListener('mousemove', (e) => {
      const rect = card.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      const centerX = rect.width / 2;
      const centerY = rect.height / 2;

      const rotateX = ((y - centerY) / centerY) * -6;
      const rotateY = ((x - centerX) / centerX) * 6;

      card.style.transform = `perspective(1000px) rotateX(${rotateX.toFixed(2)}deg) rotateY(${rotateY.toFixed(2)}deg) translateY(-4px)`;
    });

    card.addEventListener('mouseleave', () => {
      card.style.transform = 'perspective(1000px) rotateX(0deg) rotateY(0deg) translateY(0px)';
    });
  });

  /* ── Scroll Reveal ── */
  const revealElements = document.querySelectorAll('.reveal-on-scroll, .spotlight-card');
  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('revealed');
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.1 });

    revealElements.forEach(el => observer.observe(el));
  }

  /* ── Ultra-Robust Modal Controller & Clean Dismiss ── */
  document.querySelectorAll('[data-bs-toggle="modal"]').forEach(trigger => {
    trigger.addEventListener('click', () => {
      // Auto-collapse mobile navbar if open
      const mobileNav = document.querySelector('.navbar-collapse.show');
      if (mobileNav && typeof bootstrap !== 'undefined') {
        const bsCollapse = bootstrap.Collapse.getInstance(mobileNav) || new bootstrap.Collapse(mobileNav, { toggle: false });
        bsCollapse.hide();
      }
    });
  });

  // Handle all dismiss buttons smoothly
  document.addEventListener('click', (e) => {
    const dismissBtn = e.target.closest('[data-bs-dismiss="modal"]');
    if (dismissBtn) {
      const modalEl = dismissBtn.closest('.modal');
      if (modalEl && typeof bootstrap !== 'undefined') {
        const modalInstance = bootstrap.Modal.getInstance(modalEl);
        if (modalInstance) {
          modalInstance.hide();
        }
      }
    }
  });

  // Cleanup backdrop on escape key or hidden event
  document.querySelectorAll('.modal').forEach(modal => {
    modal.addEventListener('hidden.bs.modal', () => {
      document.body.classList.remove('modal-open');
      document.body.style.removeProperty('overflow');
      document.body.style.removeProperty('padding-right');
      document.querySelectorAll('.modal-backdrop').forEach(b => b.remove());
    });
  });
});

/* ── 23. PHISHGAURD AI VIRTUAL SECURITY ASSISTANT (Ask Phishgaurd AI) ── */
window.PhishGuardHelpBot = (function () {
  const KNOWLEDGE_BASE = [
    {
      keywords: ['scan', 'url', 'how to scan', 'inspect', 'check link'],
      answer: "🔍 <strong>How to Scan a URL:</strong><br/>1. Go to the <strong><a href='/scanner/scan' style='color:var(--accent-cyan);'>URL Scanner</a></strong> page.<br/>2. Paste any link (e.g., <code>https://example.com/login</code>).<br/>3. Click <strong>Run Threat Inspection</strong>.<br/>Our 15-signal heuristic engine and Random Forest AI model will classify the URL as <strong>Safe</strong>, <strong>Suspicious</strong>, or <strong>Phishing</strong> in milliseconds!"
    },
    {
      keywords: ['risk score', 'score', 'percentage', 'risk', 'meaning'],
      answer: "📊 <strong>Risk Score Guide (0–100):</strong><br/>• <span style='color:var(--status-safe); font-weight:700;'>0 to 29 (SAFE):</span> Clean verified domain with established WHOIS age and valid SSL.<br/>• <span style='color:var(--status-suspicious); font-weight:700;'>30 to 69 (SUSPICIOUS):</span> Anomalous subdomains, newly registered domain, or deceptive keyword stuffing.<br/>• <span style='color:var(--status-phishing); font-weight:700;'>70 to 100 (PHISHING):</span> High-danger threat! Contains credential harvesting forms, direct IP hosting, or spoofed brand signatures. <em>Do not enter credentials!</em>"
    },
    {
      keywords: ['typosquatting', 'typo', 'lookalike', 'spoof', 'fake domain'],
      answer: "⚠️ <strong>What is Typosquatting?</strong><br/>Attackers register lookalike domains with deceptive subdomains or hyphens (like <code>netflix-security-billing.com</code> or <code>apple-support-verify.cc</code>) to impersonate trusted platforms.<br/><br/><strong>Phishgaurd AI</strong> automatically analyzes brand entropy and multi-tier subdomains to catch these spoofed URLs instantly."
    },
    {
      keywords: ['spot', 'recognize', 'phishing', 'email', 'smishing', 'identify'],
      answer: "🚨 <strong>How to Spot Phishing Links:</strong><br/>1. <strong>Check the full address:</strong> Attackers hide true domains in subdomains (e.g. <code>paypal.com.verify-user.xyz</code>).<br/>2. <strong>Look for IP addresses:</strong> Legitimate companies rarely send raw numeric links like <code>http://192.168.1.1/login</code>.<br/>3. <strong>Beware of extreme urgency:</strong> 'Account deleted in 1 hour' is a classic social engineering trick.<br/>4. <strong>Always scan links here in Phishgaurd AI first!</strong>"
    },
    {
      keywords: ['pdf', 'report', 'download', 'audit', 'export'],
      answer: "📄 <strong>Forensic PDF Security Reports:</strong><br/>After scanning any URL, click <strong>Download PDF Forensic Report</strong> on the results page. You'll get an audit report with:<br/>• Visual risk level gauges<br/>• Exact 15-signal telemetry breakdown<br/>• SSL/TLS & WHOIS verification timestamps<br/>• Actionable security advice."
    },
    {
      keywords: ['model', 'ml', 'random forest', 'ai', 'algorithm', 'dataset'],
      answer: "🛡️ <strong>Machine Learning Architecture:</strong><br/>Phishgaurd AI utilizes an ensemble <strong>Random Forest Classifier</strong> trained on 17,000+ verified safe, suspicious, and zero-day phishing samples.<br/><br/>It simultaneously evaluates 15 structural and lexical signals to deliver &gt;99% detection precision."
    },
    {
      keywords: ['password', 'reset', 'forgot', 'account', 'recovery'],
      answer: "🔑 <strong>Account & Password Assistance:</strong><br/>• To reset your password, visit the <strong><a href='/auth/forgot-password' style='color:var(--accent-cyan);'>Password Reset</a></strong> page and enter your registered email.<br/>• When creating passwords, our live strength meter checks for 8+ characters, uppercase, lowercase, numbers, and symbols."
    }
  ];

  function toggleChat(forceState) {
    const popup = document.getElementById('pgHelpPopup');
    const hint = document.getElementById('pgHelpBubbleHint');
    if (!popup) return;

    const isActive = forceState !== undefined ? forceState : !popup.classList.contains('active');
    if (isActive) {
      popup.classList.add('active');
      if (hint) hint.style.display = 'none';
      const input = document.getElementById('pgHelpUserInput');
      if (input) setTimeout(() => input.focus(), 300);
    } else {
      popup.classList.remove('active');
    }
  }

  function closeBubble(e) {
    if (e) e.stopPropagation();
    const hint = document.getElementById('pgHelpBubbleHint');
    if (hint) hint.style.display = 'none';
    sessionStorage.setItem('pg_help_bubble_closed', '1');
  }

  function askQuestion(query) {
    if (!query || !query.trim()) return;
    const cleanQuery = query.trim();

    // Append User Message
    appendMessage(cleanQuery, 'user');

    // Show Typing Indicator
    const typingId = showTypingIndicator();

    setTimeout(() => {
      removeTypingIndicator(typingId);

      // Find Match
      const qLower = cleanQuery.toLowerCase();
      let bestMatch = null;

      for (const item of KNOWLEDGE_BASE) {
        if (item.keywords.some(k => qLower.includes(k))) {
          bestMatch = item.answer;
          break;
        }
      }

      if (!bestMatch) {
        bestMatch = `🛡️ I can help you with anything related to <strong>Phishgaurd AI</strong>!<br/><br/>Try asking about:<br/>• <em>"How does URL scanning work?"</em><br/>• <em>"What is the Risk Score?"</em><br/>• <em>"How to spot fake phishing emails?"</em><br/>• <em>"How to download forensic PDF reports?"</em><br/><br/>You can also click any of the quick action buttons below!`;
      }

      appendMessage(bestMatch, 'bot');
    }, 600);
  }

  function appendMessage(htmlContent, sender = 'bot') {
    const body = document.getElementById('pgHelpChatBody');
    if (!body) return;

    const msg = document.createElement('div');
    msg.className = `pg-chat-msg ${sender}`;

    const icon = sender === 'bot' ? '<i class="bi bi-robot"></i>' : '<i class="bi bi-person-fill"></i>';

    msg.innerHTML = `
      <div class="pg-msg-bubble">
        ${htmlContent}
      </div>
    `;

    body.appendChild(msg);
    body.scrollTop = body.scrollHeight;
  }

  function showTypingIndicator() {
    const body = document.getElementById('pgHelpChatBody');
    if (!body) return null;

    const typingDiv = document.createElement('div');
    const id = 'typing_' + Date.now();
    typingDiv.id = id;
    typingDiv.className = 'pg-chat-msg bot';
    typingDiv.innerHTML = `
      <div class="pg-typing-bubble">
        <div class="pg-typing-dot"></div>
        <div class="pg-typing-dot"></div>
        <div class="pg-typing-dot"></div>
      </div>
    `;

    body.appendChild(typingDiv);
    body.scrollTop = body.scrollHeight;
    return id;
  }

  function removeTypingIndicator(id) {
    if (!id) return;
    const el = document.getElementById(id);
    if (el) el.remove();
  }

  function resetChat() {
    const body = document.getElementById('pgHelpChatBody');
    if (!body) return;
    body.innerHTML = `
      <!-- Bot Greeting -->
      <div class="pg-chat-msg bot">
        <div class="pg-msg-bubble">
          👋 <strong>Hello! I am your Phishgaurd AI Assistant.</strong><br/>
          I'm here 24/7 to help you understand phishing detection, verify URLs, and explore security features.<br/><br/>
          <div class="pg-chips-title">Frequent Topics:</div>
          <div class="pg-chips-grid">
            <button class="pg-chip" onclick="PhishGuardHelpBot.askQuestion('How to scan a URL?')"><i class="bi bi-search"></i> How to scan a URL?</button>
            <button class="pg-chip" onclick="PhishGuardHelpBot.askQuestion('What does the Risk Score mean?')"><i class="bi bi-speedometer2"></i> Risk Score meaning</button>
            <button class="pg-chip" onclick="PhishGuardHelpBot.askQuestion('What is typosquatting?')"><i class="bi bi-exclamation-diamond"></i> Typosquatting</button>
            <button class="pg-chip" onclick="PhishGuardHelpBot.askQuestion('How to spot phishing links?')"><i class="bi bi-shield-x"></i> Spot phishing</button>
            <button class="pg-chip" onclick="PhishGuardHelpBot.askQuestion('Forensic PDF report')"><i class="bi bi-file-pdf"></i> PDF Reports</button>
          </div>
        </div>
      </div>
    `;
  }

  return {
    toggleChat,
    closeBubble,
    askQuestion,
    resetChat
  };
})();

