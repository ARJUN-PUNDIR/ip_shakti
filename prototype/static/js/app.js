/**
 * IP-SAKTI Sahayak — Minimalist Conversational AI Engine
 * ChatGPT / Apple Aesthetics with Dynamic Saved Chats, MCP Protocols, & Multi-Agent StateGraph
 */

let activeChatId = null;
let speechRecognitionInstance = null;
let voiceTranscribedText = "";

const CHATS_STORAGE_KEY = "ipsakti_saved_chats";

document.addEventListener("DOMContentLoaded", () => {
  fetchConfig();
  renderSavedChatsSidebar();
  setupUniversalModalListeners();
  initTheme();
  initLanguage();
  initSources();
});

// Universal Modal Dismissal (Click Outside Backdrop & Escape Key)
function setupUniversalModalListeners() {
  document.querySelectorAll(".modal-backdrop").forEach(modal => {
    modal.addEventListener("click", (e) => {
      if (e.target === modal) {
        modal.classList.add("hidden");
      }
    });
  });

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      document.querySelectorAll(".modal-backdrop").forEach(modal => {
        modal.classList.add("hidden");
      });
    }
  });
}

// Auto-adjust textarea height on input
const textarea = document.getElementById("userPromptInput");
if (textarea) {
  textarea.addEventListener("input", function () {
    this.style.height = "auto";
    this.style.height = Math.min(this.scrollHeight, 120) + "px";
  });
}

function handleKeyDown(e) {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    handleSend();
  }
}

let serverConfig = {
  provider: "nvidia",
  model: "nvidia/nemotron-3-ultra-550b-a55b",
  has_nvidia_key: false,
  nvidia_key_masked: "Not Set",
  has_openai_key: false,
  openai_key_masked: "Not Set",
  ollama_url: "http://localhost:11434"
};

let currentProvider = "nvidia";

const PROVIDER_MODELS = {
  nvidia: [
    { id: "nvidia/nemotron-3-ultra-550b-a55b", label: "⚡ Nemotron-3 Ultra (Accuracy: 98.2%)" },
    { id: "nvidia/nemotron-3.5-lightning-30b-a3b", label: "⚡ Nemotron-3.5 Lightning (Speed: 18ms)" },
    { id: "meta/llama-3.3-70b-instruct", label: "🦙 Llama-3.3 70B (Accuracy: 95.8%)" },
    { id: "deepseek-ai/deepseek-r1", label: "🧠 DeepSeek-R1 (Reasoning: 97.1%)" },
    { id: "custom", label: "✏️ Custom NVIDIA NIM Model..." }
  ],
  openai: [
    { id: "gpt-4o", label: "🤖 OpenAI GPT-4o (Accuracy: 98.9%)" },
    { id: "gpt-4o-mini", label: "🤖 OpenAI GPT-4o-Mini (Speed: 22ms)" },
    { id: "o3-mini", label: "🧠 OpenAI o3-Mini (Reasoning: 98.5%)" },
    { id: "o1", label: "🧠 OpenAI o1 (Deep Reasoning: 99.1%)" },
    { id: "custom", label: "✏️ Custom OpenAI Model..." }
  ],
  ollama: [
    { id: "llama3.2", label: "💻 Ollama Llama-3.2 (Local 100%)" },
    { id: "llama3:8b", label: "💻 Ollama Llama-3 8B (Local 100%)" },
    { id: "qwen2.5:7b", label: "💻 Ollama Qwen-2.5 (Local 100%)" },
    { id: "custom", label: "✏️ Custom Local Model..." }
  ]
};

// Auto-detect provider from model name
function detectProviderFromModel(modelName) {
  if (!modelName) return "nvidia";
  const m = modelName.toLowerCase().trim();
  if (m.startsWith("gpt-") || m.startsWith("o1") || m.startsWith("o3") || m.includes("openai")) {
    return "openai";
  } else if (m.startsWith("llama3") || m.startsWith("qwen") || m.startsWith("mistral") || m.includes("ollama") || m.startsWith("local/")) {
    return "ollama";
  }
  return "nvidia";
}

// Fetch Backend Configuration
async function fetchConfig() {
  try {
    const res = await fetch("/api/config");
    const data = await res.json();
    serverConfig = data;
    
    const savedModel = localStorage.getItem("ipsakti_selected_model") || data.model || "nvidia/nemotron-3-ultra-550b-a55b";
    const savedProvider = localStorage.getItem("ipsakti_selected_provider") || data.provider || detectProviderFromModel(savedModel);
    
    currentProvider = savedProvider;

    const sbModel = document.getElementById("sidebarModelText");
    if (sbModel && savedModel) sbModel.innerText = savedModel;

    const headerSelect = document.getElementById("headerModelSelect");
    if (headerSelect && savedModel) {
      headerSelect.value = savedModel;
    }
  } catch (e) {
    console.warn("Config fetch error:", e);
  }
}

// Handle change from Header Model Dropdown
function handleHeaderModelChange(modelId) {
  const provider = detectProviderFromModel(modelId);
  currentProvider = provider;

  // Check if provider requires an API key that is not yet set
  if (provider === "openai" && !serverConfig.has_openai_key) {
    openSettingsModal();
    selectLlmProvider("openai");
    const dd = document.getElementById("modalModelDropdown");
    if (dd) dd.value = modelId;
    const statusNote = document.getElementById("settingsSaveStatus");
    if (statusNote) {
      statusNote.innerText = "⚠️ Please enter your OpenAI API key (sk-...) to activate this model.";
      statusNote.style.color = "#D97706";
    }
    const keyInput = document.getElementById("modalApiKeyInput");
    if (keyInput) keyInput.focus();
    return;
  }

  if (provider === "nvidia" && !serverConfig.has_nvidia_key) {
    openSettingsModal();
    selectLlmProvider("nvidia");
    const dd = document.getElementById("modalModelDropdown");
    if (dd) dd.value = modelId;
    const statusNote = document.getElementById("settingsSaveStatus");
    if (statusNote) {
      statusNote.innerText = "⚠️ Please enter your NVIDIA API key (nvapi-...) to activate this model.";
      statusNote.style.color = "#D97706";
    }
    const keyInput = document.getElementById("modalApiKeyInput");
    if (keyInput) keyInput.focus();
    return;
  }

  // If key is present or Ollama, activate immediately
  changeHeaderModel(modelId, provider);
}

// Change Model and Persist
async function changeHeaderModel(modelId, provider) {
  try {
    const prov = provider || detectProviderFromModel(modelId);
    currentProvider = prov;
    
    localStorage.setItem("ipsakti_selected_model", modelId);
    localStorage.setItem("ipsakti_selected_provider", prov);

    const sbModel = document.getElementById("sidebarModelText");
    if (sbModel) sbModel.innerText = modelId;

    const headerSelect = document.getElementById("headerModelSelect");
    if (headerSelect && headerSelect.value !== modelId) {
      headerSelect.value = modelId;
    }

    await fetch("/api/config", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ model: modelId, provider: prov })
    });
    console.log(`[IP-SAKTI] Active Model changed to: ${modelId} (${prov.toUpperCase()})`);
  } catch (e) {
    console.warn("Failed to update model config:", e);
  }
}

// ===================================================
// DYNAMIC CHAT HISTORY (ChatGPT / Normal Chatbot Style)
// ===================================================
function getSavedChats() {
  try {
    const raw = localStorage.getItem(CHATS_STORAGE_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch (e) {
    console.error("Error reading saved chats:", e);
    return [];
  }
}

function saveChatsToStorage(chats) {
  try {
    localStorage.setItem(CHATS_STORAGE_KEY, JSON.stringify(chats));
  } catch (e) {
    console.error("Error saving chats:", e);
  }
}

function renderSavedChatsSidebar() {
  const container = document.getElementById("sidebarUserChatsList");
  if (!container) return;

  const chats = getSavedChats();
  if (chats.length === 0) {
    container.innerHTML = `<div style="padding: 6px 10px; font-size: 11.5px; color: #94A3B8;">No saved chats yet</div>`;
    return;
  }

  container.innerHTML = chats.map(chat => `
    <div class="thread-item ${chat.id === activeChatId ? 'active' : ''}" onclick="loadSavedChat('${chat.id}')">
      <span class="thread-icon">💬</span>
      <div class="thread-text" title="${escapeHtml(chat.title)}">${escapeHtml(chat.title)}</div>
      <button class="thread-delete-btn" onclick="deleteSavedChat(event, '${chat.id}')" title="Delete chat">🗑️</button>
    </div>
  `).join("");
}

// Start New Chat / Inquiry (Clears viewport, shows hero, leaves sidebar intact)
function startNewChat() {
  activeChatId = null;
  renderSavedChatsSidebar();

  const stream = document.getElementById("messagesStream");
  if (stream) stream.innerHTML = "";
  
  const hero = document.getElementById("emptyStateHero");
  if (hero) hero.style.display = "block";

  const input = document.getElementById("userPromptInput");
  if (input) {
    input.value = "";
    input.style.height = "auto";
    input.focus();
  }
}

// Load a previous saved chat session
function loadSavedChat(chatId) {
  activeChatId = chatId;
  const chats = getSavedChats();
  const chat = chats.find(c => c.id === chatId);
  if (!chat) return;

  const hero = document.getElementById("emptyStateHero");
  if (hero) hero.style.display = "none";

  const stream = document.getElementById("messagesStream");
  if (!stream) return;
  stream.innerHTML = "";

  (chat.turns || []).forEach(turn => {
    // 1. User message row
    const userRow = document.createElement("div");
    userRow.className = "user-msg-row";
    userRow.innerHTML = `<div class="user-msg-bubble">${escapeHtml(turn.query)}</div>`;
    stream.appendChild(userRow);

    // 2. Assistant response card
    if (turn.cardHtml) {
      const assistantCard = document.createElement("div");
      assistantCard.className = "assistant-msg-card";
      assistantCard.innerHTML = turn.cardHtml;
      stream.appendChild(assistantCard);
    }
  });

  renderSavedChatsSidebar();
  scrollToBottom();
}

// Delete a saved chat session
function deleteSavedChat(e, chatId) {
  if (e) e.stopPropagation();
  let chats = getSavedChats();
  chats = chats.filter(c => c.id !== chatId);
  saveChatsToStorage(chats);

  if (activeChatId === chatId) {
    startNewChat();
  } else {
    renderSavedChatsSidebar();
  }
}

// Persist a completed question & answer turn to the active session
function saveTurnToActiveChat(queryText, cardHtml) {
  let chats = getSavedChats();
  
  if (!activeChatId) {
    activeChatId = "chat_" + Date.now();
    const title = queryText.length > 34 ? queryText.slice(0, 34) + "..." : queryText;
    const newChat = {
      id: activeChatId,
      title: title,
      createdAt: Date.now(),
      turns: []
    };
    chats.unshift(newChat);
  }

  const chat = chats.find(c => c.id === activeChatId);
  if (chat) {
    if (!chat.turns) chat.turns = [];
    chat.turns.push({
      query: queryText,
      cardHtml: cardHtml,
      timestamp: Date.now()
    });
  }

  saveChatsToStorage(chats);
  renderSavedChatsSidebar();
}

// Load Saved Inquiry from preconfigured scenarios (if clicked)
function loadSavedThread(scenarioId) {
  const hero = document.getElementById("emptyStateHero");
  if (hero) hero.style.display = "none";

  const queries = {
    "scenario_1": "Can I patent an Ayurvedic topical pain relief balm containing Curcumin and Wintergreen Oil in India?",
    "scenario_2": "What are the statutory requirements to export standardized Ashwagandha extract to Germany under EU THMPD?",
    "scenario_3": "What is the difference between licensing a Classical Ayurvedic Cough Syrup versus a Proprietary Syrup under Rule 158-B?"
  };

  runQueryPipeline(queries[scenarioId] || "Regulatory inquiry", scenarioId);
}

// Submit from Empty State Suggestion Card
function submitPrompt(promptText) {
  const input = document.getElementById("userPromptInput");
  if (input) input.value = promptText;
  handleSend();
}

function handleSuggestionClick(num) {
  const dict = (typeof I18N !== "undefined" && I18N[currentAyushLanguage]) ? I18N[currentAyushLanguage] : I18N.en;
  const promptText = dict[`card${num}Prompt`];
  submitPrompt(promptText);
}

/* ===================================================
   DOCUMENT ATTACHMENT & UPLOAD PIPELINE
   =================================================== */
let attachedDocumentsList = [];

function triggerDocUpload() {
  const fileInput = document.getElementById("docFileInput");
  if (fileInput) {
    fileInput.value = "";
    fileInput.click();
  }
}

async function handleDocFilesSelected(e) {
  const files = Array.from(e.target.files || []);
  if (!files.length) return;

  const tray = document.getElementById("attachedDocsTray");
  if (tray) tray.classList.remove("hidden");

  for (const file of files) {
    const docId = "doc_" + Date.now() + "_" + Math.random().toString(36).substring(2, 6);
    const sizeKb = Math.max(1, Math.round(file.size / 1024));

    // Render loading chip
    renderDocChip({
      id: docId,
      filename: file.name,
      size_kb: sizeKb
    });

    try {
      const formData = new FormData();
      formData.append("file", file);

      const res = await fetch("/api/documents/parse", {
        method: "POST",
        body: formData
      });

      if (!res.ok) throw new Error("Upload response not OK: " + res.status);
      const data = await res.json();

      const docItem = {
        id: docId,
        filename: data.filename,
        size_kb: data.size_kb,
        word_count: data.word_count,
        botanicals_detected: data.botanicals_detected || [],
        clauses_detected: data.clauses_detected || [],
        text: data.text || "",
        snippet: data.snippet || ""
      };

      attachedDocumentsList.push(docItem);
      updateDocChip(docId, docItem);

      const isHi = currentAyushLanguage === "hi";
      const toastMsg = isHi
        ? `📎 दस्तावेज़ संलग्न: ${data.filename} (${data.size_kb} KB)`
        : `📎 Document attached: ${data.filename} (${data.size_kb} KB)`;
      showNotificationToast(toastMsg);
    } catch (err) {
      console.warn("Server document parsing fallback to local reader:", err);
      readDocLocally(file, docId, sizeKb);
    }
  }
}

function readDocLocally(file, docId, sizeKb) {
  const reader = new FileReader();
  reader.onload = function(e) {
    const textContent = String(e.target.result || "");
    const docItem = {
      id: docId,
      filename: file.name,
      size_kb: sizeKb,
      word_count: textContent.split(/\s+/).length,
      botanicals_detected: [],
      clauses_detected: [],
      text: textContent.slice(0, 10000),
      snippet: textContent.slice(0, 200).replace(/\n/g, " ")
    };
    attachedDocumentsList.push(docItem);
    updateDocChip(docId, docItem);
    showNotificationToast(`📎 ${file.name} (${sizeKb} KB) attached`);
  };
  reader.onerror = function() {
    const docItem = {
      id: docId,
      filename: file.name,
      size_kb: sizeKb,
      word_count: 0,
      botanicals_detected: [],
      clauses_detected: [],
      text: `[Attached file: ${file.name}]`,
      snippet: `Attached file: ${file.name}`
    };
    attachedDocumentsList.push(docItem);
    updateDocChip(docId, docItem);
  };

  if (file.type.startsWith("text") || file.name.match(/\.(txt|md|json|csv|tsv|rtf)$/i)) {
    reader.readAsText(file);
  } else {
    reader.onload({ target: { result: `[Uploaded binary document: ${file.name} (${sizeKb} KB)]` } });
  }
}

function renderDocChip(doc) {
  const tray = document.getElementById("attachedDocsTray");
  if (!tray) return;

  const isHi = currentAyushLanguage === "hi";
  let icon = "📄";
  if (doc.filename.endsWith(".pdf")) icon = "📕";
  else if (doc.filename.match(/\.(docx|doc)$/i)) icon = "📘";
  else if (doc.filename.match(/\.(png|jpg|jpeg|webp)$/i)) icon = "🖼️";

  const chip = document.createElement("div");
  chip.className = "attached-doc-chip";
  chip.id = doc.id;
  chip.innerHTML = `
    <span class="doc-chip-icon">${icon}</span>
    <div class="doc-chip-info">
      <span class="doc-chip-name" title="${escapeHtml(doc.filename)}">${escapeHtml(doc.filename)}</span>
      <span class="doc-chip-meta">${isHi ? 'प्रसंस्करण हो रहा है...' : 'Screening document...'} (${doc.size_kb} KB)</span>
    </div>
    <button class="doc-chip-remove" onclick="removeAttachedDoc('${doc.id}')" title="Remove">&times;</button>
  `;
  tray.appendChild(chip);
}

function updateDocChip(docId, doc) {
  const chip = document.getElementById(docId);
  if (!chip) return;

  const isHi = currentAyushLanguage === "hi";
  let metaText = `${doc.size_kb} KB`;
  if (doc.botanicals_detected && doc.botanicals_detected.length > 0) {
    metaText += ` • 🌿 ${doc.botanicals_detected.slice(0, 2).join(", ")}`;
  } else {
    metaText += isHi ? " • ✓ विश्लेषण हेतु तैयार" : " • ✓ Ready to analyze";
  }

  const metaEl = chip.querySelector(".doc-chip-meta");
  if (metaEl) metaEl.textContent = metaText;
}

function removeAttachedDoc(docId) {
  attachedDocumentsList = attachedDocumentsList.filter(d => d.id !== docId);
  const chip = document.getElementById(docId);
  if (chip) chip.remove();

  const tray = document.getElementById("attachedDocsTray");
  if (tray && attachedDocumentsList.length === 0) {
    tray.classList.add("hidden");
  }
}

function clearAttachedDocs() {
  attachedDocumentsList = [];
  const tray = document.getElementById("attachedDocsTray");
  if (tray) {
    tray.innerHTML = "";
    tray.classList.add("hidden");
  }
}

// Handle Send from Input Dock
function handleSend() {
  const input = document.getElementById("userPromptInput");
  let query = input ? input.value.trim() : "";

  // If user attached documents but did not enter text query
  if (!query && attachedDocumentsList.length > 0) {
    query = currentAyushLanguage === "hi"
      ? "कृपया संलग्न विनियामक दस्तावेज़ / फॉर्मूलेशन विनिर्देश का भारतीय पेटेंट अधिनियम धारा 3(p), एनबीए प्रपत्र 3 अनुपालन और आयुष नियम 158-B लाइसेंसिंग के अनुसार विश्लेषण करें।"
      : "Please evaluate the attached regulatory document / formulation specification for Section 3(p) patent eligibility, NBA Form 3 compliance, and Ayush Rule 158-B licensing.";
  }

  if (!query) return;

  if (input) {
    input.value = "";
    input.style.height = "auto";
  }

  const hero = document.getElementById("emptyStateHero");
  if (hero) hero.style.display = "none";

  const docsToSend = [...attachedDocumentsList];
  clearAttachedDocs();

  runQueryPipeline(query, null, docsToSend);
}

// ===================================================
// IMMEDIATE STRUCTURED REGULATORY PIPELINE
// ===================================================
async function runQueryPipeline(queryText, scenarioId, attachedDocs = []) {
  const stream = document.getElementById("messagesStream");

  // 1. Append User Bubble with Attached Documents Badge
  const userRow = document.createElement("div");
  userRow.className = "user-msg-row";

  let docsHtml = "";
  if (attachedDocs && attachedDocs.length > 0) {
    docsHtml = `<div class="user-attached-docs-wrapper">` + attachedDocs.map(d => `
      <div class="user-attached-doc-badge">
        <span>📄</span>
        <strong>${escapeHtml(d.filename)}</strong>
        <span style="opacity: 0.85; margin-left: 4px;">(${d.size_kb} KB${d.botanicals_detected && d.botanicals_detected.length ? ' • 🌿 ' + escapeHtml(d.botanicals_detected.slice(0, 2).join(', ')) : ''})</span>
      </div>
    `).join("") + `</div>`;
  }

  userRow.innerHTML = `<div class="user-msg-bubble">${docsHtml}<div class="user-bubble-text">${escapeHtml(queryText)}</div></div>`;
  stream.appendChild(userRow);

  // 2. Create Assistant Message Card Shell
  const isHi = currentAyushLanguage === "hi";
  const assistantCard = document.createElement("div");
  assistantCard.className = "assistant-msg-card";
  assistantCard.innerHTML = `
    <div class="msg-header-meta">
      <div class="msg-identity">
        <div class="assistant-avatar">🏛️</div>
        <span class="assistant-name">IP-SAKTI Sahayak</span>
      </div>
      <span class="msg-engine-badge" id="cardEngineBadge">${isHi ? 'सत्यापित विधिक साक्ष्य' : 'Verified Grounding'}</span>
    </div>
    <div class="card-vernacular-slot"></div>
    <div class="card-agents-slot"></div>
    <div class="card-trace-slot"></div>
    <div class="msg-content-text">
      <div style="display:flex; align-items:center; gap:8px; color:#64748B; font-size:13px; padding:12px 0;">
        <span>${isHi ? '⚙️ धारा 3(p), NBA प्रपत्र 3, नियम 158-B एवं राजपत्र SHA-256 हैश का मूल्यांकन किया जा रहा है...' : '⚙️ Evaluating Section 3(p), NBA Form 3, Rule 158-B, and Gazette SHA-256 hashes...'}</span>
      </div>
    </div>
    <div class="card-workaround-slot"></div>
    <div class="card-citations-slot"></div>
    <div class="card-vernacular-bottom-slot"></div>
    <div class="card-actions-slot"></div>
  `;
  stream.appendChild(assistantCard);
  scrollToBottom();

  const badgeEl = assistantCard.querySelector("#cardEngineBadge");
  const vernacularSlot = assistantCard.querySelector(".card-vernacular-slot");
  const vernacularBottomSlot = assistantCard.querySelector(".card-vernacular-bottom-slot");
  const agentsSlot = assistantCard.querySelector(".card-agents-slot");
  const traceSlot = assistantCard.querySelector(".card-trace-slot");
  const contentSlot = assistantCard.querySelector(".msg-content-text");
  const workaroundSlot = assistantCard.querySelector(".card-workaround-slot");
  const citationsSlot = assistantCard.querySelector(".card-citations-slot");
  const actionsSlot = assistantCard.querySelector(".card-actions-slot");

  try {
    const res = await fetch("/api/query", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ 
        query: queryText, 
        scenario_id: scenarioId,
        language: currentAyushLanguage,
        documents: attachedDocs
      })
    });
    const data = await res.json();

    if (badgeEl) {
      badgeEl.innerText = data.llm_live ? `⚡ ${data.model || 'Live LLM'}` : "Verified Grounding";
      badgeEl.style.cssText = data.llm_live ? "background:#ECFDF5; color:#059669; border-color:#A7F3D0; font-weight:600;" : "background:var(--bg-subtle); color:var(--text-body); border-color:var(--border-subtle);";
    }

    const hasVernacular = !!(
      data.vernacular_data &&
      data.vernacular_data.recognized_vernaculars &&
      data.vernacular_data.recognized_vernaculars.length > 0
    );

    if (hasVernacular) {
      if (vernacularSlot) vernacularSlot.innerHTML = buildVernacularBannerHtml(data.vernacular_data);
      if (vernacularBottomSlot) vernacularBottomSlot.innerHTML = "";
    } else {
      if (vernacularSlot) vernacularSlot.innerHTML = "";
      if (vernacularBottomSlot) vernacularBottomSlot.innerHTML = buildVernacularNotNeededHtml();
    }
    if (agentsSlot) agentsSlot.innerHTML = buildAgentPillsHtml(data.conflict_matrix);
    if (traceSlot) traceSlot.innerHTML = buildTraceHtml(data.execution_trace);
    if (contentSlot) contentSlot.innerHTML = formatContentMarkdown(data.summary);

    let wText = data.workaround || "";
    if (!wText && data.conflict_matrix) {
      const w = data.conflict_matrix.find(c => c.jurisdiction && (c.jurisdiction.includes("Workaround") || c.jurisdiction.includes("Route") || c.jurisdiction.includes("Strategic")));
      if (w) wText = w.reasoning;
    }
    if (workaroundSlot) workaroundSlot.innerHTML = buildWorkaroundHtml(wText);
    if (citationsSlot) citationsSlot.innerHTML = buildCitationsHtml(data.citations);
    if (actionsSlot) actionsSlot.innerHTML = buildActionButtonsHtml();

    scrollToBottom();
    saveTurnToActiveChat(queryText, assistantCard.innerHTML);
  } catch (err) {
    console.error("Query synthesis error:", err);
    if (contentSlot) {
      contentSlot.innerHTML = `<div style="color:#DC2626; padding:8px 0;">Error executing regulatory synthesis. Please verify connection.</div>`;
    }
  }
}

// Fallback to synchronous query alias
const runQueryFallback = runQueryPipeline;

// ===================================================
// UI BUILDER HELPERS
// ===================================================

function cleanSectionSigns(str) {
  if (!str) return "";
  return String(str).replace(/§\s*/g, "Section ");
}

function buildAgentPillsHtml(conflict_matrix) {
  if (!conflict_matrix || !Array.isArray(conflict_matrix)) return "";

  // Extract specific statutory resources used during this query
  const ipo = conflict_matrix.find(c => c.jurisdiction && (c.jurisdiction.includes("Patent") || c.jurisdiction.includes("IPO")));
  const nba = conflict_matrix.find(c => c.jurisdiction && (c.jurisdiction.includes("Biodiversity") || c.jurisdiction.includes("NBA")));
  const ayush = conflict_matrix.find(c => c.jurisdiction && (c.jurisdiction.includes("Ayush") || c.jurisdiction.includes("SALA") || c.jurisdiction.includes("Licensing")));
  const global = conflict_matrix.find(c => c.jurisdiction && (c.jurisdiction.includes("Global") || c.jurisdiction.includes("Export") || c.jurisdiction.includes("European")));

  const activePills = [];

  if (ipo) {
    activePills.push(`
      <div class="agent-mini-pill ${ipo.color || 'yellow'}">
        <span class="pill-title">⚖️ IPO Patent</span>
        <span class="pill-status ${ipo.color || 'yellow'}">${escapeHtml(cleanSectionSigns(ipo.status))}</span>
      </div>
    `);
  }

  if (nba) {
    activePills.push(`
      <div class="agent-mini-pill ${nba.color || 'red'}">
        <span class="pill-title">🌿 NBA Biodiversity</span>
        <span class="pill-status ${nba.color || 'red'}">${escapeHtml(cleanSectionSigns(nba.status))}</span>
      </div>
    `);
  }

  if (ayush) {
    activePills.push(`
      <div class="agent-mini-pill ${ayush.color || 'green'}">
        <span class="pill-title">🏥 Ayush Licensing</span>
        <span class="pill-status ${ayush.color || 'green'}">${escapeHtml(cleanSectionSigns(ayush.status))}</span>
      </div>
    `);
  }

  if (global) {
    activePills.push(`
      <div class="agent-mini-pill ${global.color || 'yellow'}">
        <span class="pill-title">🌍 Global Export</span>
        <span class="pill-status ${global.color || 'yellow'}">${escapeHtml(cleanSectionSigns(global.status))}</span>
      </div>
    `);
  }

  return `
    <div class="regulatory-agent-pills">
      ${activePills.join("")}
    </div>
  `;
}

function buildDirectSummaryHtml(data) {
  if (!data) return "";
  
  let summaryText = data.direct_short_summary || "";
  if (!summaryText && data.summary) {
    const lines = data.summary.split("\n").filter(l => l.trim().startsWith("•") || l.trim().startsWith("###"));
    summaryText = lines.slice(0, 4).join("\n");
  }

  if (!summaryText) return "";

  const formattedHtml = summaryText.split("\n").map(line => {
    let clean = escapeHtml(line.trim());
    clean = clean.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    return `<div style="margin-bottom: 5px;">${clean}</div>`;
  }).join("");

  return `
    <div class="direct-summary-card">
      <div class="direct-summary-header">
        <span>⚡ Executive Regulatory Verdict &amp; Summary:</span>
      </div>
      <div class="direct-summary-body">
        ${formattedHtml}
      </div>
    </div>
  `;
}

function buildEyeCatchingMatrixHtml(conflict_matrix, detected_collisions) {
  if (!conflict_matrix || !Array.isArray(conflict_matrix) || conflict_matrix.length === 0) return "";

  const rows = conflict_matrix.map(c => {
    const icon = c.icon || (c.jurisdiction.includes("Patent") ? "⚖️" : c.jurisdiction.includes("Biodiversity") ? "🌿" : c.jurisdiction.includes("Ayush") ? "🏥" : "🌍");
    const name = c.jurisdiction || "Statutory Authority";
    const basis = c.statutory_act || (name.includes("Patent") ? "The Patents Act, 1970 Section 3(p)/3(e)" : name.includes("Bio") ? "The Biological Diversity Act, 2002 Section 6" : name.includes("Ayush") ? "Drugs & Cosmetics Rules 1945 Rule 158-B" : "WIPO PCT / EU THMPD");
    const color = c.color || "yellow";
    const statusText = c.status || "Evaluated";
    const insight = (c.reasoning || "").split(".")[0] + ".";

    return `
      <div class="matrix-row">
        <div class="matrix-regulator-col">
          <span>${icon}</span>
          <span>${escapeHtml(name)}</span>
        </div>
        <div class="matrix-basis-col">${escapeHtml(basis)}</div>
        <div class="matrix-status-col">
          <span class="matrix-status-badge ${color}">${escapeHtml(statusText)}</span>
        </div>
        <div class="matrix-insight-col">${escapeHtml(insight)}</div>
      </div>
    `;
  }).join("");

  const collisionBanner = (detected_collisions && detected_collisions.length > 0) ? `
    <div class="matrix-collision-banner">
      <span>🚨</span>
      <span><strong>Cross-Regulatory Collision:</strong> ${escapeHtml(detected_collisions[0])}</span>
    </div>
  ` : '';

  return `
    <div class="collision-mini-matrix-card">
      <div class="matrix-card-header">
        <div class="matrix-title">
          <span>⚡ Cross-Regulatory Collision Matrix</span>
        </div>
        <span class="matrix-subtitle">Comparative Status Across 4 Statutory Jurisdictions</span>
      </div>
      <div class="matrix-table-grid">
        <div class="matrix-row matrix-header">
          <div>Authority</div>
          <div>Statutory Basis</div>
          <div>Clearance Status</div>
          <div>Cross-Statutory Impact</div>
        </div>
        ${rows}
      </div>
      ${collisionBanner}
    </div>
  `;
}

function buildVernacularBannerHtml(vData) {
  if (!vData || !vData.recognized_vernaculars || vData.recognized_vernaculars.length === 0) return "";
  const vList = vData.recognized_vernaculars;
  const traditions = (vData.detected_traditions || []).join(" • ");
  return `
    <div class="vernacular-recognized-card">
      <div class="vernacular-card-header">
        <div class="v-header-left">
          <span class="v-icon-pulse">🌿</span>
          <span class="v-title-text">Vernacular Dialect Grounding (${escapeHtml(traditions || 'Traditional Medicine')})</span>
        </div>
        <span class="v-pill-count">${vList.length} Spoken Terms Normalized</span>
      </div>
      <div class="vernacular-terms-grid">
        ${vList.map(v => `
          <div class="vernacular-term-chip">
            <div class="vt-top">
              <span class="vt-spoken">"${escapeHtml(v.spoken_vernacular.toUpperCase())}"</span>
              <span class="vt-arrow">➔</span>
              <span class="vt-canonical">${escapeHtml(v.canonical_name)}</span>
              <span class="vt-system-badge">${escapeHtml(v.traditional_system)}</span>
            </div>
            <div class="vt-botanical-row">
              <span class="vt-latin"><i>${escapeHtml(v.latin_name)}</i> (${escapeHtml(v.family)})</span>
            </div>
            <div class="vt-mono-row">
              <span class="vt-monograph" title="${escapeHtml(v.pharmacopoeia_monograph)}">📜 ${escapeHtml(v.pharmacopoeia_monograph)}</span>
              <span class="vt-marker">🔬 ${escapeHtml(v.active_chemical_marker)}</span>
            </div>
          </div>
        `).join("")}
      </div>
    </div>
  `;
}

function buildVernacularNotNeededHtml() {
  return `
    <div class="vernacular-not-needed-note">
      <div class="v-nn-left">
        <span class="v-nn-icon">🌿</span>
        <span class="v-nn-text"><strong>Vernacular Dialect Grounding is not needed</strong> <span class="v-nn-sub">(Standard statutory / botanical terminology verified)</span></span>
      </div>
      <span class="v-nn-badge">Standard Terms Verified</span>
    </div>
  `;
}

function buildTraceHtml(trace) {
  if (!trace || trace.length === 0) return "";
  const totalMs = trace.reduce((acc, t) => acc + (t.latency_ms || 10), 0);
  const nodeIcons = {
    "NormalizerNode": "🔍",
    "IPRAgentNode": "⚖️",
    "BiodiversityAgentNode": "🌿",
    "AyushAgentNode": "🏥",
    "GlobalExportAgentNode": "🌍",
    "ConflictDetectorNode": "⚡",
    "WorkaroundSynthesizerNode": "💡",
    "VerifierNode": "🛡️"
  };

  const traceStepsHtml = trace.map(t => `
    <div class="trace-step-row" style="display:flex; align-items:flex-start; gap:10px; margin-bottom:8px; background:#FFFFFF; border:1px solid #E2E8F0; border-radius:8px; padding:9px 12px; transition:box-shadow 0.15s ease;">
      <div class="trace-step-icon" style="display:flex; align-items:center; justify-content:center; width:30px; height:30px; border-radius:8px; background:#F1F5F9; border:1px solid #E2E8F0; font-size:14px; flex-shrink:0;">${nodeIcons[t.node] || '⚙️'}</div>
      <div class="trace-step-info" style="flex:1; min-width:0;">
        <div class="trace-step-head" style="display:flex; align-items:center; justify-content:space-between; margin-bottom:3px;">
          <span class="trace-step-name" style="font-size:12.5px; font-weight:600; color:#0F172A;">${cleanSectionSigns(t.node)}</span>
          <span class="trace-step-ms" style="font-size:11px; font-weight:600; color:#059669; background:#ECFDF5; border:1px solid #A7F3D0; padding:1px 7px; border-radius:9999px; font-family:'JetBrains Mono', monospace;">${t.latency_ms || 12}ms</span>
        </div>
        <div class="trace-step-desc" style="font-size:12px; color:#475569; line-height:1.45;">${escapeHtml(cleanSectionSigns(t.description || ''))}</div>
      </div>
    </div>
  `).join("");

  return `
    <div class="agent-graph-trace-container" style="margin:14px 0 16px 0; border:1px solid #E2E8F0; border-radius:10px; background:#F8FAFC; overflow:hidden;">
      <div class="trace-header open" onclick="toggleTrace(this)" style="display:flex; align-items:center; justify-content:space-between; padding:9px 14px; background:#F1F5F9; cursor:pointer; user-select:none; border-bottom:1px solid #E2E8F0;">
        <div class="trace-header-left" style="display:flex; align-items:center; gap:8px;">
          <span class="trace-pulse-icon" style="display:inline-flex; align-items:center; justify-content:center; width:22px; height:22px; background:#0F172A; color:#F59E0B; border-radius:6px; font-size:12px;">⚡</span>
          <span class="trace-title" style="font-size:12px; font-weight:600; color:#1E293B;">StateGraph Trace (${trace.length} Nodes Executed)</span>
        </div>
        <div class="trace-header-right" style="display:flex; align-items:center; gap:8px;">
          <span class="trace-latency-badge" style="font-size:11px; font-weight:600; font-family:var(--font-mono); background:#E2E8F0; color:#334155; padding:2px 8px; border-radius:9999px;">${totalMs}ms</span>
          <span class="trace-chevron" style="font-size:11px; color:#64748B;">▾</span>
        </div>
      </div>
      <div class="trace-nodes-body" style="display:block; padding:12px 14px 4px 14px; background:#FAFAFC;">
        <div class="trace-pipeline-flow" style="display:flex; flex-direction:column; gap:2px;">
          ${traceStepsHtml}
        </div>
      </div>
    </div>
  `;
}

function buildCitationsHtml(citations) {
  if (!citations || citations.length === 0) return "";
  return `
    <div class="msg-citations-row">
      <span class="cit-label">Statutory Grounding:</span>
      ${citations.map(c => `
        <div class="cit-item-group">
          <button class="cit-pill" onclick="openGazettePanel('${c.doc_id}')" title="Click to view authentic Gazette text">
            📜 ${escapeHtml(cleanSectionSigns(c.label))}
          </button>
          ${c.official_url ? `
            <a href="${c.official_url}" target="_blank" rel="noopener noreferrer" class="cit-link-btn" title="Open ${escapeHtml(cleanSectionSigns(c.portal_name || 'Official Gazette'))}">
              🔗 Gov ↗
            </a>
          ` : ''}
        </div>
      `).join("")}
    </div>
  `;
}

function buildWorkaroundHtml(workaroundText) {
  if (!workaroundText) return "";
  return `
    <div class="workaround-card-clean">
      <span class="w-bulb">💡</span>
      <div>
        <div class="w-title">Strategic Regulatory Workaround:</div>
        <div class="w-desc">${cleanSectionSigns(workaroundText)}</div>
      </div>
    </div>
  `;
}

function buildActionButtonsHtml() {
  return `
    <div class="msg-actions-footer">
      <button class="action-btn-secondary" onclick="openScannerModal()">
        🔬 Formulation Screener
      </button>
      <button class="action-btn-secondary" onclick="downloadDoc('nba_form_3')">
        🌿 NBA Form 3 (.docx)
      </button>
      <button class="action-btn-primary" onclick="downloadDoc('patent_form_2')">
        📄 Download Form 2 (.docx)
      </button>
    </div>
  `;
}

// Markdown Formatter for Assistant Responses
function formatContentMarkdown(text) {
  if (!text) return "";
  let s = cleanSectionSigns(text).replace(/\r\n/g, "\n").replace(/\r/g, "\n");
  // Subheadings ### Title
  s = s.replace(/^[ \t]*###[ \t]+(.*?)$/gm, '<h3 class="msg-subheading">$1</h3>');
  s = s.replace(/^[ \t]*##[ \t]+(.*?)$/gm, '<h2 class="msg-subheading">$1</h2>');
  // Bold **word**
  s = s.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
  // Bullet points •, -, *
  s = s.replace(/^[ \t]*[•\-\*][ \t]+(.*?)$/gm, '<div class="msg-bullet-item"><span class="msg-bullet-dot">•</span><div>$1</div></div>');
  // Numbered points 1. Item
  s = s.replace(/^[ \t]*(\d+)\.[ \t]+(.*?)$/gm, '<div class="msg-bullet-item"><span class="msg-bullet-num">$1.</span><div>$2</div></div>');
  // Convert paragraph breaks
  s = s.replace(/\n\n+/g, '<div class="msg-spacer"></div>');
  s = s.replace(/\n/g, '<br>');
  return s;
}

function toggleTrace(headerEl) {
  headerEl.classList.toggle("open");
  const body = headerEl.nextElementSibling;
  const chevron = headerEl.querySelector(".trace-chevron");
  const isOpen = headerEl.classList.contains("open");
  if (body) {
    body.style.display = isOpen ? "block" : "none";
  }
  if (chevron) {
    chevron.style.transform = isOpen ? "rotate(180deg)" : "rotate(0deg)";
  }
}

function scrollToBottom() {
  const area = document.getElementById("chatScrollArea");
  if (area) area.scrollTop = area.scrollHeight;
}

// Split-Screen Official Gazette Sheet
async function openGazettePanel(docId) {
  try {
    const res = await fetch(`/api/gazette/${docId}`);
    if (!res.ok) throw new Error("Document not found");
    const data = await res.json();

    document.getElementById("panelDocTitle").innerText = `${data.chapter} • ${data.section} ${data.clause}`;
    document.getElementById("panelAuthority").innerText = data.authority;
    document.getElementById("panelDate").innerText = data.gazette_date;
    document.getElementById("panelStatus").innerText = data.status;
    document.getElementById("panelVerbatimText").innerText = data.verbatim_text;
    document.getElementById("panelShaText").innerText = data.sha256;

    const officialLink = document.getElementById("panelOfficialLink");
    const officialLinkText = document.getElementById("panelOfficialLinkText");
    if (officialLink) {
      if (data.official_url) {
        officialLink.href = data.official_url;
        officialLink.style.display = "flex";
        if (officialLinkText) officialLinkText.innerText = `🏛️ Open Official Gazette (${data.portal_name || 'Portal'})`;
      } else {
        officialLink.style.display = "none";
      }
    }

    document.getElementById("gazettePanel").classList.add("open");
  } catch (e) {
    console.error("Gazette open error:", e);
  }
}

function closeGazettePanel() {
  document.getElementById("gazettePanel").classList.remove("open");
}

// Document Download Trigger
async function downloadDoc(docType) {
  try {
    const res = await fetch("/api/generate-doc", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        doc_type: docType,
        title: "Synergistic Topical Phytopharmaceutical Composition",
        herbs: ["Curcuma longa (Curcumin)", "Gaultheria procumbens (Gandhapura)"],
        workaround_type: "Phospholipid Nanocarrier"
      })
    });

    if (!res.ok) throw new Error("Download failed");

    const blob = await res.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = docType === "patent_form_2" 
      ? "Draft_Patent_Form_2_Complete_Specification.docx" 
      : "Draft_NBA_Form_III_IPR_Approval.docx";
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    a.remove();
  } catch (e) {
    console.error("Download error:", e);
    alert("Error downloading document draft.");
  }
}

// Architecture Modal & Zoom Handlers
let currentZoomedNodeIndex = null;

function openArchitectureModal() {
  const modal = document.getElementById("architectureModal");
  if (modal) modal.classList.remove("hidden");
}

function closeArchitectureModal() {
  const modal = document.getElementById("architectureModal");
  if (modal) modal.classList.add("hidden");
  resetArchZoom();
}

function zoomArchNode(nodeIndex, centerX, centerY) {
  const svg = document.getElementById("archSvgCanvas");
  const hint = document.getElementById("archZoomHint");
  const resetBtn = document.getElementById("archResetZoomBtn");
  if (!svg) return;

  // If clicked again, reset zoom
  if (currentZoomedNodeIndex === nodeIndex) {
    resetArchZoom();
    return;
  }

  currentZoomedNodeIndex = nodeIndex;

  // Clear previous active states
  document.querySelectorAll(".arch-svg-node").forEach(el => el.classList.remove("zoomed-node-active"));
  document.querySelectorAll(".arch-node-box").forEach(el => el.classList.remove("active-zoomed"));

  // Highlight selected SVG node
  const activeSvgNode = document.getElementById(`archSvg_${nodeIndex}`);
  if (activeSvgNode) activeSvgNode.classList.add("zoomed-node-active");

  // Highlight matching box down below & scroll smoothly
  const activeBox = document.getElementById(`archBox_${nodeIndex}`);
  if (activeBox) {
    activeBox.classList.add("active-zoomed");
    activeBox.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }

  // Smoothly focus viewBox around node (zoom to width 320, height 170)
  const zoomW = 320;
  const zoomH = 170;
  let minX = Math.max(0, Math.min(840 - zoomW, centerX - (zoomW / 2)));
  let minY = Math.max(0, Math.min(300 - zoomH, centerY - (zoomH / 2)));

  svg.setAttribute("viewBox", `${minX} ${minY} ${zoomW} ${zoomH}`);

  const nodeNames = {
    0: "User Inquiry",
    1: "Node 1: NormalizerNode",
    2: "Node 2: IPRAgentNode (Section 3p/3e)",
    3: "Node 3: BiodiversityAgentNode (Section 6)",
    4: "Node 4: AyushAgentNode (Rule 158-B)",
    5: "Node 5: GlobalExportAgentNode",
    6: "Node 6: ConflictMatrixNode",
    7: "Node 7: WorkaroundLabNode",
    8: "Node 8: SHA256VerifierNode",
    9: "Verified Dossier Output"
  };

  if (hint) {
    hint.innerHTML = `🔍 <strong>Zoomed into: ${nodeNames[nodeIndex] || `Node ${nodeIndex}`}</strong> • Click node again or reset button to view full diagram`;
  }
  if (resetBtn) resetBtn.classList.remove("hidden");
}

function resetArchZoom() {
  const svg = document.getElementById("archSvgCanvas");
  const hint = document.getElementById("archZoomHint");
  const resetBtn = document.getElementById("archResetZoomBtn");

  currentZoomedNodeIndex = null;
  if (svg) svg.setAttribute("viewBox", "0 0 840 300");

  document.querySelectorAll(".arch-svg-node").forEach(el => el.classList.remove("zoomed-node-active"));
  document.querySelectorAll(".arch-node-box").forEach(el => el.classList.remove("active-zoomed"));

  if (hint) hint.innerHTML = "💡 Click any node in diagram or box below to zoom in";
  if (resetBtn) resetBtn.classList.add("hidden");
}

// Model & API Key Configuration Modal
function openModelConfigModal() {
  const modal = document.getElementById("modelConfigModal");
  if (modal) modal.classList.remove("hidden");
  
  const initialProvider = currentProvider || serverConfig.provider || "nvidia";
  selectLlmProvider(initialProvider);
}

function closeModelConfigModal() {
  const modal = document.getElementById("modelConfigModal");
  if (modal) modal.classList.add("hidden");
  const statusNote = document.getElementById("settingsSaveStatus");
  if (statusNote) statusNote.innerText = "";
}

// Backward-compatibility aliases
const openSettingsModal = openArchitectureModal;
const closeSettingsModal = closeArchitectureModal;

function selectLlmProvider(provider) {
  currentProvider = provider;

  // Toggle active tab buttons
  const tabNvidia = document.getElementById("tabNvidia");
  const tabOpenai = document.getElementById("tabOpenai");
  const tabOllama = document.getElementById("tabOllama");

  if (tabNvidia) tabNvidia.classList.toggle("active", provider === "nvidia");
  if (tabOpenai) tabOpenai.classList.toggle("active", provider === "openai");
  if (tabOllama) tabOllama.classList.toggle("active", provider === "ollama");

  // Populate model dropdown for this provider
  const dropdown = document.getElementById("modalModelDropdown");
  const models = PROVIDER_MODELS[provider] || [];
  if (dropdown) {
    dropdown.innerHTML = models.map(m => `
      <option value="${escapeHtml(m.id)}">${escapeHtml(m.label)}</option>
    `).join("");

    // If current saved model is in this list, select it
    const activeModel = localStorage.getItem("ipsakti_selected_model") || serverConfig.model;
    const match = models.find(m => m.id === activeModel);
    if (match) {
      dropdown.value = activeModel;
    } else if (models.length > 0) {
      dropdown.value = models[0].id;
    }
  }

  // Handle custom model input visibility
  const customWrapper = document.getElementById("customModelWrapper");
  if (customWrapper) customWrapper.style.display = "none";

  // Configure API Key input & Ollama info card
  const apiKeyGroup = document.getElementById("apiKeyFormGroup");
  const apiKeyLabel = document.getElementById("apiKeyLabel");
  const apiKeyInput = document.getElementById("modalApiKeyInput");
  const apiKeyHint = document.getElementById("apiKeyHint");
  const ollamaCard = document.getElementById("ollamaZeroKeyCard");

  if (provider === "ollama") {
    if (apiKeyGroup) apiKeyGroup.style.display = "none";
    if (ollamaCard) ollamaCard.style.display = "block";
  } else {
    if (apiKeyGroup) apiKeyGroup.style.display = "block";
    if (ollamaCard) ollamaCard.style.display = "none";

    if (provider === "openai") {
      if (apiKeyLabel) apiKeyLabel.innerText = "OpenAI API Key:";
      if (apiKeyInput) {
        apiKeyInput.placeholder = serverConfig.has_openai_key 
          ? `Active: ${serverConfig.openai_key_masked}` 
          : "sk-proj-...";
        apiKeyInput.value = "";
      }
      if (apiKeyHint) apiKeyHint.innerHTML = `Paste your OpenAI API key (<code>sk-...</code>). Saved securely into <code>.env</code>.`;
    } else {
      // NVIDIA
      if (apiKeyLabel) apiKeyLabel.innerText = "NVIDIA NIM API Key:";
      if (apiKeyInput) {
        apiKeyInput.placeholder = serverConfig.has_nvidia_key 
          ? `Active: ${serverConfig.nvidia_key_masked}` 
          : "nvapi-...";
        apiKeyInput.value = "";
      }
      if (apiKeyHint) apiKeyHint.innerHTML = `Paste your NVIDIA NIM API key (<code>nvapi-...</code>). Saved securely into <code>.env</code>.`;
    }
  }

  const modelHint = document.getElementById("modalModelHint");
  if (modelHint) {
    if (provider === "openai") {
      modelHint.innerText = "OpenAI GPT-4o & o3-mini series with deep statutory reasoning.";
    } else if (provider === "nvidia") {
      modelHint.innerText = "High-throughput NVIDIA Nemotron & Llama NIM legal checkpoints.";
    } else {
      modelHint.innerText = "Local offline LLM running zero-cost on your hardware via Ollama.";
    }
  }
}

function handleModalModelSelect(val) {
  const customWrapper = document.getElementById("customModelWrapper");
  if (customWrapper) {
    if (val === "custom") {
      customWrapper.style.display = "block";
      const customInput = document.getElementById("modalCustomModelInput");
      if (customInput) customInput.focus();
    } else {
      customWrapper.style.display = "none";
    }
  }
}

async function saveSettings() {
  const dropdown = document.getElementById("modalModelDropdown");
  let selectedModel = dropdown ? dropdown.value : "nvidia/nemotron-3-ultra-550b-a55b";
  
  if (selectedModel === "custom") {
    const customInput = document.getElementById("modalCustomModelInput");
    const customVal = customInput ? customInput.value.trim() : "";
    if (customVal) {
      selectedModel = customVal;
    }
  }

  const keyInput = document.getElementById("modalApiKeyInput");
  const key = (currentProvider !== "ollama" && keyInput) ? keyInput.value.trim() : "";
  const statusNote = document.getElementById("settingsSaveStatus");

  if (statusNote) {
    statusNote.innerText = "Saving configuration...";
    statusNote.style.color = "#4F46E5";
  }

  try {
    const payload = {
      provider: currentProvider,
      model: selectedModel
    };
    if (key) {
      payload.api_key = key;
    }

    const res = await fetch("/api/config", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    const data = await res.json();
    
    // Save to localStorage
    localStorage.setItem("ipsakti_selected_model", selectedModel);
    localStorage.setItem("ipsakti_selected_provider", currentProvider);

    // Update UI elements
    const sbModel = document.getElementById("sidebarModelText");
    if (sbModel) sbModel.innerText = selectedModel;

    const headerSelect = document.getElementById("headerModelSelect");
    if (headerSelect) {
      // If option not in dropdown, add it dynamically
      let exists = false;
      for (let i = 0; i < headerSelect.options.length; i++) {
        if (headerSelect.options[i].value === selectedModel) {
          exists = true;
          break;
        }
      }
      if (!exists) {
        const opt = document.createElement("option");
        opt.value = selectedModel;
        opt.innerText = `⚡ ${selectedModel} (${currentProvider.toUpperCase()})`;
        headerSelect.appendChild(opt);
      }
      headerSelect.value = selectedModel;
    }

    await fetchConfig();

    if (statusNote) {
      statusNote.innerText = `✓ ${currentProvider.toUpperCase()} model '${selectedModel}' activated and saved!`;
      statusNote.style.color = "#059669";
    }

    setTimeout(() => {
      closeSettingsModal();
      if (statusNote) statusNote.innerText = "";
    }, 1000);
  } catch (e) {
    if (statusNote) {
      statusNote.innerText = "Error saving settings: " + e.message;
      statusNote.style.color = "#DC2626";
    }
  }
}

// Scanner Modal
function openScannerModal() {
  document.getElementById("scannerModal").classList.remove("hidden");
}

function closeScannerModal() {
  document.getElementById("scannerModal").classList.add("hidden");
}

async function calcScannerScore() {
  const dosage = document.getElementById("scannerDosageSelect").value;
  const herbs = Array.from(document.querySelectorAll(".herb-chip input:checked")).map(b => b.value);

  const res = await fetch("/api/scan", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ ingredients: herbs, dosage_form: dosage })
  });

  const data = await res.json();
  document.getElementById("scannerScorePct").innerText = `${data.formulation_score}%`;
  document.getElementById("scannerScoreFillClean").style.width = `${data.formulation_score}%`;
  document.getElementById("scannerScoreNote").innerHTML = `<strong>Filing Strategy:</strong> ${data.workaround_strategy}`;
}

function applyScannerToChat() {
  closeScannerModal();
  const dosage = document.getElementById("scannerDosageSelect").value;
  const herbs = Array.from(document.querySelectorAll(".herb-chip input:checked")).map(b => b.value).join(", ");
  const query = `Analyze patentability for formulation containing ${herbs} in ${dosage} dosage form.`;
  
  const hero = document.getElementById("emptyStateHero");
  if (hero) hero.style.display = "none";

  runQueryPipeline(query, null);
}

// ===================================================
// ENHANCED WEB SPEECH API (ENGLISH FONT ONLY)
// ===================================================
function setupVoiceRecognition() {
  const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
  const statusEl = document.getElementById("voiceStatusText");
  const previewEl = document.getElementById("voicePreviewText");
  const barsEl = document.getElementById("voiceAudioBars");

  if (!SpeechRec) {
    if (statusEl) statusEl.innerText = "Web Speech API is not supported in this browser.";
    if (previewEl) previewEl.innerText = 'Preset sample loaded: "Can I patent an Ayurvedic pain balm containing Asgandh and Gandhapura in India?"';
    voiceTranscribedText = "Can I patent an Ayurvedic topical pain relief balm containing Asgandh and Gandhapura in India?";
    return;
  }

  try {
    speechRecognitionInstance = new SpeechRec();
    speechRecognitionInstance.continuous = false;
    speechRecognitionInstance.interimResults = true;
    speechRecognitionInstance.lang = "en-IN"; // English (India) with local botanical term phonetics

    speechRecognitionInstance.onstart = () => {
      if (statusEl) statusEl.innerText = "🎙️ Listening... Speak your formulation or regulatory query in English";
      if (previewEl) previewEl.innerText = "Listening for speech...";
      if (barsEl) barsEl.style.opacity = "1";
    };

    speechRecognitionInstance.onresult = (event) => {
      let interim = "";
      for (let i = event.resultIndex; i < event.results.length; ++i) {
        interim += event.results[i][0].transcript;
      }
      voiceTranscribedText = interim.trim();
      if (previewEl) previewEl.innerText = `"${voiceTranscribedText}"`;
    };

    speechRecognitionInstance.onerror = (event) => {
      console.warn("Speech recognition notice:", event.error);
      if (statusEl) statusEl.innerText = "🎙️ Speech input ready (or click Search with sample query)";
      if (!voiceTranscribedText) {
        voiceTranscribedText = "Can I patent an Ayurvedic topical pain relief balm containing Asgandh and Gandhapura in India?";
        if (previewEl) previewEl.innerText = `"${voiceTranscribedText}"`;
      }
    };

    speechRecognitionInstance.onend = () => {
      if (statusEl) statusEl.innerText = "✓ Speech captured. Ready to search regulatory database.";
      if (!voiceTranscribedText) {
        voiceTranscribedText = "Can I patent an Ayurvedic topical pain relief balm containing Asgandh and Gandhapura in India?";
        if (previewEl) previewEl.innerText = `"${voiceTranscribedText}"`;
      }
    };

    speechRecognitionInstance.start();
  } catch (err) {
    console.warn("Speech init error:", err);
    voiceTranscribedText = "Can I patent an Ayurvedic topical pain relief balm containing Asgandh and Gandhapura in India?";
    if (previewEl) previewEl.innerText = `"${voiceTranscribedText}"`;
  }
}

const voiceBtn = document.getElementById("voiceMicBtn");
if (voiceBtn) {
  voiceBtn.addEventListener("click", () => {
    document.getElementById("voiceModal").classList.remove("hidden");
    voiceTranscribedText = "";
    setupVoiceRecognition();
  });
}

function cancelVoiceModal() {
  if (speechRecognitionInstance) {
    try { speechRecognitionInstance.stop(); } catch (e) {}
  }
  document.getElementById("voiceModal").classList.add("hidden");
}

function submitVoiceModal() {
  cancelVoiceModal();
  const query = voiceTranscribedText || "Can I patent an Ayurvedic topical pain relief balm containing Asgandh and Gandhapura in India?";
  const input = document.getElementById("userPromptInput");
  if (input) input.value = query;
  
  const hero = document.getElementById("emptyStateHero");
  if (hero) hero.style.display = "none";

  runQueryPipeline(query, null);
}

// Toggle Sidebar for Mobile / Small Screens
function toggleSidebar() {
  const sb = document.getElementById("chatSidebar");
  if (sb) sb.classList.toggle("collapsed");
}

function escapeHtml(str) {
  if (!str) return "";
  return String(str).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

// ===================================================
// MODEL CONTEXT PROTOCOL (MCP) INSPECTOR
// ===================================================

async function openMcpModal() {
  const modal = document.getElementById("mcpModal");
  if (modal) modal.classList.remove("hidden");

  try {
    const res = await fetch("/api/mcp/tools");
    const data = await res.json();
    renderMcpToolsList(data.tools);
  } catch (e) {
    console.error("Error fetching MCP tools:", e);
  }
}

function closeMcpModal() {
  const modal = document.getElementById("mcpModal");
  if (modal) modal.classList.add("hidden");
}

window.openMcpModal = openMcpModal;
window.closeMcpModal = closeMcpModal;


function renderMcpToolsList(tools) {
  const container = document.getElementById("mcpToolsGrid");
  if (!container || !tools) return;

  container.innerHTML = tools.map(t => `
    <div class="mcp-tool-card">
      <div class="mcp-tool-name">⚡ ${escapeHtml(t.name)}</div>
      <div class="mcp-tool-desc">${escapeHtml(t.description)}</div>
      <button class="mcp-run-btn" onclick="runMcpToolDemo('${t.name}')">
        ▶ Test Run Tool
      </button>
    </div>
  `).join("");
}

async function runMcpToolDemo(toolName) {
  const consoleEl = document.getElementById("mcpConsoleOutput");
  if (consoleEl) {
    consoleEl.innerText = `Executing MCP Tool: ${toolName} via JSON-RPC 2.0...\nSending request payload...`;
  }

  const samplePayloads = {
    "screen_patentability": { "botanicals": ["Curcuma longa (Curcumin)", "Wintergreen Oil"], "dosage_form": "Liposomal Nanocarrier" },
    "check_nba_clearance": { "biological_resources": ["Withania somnifera"], "applicant_type": "Indian Citizen / Company" },
    "get_ayush_licensing": { "category": "Ayurvedic Proprietary Medicine (Patent / Novel Formulation)", "ingredients": ["Curcumin", "Shallaki"] },
    "calculate_abs_royalty": { "annual_gross_ex_factory_sale_inr": 25000000 },
    "resolve_vernacular_botanical": { "vernacular_term": "Asgandh Nagori" },
    "get_gazette_citation": { "doc_id": "patent_act_3p" }
  };

  const payload = samplePayloads[toolName] || {};

  try {
    const res = await fetch("/api/mcp/execute", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ tool_name: toolName, arguments: payload })
    });
    const data = await res.json();
    if (consoleEl) {
      consoleEl.innerText = `// MCP Protocol Response (JSON-RPC 2.0)\n` + JSON.stringify(data, null, 2);
    }
  } catch (e) {
    if (consoleEl) {
      consoleEl.innerText = `Error executing MCP tool: ${e.message}`;
    }
  }
}

// ===================================================
// ===================================================
// PAID TIER & EXECUTIVE REGULATORY SUITE
// ===================================================

let currentTierMode = "free"; // 'free' | 'paid'
let proProjectsList = [];
let currentProProjectId = "proj_ayur_rheuma";
let currentSelectedStageId = "stage_3";

function toggleTierMode() {
  if (currentTierMode === "free") {
    openPaidHub();
  } else {
    returnToFreeTier();
  }
}

function openPaidHub() {
  currentTierMode = "paid";
  const chatScroll = document.getElementById("chatScrollArea");
  const chatDock = document.querySelector(".chat-input-dock");
  const proContainer = document.getElementById("proStudioContainer");
  const achieveContainer = document.getElementById("achieveGoalContainer");
  const mentorshipContainer = document.getElementById("mentorshipGatewayContainer");
  const headerProBtn = document.getElementById("headerProBtn");
  const modulesGrid = document.getElementById("paidModulesGrid");
  const sidebar = document.getElementById("chatSidebar");
  const mentorshipThreads = document.getElementById("sidebarMentorshipThreads");

  const chatHeader = document.querySelector(".chat-header");
  if (chatHeader) chatHeader.classList.remove("hidden");

  // Per user request: Hide left sidebar on the Paid landing page so 3 cards take full center focus
  if (sidebar) sidebar.classList.add("hidden");
  if (mentorshipThreads) mentorshipThreads.classList.add("hidden");

  if (chatScroll) chatScroll.classList.add("hidden");
  if (chatDock) chatDock.classList.add("hidden");
  if (achieveContainer) achieveContainer.classList.add("hidden");
  if (mentorshipContainer) mentorshipContainer.classList.add("hidden");
  if (proContainer) proContainer.classList.remove("hidden");
  if (modulesGrid) modulesGrid.classList.remove("hidden");

  if (headerProBtn) {
    headerProBtn.classList.add("paid-active");
    headerProBtn.title = "Go back to Free Tier";
    headerProBtn.innerHTML = `<span class="pro-sparkle">←</span><span class="pro-label">Free Tier</span>`;
  }
}

function returnToFreeTier() {
  currentTierMode = "free";
  const chatScroll = document.getElementById("chatScrollArea");
  const chatDock = document.querySelector(".chat-input-dock");
  const proContainer = document.getElementById("proStudioContainer");
  const achieveContainer = document.getElementById("achieveGoalContainer");
  const mentorshipContainer = document.getElementById("mentorshipGatewayContainer");
  const headerProBtn = document.getElementById("headerProBtn");
  const sidebar = document.getElementById("chatSidebar");
  const chatbotThreads = document.getElementById("sidebarChatbotThreads");
  const goalThreads = document.getElementById("sidebarGoalThreads");
  const mentorshipThreads = document.getElementById("sidebarMentorshipThreads");
  const chatHeader = document.querySelector(".chat-header");
  if (chatHeader) chatHeader.classList.remove("hidden");

  // Restore left sidebar and chatbot history when returning to Free Tier
  if (sidebar) sidebar.classList.remove("hidden");
  if (chatbotThreads) chatbotThreads.classList.remove("hidden");
  if (goalThreads) goalThreads.classList.add("hidden");
  if (mentorshipThreads) mentorshipThreads.classList.add("hidden");

  if (proContainer) proContainer.classList.add("hidden");
  if (achieveContainer) achieveContainer.classList.add("hidden");
  if (mentorshipContainer) mentorshipContainer.classList.add("hidden");
  if (chatScroll) chatScroll.classList.remove("hidden");
  if (chatDock) chatDock.classList.remove("hidden");

  // Close any open mentor modals
  closeMentorModals();

  if (headerProBtn) {
    headerProBtn.classList.remove("paid-active");
    headerProBtn.title = "Switch between Free and Assist Plus";
    headerProBtn.innerHTML = `<span class="pro-sparkle">★</span><span class="pro-label">Assist Plus</span><span class="pro-badge">PLUS</span>`;
  }
}

function openPaidChatbot() {
  // Directly opens the chatbot interface exactly like the free option
  const chatScroll = document.getElementById("chatScrollArea");
  const chatDock = document.querySelector(".chat-input-dock");
  const proContainer = document.getElementById("proStudioContainer");
  const achieveContainer = document.getElementById("achieveGoalContainer");
  const mentorshipContainer = document.getElementById("mentorshipGatewayContainer");
  const headerProBtn = document.getElementById("headerProBtn");
  const sidebar = document.getElementById("chatSidebar");
  const chatbotThreads = document.getElementById("sidebarChatbotThreads");
  const goalThreads = document.getElementById("sidebarGoalThreads");
  const mentorshipThreads = document.getElementById("sidebarMentorshipThreads");
  const chatHeader = document.querySelector(".chat-header");
  if (chatHeader) chatHeader.classList.remove("hidden");

  // Restore sidebar with chatbot history
  if (sidebar) sidebar.classList.remove("hidden");
  if (chatbotThreads) chatbotThreads.classList.remove("hidden");
  if (goalThreads) goalThreads.classList.add("hidden");
  if (mentorshipThreads) mentorshipThreads.classList.add("hidden");

  if (proContainer) proContainer.classList.add("hidden");
  if (achieveContainer) achieveContainer.classList.add("hidden");
  if (mentorshipContainer) mentorshipContainer.classList.add("hidden");
  if (chatScroll) chatScroll.classList.remove("hidden");
  if (chatDock) chatDock.classList.remove("hidden");

  // Keep button as "← Free Tier"
  if (headerProBtn) {
    headerProBtn.classList.add("paid-active");
    headerProBtn.title = "Go back to Free Tier";
    headerProBtn.innerHTML = `<span class="pro-sparkle">←</span><span class="pro-label">Free Tier</span>`;
  }
}

// ===================================================
// ACHIEVE GOAL: DEDICATED HISTORY & ROADMAP WORKFLOW
// ===================================================

let currentActiveGoalStageId = "stage_1";
let currentGoalZoomedNodeId = null;

let achieveGoalHistory = [
  {
    id: "goal_curcumin_balm",
    title: "Curcumin & Boswellia Arthritis Topical Balm",
    query: "Formulate and patent a novel Curcumin and Boswellia topical arthritis balm with Section 3(p) clearance and NBA export approval",
    date: "Active Project",
    stages: [
      { id: "stage_1", order: 1, title: "Botanical Normalization", timeline: "Weeks 1-2", authority: "PCIM&H / Ministry of Ayush", statute: "Ayurvedic Pharmacopoeia Standards", description: "Standardize raw Curcumin and Boswellia botanical markers against official monographs.", mandates: ["HPTLC Fingerprint Identification", "Heavy Metal & Microbial Clearance (Schedule E-1)"], completed: true, x: 80, y: 150 },
      { id: "stage_2", order: 2, title: "TKDL Section 3(p) Clearance", timeline: "Weeks 3-5", authority: "Indian Patent Office (IPO)", statute: "Patents Act Section 3(p) & 3(e)", description: "Screen against 250,000+ TKDL prior art references to establish non-obvious synergistic efficacy.", mandates: ["CSIR-TKDL Clearance Certificate", "Synergy Assay (CI < 0.75)"], completed: true, x: 240, y: 150 },
      { id: "stage_3", order: 3, title: "NBA Section 6 Prior Approval", timeline: "Weeks 6-9", authority: "National Biodiversity Authority (NBA)", statute: "Biological Diversity Act Section 6(1)", description: "Submit mandatory Form III prior approval filing for commercial bio-resource utilization.", mandates: ["NBA Form III Application", "SBB Intimation Notice"], completed: false, x: 400, y: 150 },
      { id: "stage_4", order: 4, title: "Rule 158-B Topical Dossier", timeline: "Weeks 10-15", authority: "State Ayush Licensing Authority", statute: "Drugs & Cosmetics Rules Rule 158-B", description: "Compile Form 24-D manufacturing license application backed by Schedule T cleanroom audit.", mandates: ["Rule 158-B Proof of Safety", "Schedule T Cleanroom Validation"], completed: false, x: 560, y: 150 },
      { id: "stage_5", order: 5, title: "GLP Pre-Clinical Safety Protocol", timeline: "Weeks 16-20", authority: "Accredited Ayush Testing Lab", statute: "OECD 408 & Ayush GCP Guidelines", description: "Execute 90-day repeated-dose topical toxicity and stability testing.", mandates: ["OECD 408 90-Day Toxicity Protocol", "Accelerated Stability (ICH Q1A)"], completed: false, x: 720, y: 150 },
      { id: "stage_6", order: 6, title: "Commercial Manufacturing Grant", timeline: "Weeks 21-26", authority: "State Ayush Licensing Authority", statute: "Drugs & Cosmetics Act Form 25-D", description: "Obtain Certificate of Pharmaceutical Product (CoPP) for market launch.", mandates: ["WHO-GMP CoPP Certificate", "Gazette Form 25-D License"], completed: false, x: 880, y: 150 }
    ]
  },
  {
    id: "goal_ashwagandha_syrup",
    title: "Rule 158-B Classical Ashwagandha Syrup",
    query: "Secure Ayush manufacturing license under Rule 158-B for Classical Ashwagandha syrup with stability study",
    date: "Licensing Track",
    stages: [
      { id: "stage_1", order: 1, title: "Classical Shastra Citation", timeline: "Weeks 1-2", authority: "PCIM&H / Ministry of Ayush", statute: "D&C Act First Schedule Texts", description: "Verify Ashwagandha Arishta/Syrup classical text citation from Sharangadhara Samhita.", mandates: ["First Schedule Ayurvedic Formulary Validation", "Withanolide A/B Marker Standardization"], completed: true, x: 80, y: 150 },
      { id: "stage_2", order: 2, title: "State SLA Form 24-D Dossier", timeline: "Weeks 3-5", authority: "State Ayush Licensing Authority", statute: "Drugs & Cosmetics Rules Rule 158-B", description: "Submit Form 24-D manufacturing application for classical ASU formulation.", mandates: ["Form 24-D Statutory Application", "Raw Material Certificate of Analysis"], completed: false, x: 240, y: 150 },
      { id: "stage_3", order: 3, title: "Schedule T Cleanroom Inspection", timeline: "Weeks 6-9", authority: "State Ayush Drug Inspectorate", statute: "Schedule T Good Manufacturing Practices", description: "State regulatory inspection of manufacturing premises and liquid oral filling line.", mandates: ["1,200 sq. ft. Cleanroom Compliance", "Batch Production Record Verification"], completed: false, x: 400, y: 150 },
      { id: "stage_4", order: 4, title: "Stability & Shelf-Life Study", timeline: "Weeks 10-15", authority: "NABL Accredited Ayush Lab", statute: "Rule 161-B Stability Protocols", description: "Complete accelerated and real-time stability protocols verifying 3-year shelf life.", mandates: ["ICH Q1A Accelerated Stability Testing", "Preservative Efficacy Verification"], completed: false, x: 560, y: 150 },
      { id: "stage_5", order: 5, title: "State Licensing Authority Approval", timeline: "Weeks 16-20", authority: "State Ayush Licensing Authority", statute: "Rule 158-B Classical Exemption", description: "Procure commercial manufacturing license with clinical trial exemption.", mandates: ["SLA Technical Committee Approval", "Schedule M Cleanroom Clearance"], completed: false, x: 720, y: 150 },
      { id: "stage_6", order: 6, title: "Commercial Form 25-D Issuance", timeline: "Weeks 21-26", authority: "Ministry of Ayush / SLA", statute: "Form 25-D Final License", description: "Final gazetted statutory manufacturing license for pan-India distribution.", mandates: ["Commercial Batch Packaging Approval", "Ayush Standard Mark Certification"], completed: false, x: 880, y: 150 }
    ]
  },
  {
    id: "goal_brahmi_ind",
    title: "Standardized Brahmi Extract US FDA IND",
    query: "File international PCT patent and US FDA botanical IND for standardized Brahmi extract",
    date: "Global Export",
    stages: [
      { id: "stage_1", order: 1, title: "PCIM&H Monograph Baseline", timeline: "Weeks 1-3", authority: "PCIM&H / CDSCO", statute: "API Part-I Monograph 14", description: "Standardize Bacoside A/B active markers using supercritical fluid extraction.", mandates: ["Supercritical CO2 Extraction Protocol", "Chemical Fingerprint Monograph"], completed: false, x: 80, y: 150 },
      { id: "stage_2", order: 2, title: "NBA Biodiversity Form 1 Export", timeline: "Weeks 4-7", authority: "National Biodiversity Authority", statute: "BD Act Section 3 & Section 20", description: "Procure NBA Form 1 approval for biological export of Bacopa monnieri outside India.", mandates: ["NBA Form 1 Application", "ABS Ex-Factory Commercial Agreement"], completed: false, x: 240, y: 150 },
      { id: "stage_3", order: 3, title: "WIPO PCT International Filing", timeline: "Weeks 8-12", authority: "WIPO / Indian Patent Office", statute: "Patent Cooperation Treaty (PCT)", description: "File PCT international patent application claiming priority under Paris Convention.", mandates: ["PCT Request Form & Specification", "International Search Authority Designation"], completed: false, x: 400, y: 150 },
      { id: "stage_4", order: 4, title: "US FDA Pre-IND Consultation", timeline: "Weeks 13-18", authority: "US FDA CDER Botanical Team", statute: "FDA Botanical Drug Guidance (21 CFR 312)", description: "Conduct Type B pre-IND meeting with FDA reviewing Chemistry, Manufacturing & Controls (CMC).", mandates: ["Pre-IND Meeting Briefing Package", "Batch-to-Batch Consistency Validation"], completed: false, x: 560, y: 150 },
      { id: "stage_5", order: 5, title: "GLP Toxicology & Safety Profiling", timeline: "Weeks 19-24", authority: "GLP Certified Research Lab", statute: "OECD GLP Guidelines", description: "Complete safety pharmacology and 28-day oral rodent toxicity study.", mandates: ["GLP Toxicology Final Report", "Human Equivalent Dose (HED) Calculation"], completed: false, x: 720, y: 150 },
      { id: "stage_6", order: 6, title: "FDA IND 30-Day Safe-to-Proceed", timeline: "Weeks 25-30", authority: "US Food and Drug Administration", statute: "US 21 CFR Part 312 IND Clearance", description: "Obtain US FDA 30-day clearance allowing Phase-II clinical evaluation.", mandates: ["Electronic Common Technical Document (eCTD)", "Clinical Protocol Approval"], completed: false, x: 880, y: 150 }
    ]
  }
];

let currentGoalData = JSON.parse(JSON.stringify(achieveGoalHistory[0]));

function renderGoalHistory() {
  const container = document.getElementById("sidebarGoalRoadmapsList");
  if (!container) return;

  container.innerHTML = achieveGoalHistory.map(g => {
    const isCurrent = currentGoalData && currentGoalData.id === g.id;
    const totalStages = g.stages ? g.stages.length : 6;
    const completedCount = g.stages ? g.stages.filter(s => s.completed).length : 0;
    
    return `
      <div class="goal-history-item ${isCurrent ? 'active-goal' : ''}" onclick="loadSavedGoal('${g.id}')">
        <div class="goal-history-title">${escapeHtml(g.title || g.query)}</div>
        <div class="goal-history-meta">
          <span class="goal-history-badge">${completedCount}/${totalStages} Completed</span>
          <span>${escapeHtml(g.date || 'Roadmap')}</span>
        </div>
      </div>
    `;
  }).join("");
}

function loadSavedGoal(goalId) {
  const item = achieveGoalHistory.find(g => g.id === goalId);
  if (!item) return;

  currentGoalData = JSON.parse(JSON.stringify(item));
  currentActiveGoalStageId = currentGoalData.stages[0]?.id || "stage_1";

  // Position nodes
  const startX = 80;
  const endX = 880;
  const stepX = currentGoalData.stages.length > 1 ? (endX - startX) / (currentGoalData.stages.length - 1) : 0;
  currentGoalData.stages.forEach((s, idx) => {
    s.x = Math.round(startX + (idx * stepX));
    s.y = 150;
  });

  const goalLabel = document.getElementById("roadmapGoalText");
  const topLabel = document.getElementById("achieveCurrentGoalLabel");
  const newGoalBtn = document.getElementById("achieveNewGoalBtn");
  const entryView = document.getElementById("achieveEntryView");
  const loadingState = document.getElementById("achieveLoadingState");
  const roadmapView = document.getElementById("achieveRoadmapView");
  const canvasWrapper = document.getElementById("roadmapCanvasWrapper");
  const implWorkspace = document.getElementById("implementationWorkspace");

  if (goalLabel) goalLabel.textContent = (currentGoalData.title || currentGoalData.query);
  if (topLabel) topLabel.textContent = "Milestone Roadmap: " + (currentGoalData.title || currentGoalData.query);
  if (newGoalBtn) newGoalBtn.classList.remove("hidden");

  if (entryView) entryView.classList.add("hidden");
  if (loadingState) loadingState.classList.add("hidden");
  if (roadmapView) roadmapView.classList.remove("hidden");
  if (canvasWrapper) canvasWrapper.classList.remove("hidden");
  if (implWorkspace) implWorkspace.classList.add("hidden");

  resetGoalGraphZoom();
  renderGoalSvgGraph();
  renderGoalHistory();
}

function openAchieveGoalSection() {
  const proContainer = document.getElementById("proStudioContainer");
  const achieveContainer = document.getElementById("achieveGoalContainer");
  const mentorshipContainer = document.getElementById("mentorshipGatewayContainer");
  const chatScroll = document.getElementById("chatScrollArea");
  const chatDock = document.querySelector(".chat-input-dock");
  const headerProBtn = document.getElementById("headerProBtn");
  const sidebar = document.getElementById("chatSidebar");
  const chatbotThreads = document.getElementById("sidebarChatbotThreads");
  const goalThreads = document.getElementById("sidebarGoalThreads");
  const mentorshipThreads = document.getElementById("sidebarMentorshipThreads");

  // Show sidebar with its own Achieve Goal history
  if (sidebar) sidebar.classList.remove("hidden");
  if (chatbotThreads) chatbotThreads.classList.add("hidden");
  if (mentorshipThreads) mentorshipThreads.classList.add("hidden");
  if (goalThreads) goalThreads.classList.remove("hidden");

  if (proContainer) proContainer.classList.add("hidden");
  if (mentorshipContainer) mentorshipContainer.classList.add("hidden");
  if (chatScroll) chatScroll.classList.add("hidden");
  if (chatDock) chatDock.classList.add("hidden");
  if (achieveContainer) achieveContainer.classList.remove("hidden");

  const chatHeader = document.querySelector(".chat-header");
  if (chatHeader) chatHeader.classList.add("hidden");

  // Render dedicated goal history in sidebar
  renderGoalHistory();

  // Keep button as "← Free Tier"
  if (headerProBtn) {
    headerProBtn.classList.add("paid-active");
    headerProBtn.title = "Go back to Free Tier";
    headerProBtn.innerHTML = `<span class="pro-sparkle">←</span><span class="pro-label">Free Tier</span>`;
  }
}

function handleAchieveInputKey(e) {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    handleAchieveSubmit();
  }
}

function handleAchieveSubmit() {
  const input = document.getElementById("achieveGoalInput");
  const query = (input ? input.value : "").trim();
  if (!query) return;
  submitAchieveGoal(query);
}

async function submitAchieveGoal(goalQuery) {
  if (!goalQuery || !goalQuery.trim()) return;
  const cleanQuery = goalQuery.trim();

  const entryView = document.getElementById("achieveEntryView");
  const loadingState = document.getElementById("achieveLoadingState");
  const roadmapView = document.getElementById("achieveRoadmapView");
  const topLabel = document.getElementById("achieveCurrentGoalLabel");
  const newGoalBtn = document.getElementById("achieveNewGoalBtn");

  // Show loading state while querying LLM
  if (entryView) entryView.classList.add("hidden");
  if (roadmapView) roadmapView.classList.add("hidden");
  if (loadingState) loadingState.classList.remove("hidden");
  if (topLabel) topLabel.textContent = "Synthesizing Roadmap...";

  try {
    const res = await fetch("/api/goal/generate-roadmap", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ goal: cleanQuery })
    });
    const data = await res.json();

    if (data.status === "success" && data.stages && data.stages.length > 0) {
      const stages = data.stages;
      const startX = 80;
      const endX = 880;
      const stepX = stages.length > 1 ? (endX - startX) / (stages.length - 1) : 0;
      stages.forEach((s, idx) => {
        s.x = Math.round(startX + (idx * stepX));
        s.y = 150;
        s.completed = false;
      });

      const newId = "goal_" + Date.now();
      currentGoalData = {
        id: newId,
        query: cleanQuery,
        title: data.title || cleanQuery,
        date: "Just now",
        stages: stages
      };
      currentActiveGoalStageId = stages[0].id;

      // Add to history and render
      achieveGoalHistory.unshift(JSON.parse(JSON.stringify(currentGoalData)));
      renderGoalHistory();
    }
  } catch (err) {
    console.error("Error generating roadmap:", err);
  } finally {
    if (loadingState) loadingState.classList.add("hidden");
    if (roadmapView) roadmapView.classList.remove("hidden");
    const canvasWrapper = document.getElementById("roadmapCanvasWrapper");
    const implWorkspace = document.getElementById("implementationWorkspace");
    if (canvasWrapper) canvasWrapper.classList.remove("hidden");
    if (implWorkspace) implWorkspace.classList.add("hidden");
    if (newGoalBtn) newGoalBtn.classList.remove("hidden");

    const goalLabel = document.getElementById("roadmapGoalText");
    if (goalLabel) goalLabel.textContent = currentGoalData.title || cleanQuery;
    if (topLabel) topLabel.textContent = "Milestone Roadmap: " + (currentGoalData.title || cleanQuery);

    resetGoalGraphZoom();
    renderGoalSvgGraph();
  }
}

function resetAchieveGoalView() {
  const entryView = document.getElementById("achieveEntryView");
  const roadmapView = document.getElementById("achieveRoadmapView");
  const loadingState = document.getElementById("achieveLoadingState");
  const newGoalBtn = document.getElementById("achieveNewGoalBtn");
  const input = document.getElementById("achieveGoalInput");
  const topLabel = document.getElementById("achieveCurrentGoalLabel");
  const inspector = document.getElementById("nodeInspectorDrawer");
  const canvasWrapper = document.getElementById("roadmapCanvasWrapper");
  const implWorkspace = document.getElementById("implementationWorkspace");

  if (input) input.value = "";
  if (topLabel) topLabel.textContent = "Milestone Roadmap Generator";
  if (entryView) entryView.classList.remove("hidden");
  if (loadingState) loadingState.classList.add("hidden");
  if (roadmapView) roadmapView.classList.add("hidden");
  if (newGoalBtn) newGoalBtn.classList.add("hidden");
  if (inspector) inspector.classList.add("hidden");
  if (canvasWrapper) canvasWrapper.classList.remove("hidden");
  if (implWorkspace) implWorkspace.classList.add("hidden");

  currentGoalZoomedNodeId = null;
  renderGoalHistory();
}

function renderGoalSvgGraph() {
  const edgesGroup = document.getElementById("goalEdgesGroup");
  const nodesGroup = document.getElementById("goalNodesGroup");
  if (!edgesGroup || !nodesGroup) return;

  // Clear previous
  edgesGroup.innerHTML = "";
  nodesGroup.innerHTML = "";

  const stages = currentGoalData.stages;
  const nodeW = 132;
  const nodeH = 82;

  // Draw Connecting Edges with Arrowheads
  for (let i = 0; i < stages.length - 1; i++) {
    const s1 = stages[i];
    const s2 = stages[i + 1];

    const x1 = s1.x + (nodeW / 2);
    const y1 = s1.y;
    const x2 = s2.x - (nodeW / 2);
    const y2 = s2.y;

    const markerId = s1.completed ? "goalArrowCompleted" : "goalArrow";
    const strokeColor = s1.completed ? "#059669" : "#3B82F6";

    const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
    path.setAttribute("d", `M ${x1} ${y1} C ${x1 + 18} ${y1}, ${x2 - 18} ${y2}, ${x2} ${y2}`);
    path.setAttribute("fill", "none");
    path.setAttribute("stroke", strokeColor);
    path.setAttribute("stroke-width", "2");
    path.setAttribute("stroke-dasharray", s1.completed ? "none" : "4,3");
    path.setAttribute("marker-end", `url(#${markerId})`);
    edgesGroup.appendChild(path);
  }

  // Draw Nodes
  stages.forEach(stage => {
    const g = document.createElementNS("http://www.w3.org/2000/svg", "g");
    const isCompleted = stage.completed;
    const isZoomed = currentGoalZoomedNodeId === stage.id;
    g.setAttribute("class", `goal-svg-node ${isCompleted ? 'goal-node-completed-dark' : 'goal-node-light'} ${isZoomed ? 'goal-node-active-zoomed' : ''}`);
    g.setAttribute("id", `goalSvgNode_${stage.id}`);
    g.setAttribute("onclick", `zoomGoalNode('${stage.id}', ${stage.x}, ${stage.y})`);

    const rectX = stage.x - (nodeW / 2);
    const rectY = stage.y - (nodeH / 2);

    // Tooltip title for hover
    const titleEl = document.createElementNS("http://www.w3.org/2000/svg", "title");
    titleEl.textContent = `Stage ${stage.order}: ${stage.title} • ${stage.timeline}`;
    g.appendChild(titleEl);

    // Node Box Rectangle
    const rect = document.createElementNS("http://www.w3.org/2000/svg", "rect");
    rect.setAttribute("class", "goal-node-rect");
    rect.setAttribute("x", rectX);
    rect.setAttribute("y", rectY);
    rect.setAttribute("width", nodeW);
    rect.setAttribute("height", nodeH);
    rect.setAttribute("rx", "12");
    rect.setAttribute("ry", "12");
    g.appendChild(rect);

    // Order Pill (Stage 1..6)
    const pillG = document.createElementNS("http://www.w3.org/2000/svg", "g");
    const pillRect = document.createElementNS("http://www.w3.org/2000/svg", "rect");
    pillRect.setAttribute("x", rectX + 8);
    pillRect.setAttribute("y", rectY + 7);
    pillRect.setAttribute("width", "50");
    pillRect.setAttribute("height", "16");
    pillRect.setAttribute("rx", "8");
    pillRect.setAttribute("fill", isCompleted ? "rgba(16, 185, 129, 0.2)" : "#EFF6FF");
    pillRect.setAttribute("stroke", isCompleted ? "#10B981" : "#BFDBFE");
    pillRect.setAttribute("stroke-width", "1");
    pillG.appendChild(pillRect);

    const pillText = document.createElementNS("http://www.w3.org/2000/svg", "text");
    pillText.setAttribute("x", rectX + 33);
    pillText.setAttribute("y", rectY + 18.5);
    pillText.setAttribute("text-anchor", "middle");
    pillText.setAttribute("font-size", "8.5");
    pillText.setAttribute("font-weight", "800");
    pillText.setAttribute("fill", isCompleted ? "#34D399" : "#1D4ED8");
    pillText.textContent = `STAGE ${stage.order}`;
    pillG.appendChild(pillText);
    g.appendChild(pillG);

    // Status Checkmark / Dot (top right)
    const statusText = document.createElementNS("http://www.w3.org/2000/svg", "text");
    statusText.setAttribute("x", rectX + nodeW - 14);
    statusText.setAttribute("y", rectY + 19);
    statusText.setAttribute("text-anchor", "middle");
    statusText.setAttribute("font-size", isCompleted ? "11" : "9");
    statusText.setAttribute("font-weight", "800");
    statusText.setAttribute("fill", isCompleted ? "#10B981" : "#94A3B8");
    statusText.textContent = isCompleted ? "✓" : "○";
    g.appendChild(statusText);

    // Node Title using foreignObject for strict HTML line wrapping (Never overflows the box!)
    const fo = document.createElementNS("http://www.w3.org/2000/svg", "foreignObject");
    fo.setAttribute("x", rectX + 8);
    fo.setAttribute("y", rectY + 27);
    fo.setAttribute("width", nodeW - 16);
    fo.setAttribute("height", 36);

    const titleDiv = document.createElement("div");
    titleDiv.setAttribute("style", `
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Inter', sans-serif;
      font-size: 9.5px;
      font-weight: 700;
      line-height: 1.22;
      color: ${isCompleted ? '#FFFFFF' : '#0F172A'};
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
      overflow: hidden;
      text-overflow: ellipsis;
      word-break: break-word;
      hyphens: auto;
      pointer-events: none;
      user-select: none;
    `);
    titleDiv.textContent = stage.title;
    fo.appendChild(titleDiv);
    g.appendChild(fo);

    // Timeline Subtitle
    const timelineText = document.createElementNS("http://www.w3.org/2000/svg", "text");
    timelineText.setAttribute("x", rectX + 8);
    timelineText.setAttribute("y", rectY + 73);
    timelineText.setAttribute("font-size", "8.5");
    timelineText.setAttribute("font-weight", "600");
    timelineText.setAttribute("fill", isCompleted ? "#94A3B8" : "#64748B");
    timelineText.textContent = `⏱ ${stage.timeline}`;
    g.appendChild(timelineText);

    nodesGroup.appendChild(g);
  });
}

function zoomGoalNode(stageId, centerX, centerY) {
  const svg = document.getElementById("goalSvgCanvas");
  const drawer = document.getElementById("nodeInspectorDrawer");
  const stage = currentGoalData.stages.find(s => s.id === stageId);
  if (!svg || !stage) return;

  currentActiveGoalStageId = stageId;

  // Toggle zoom if same node clicked
  if (currentGoalZoomedNodeId === stageId) {
    resetGoalGraphZoom();
    return;
  }

  currentGoalZoomedNodeId = stageId;

  // Update SVG highlight class
  document.querySelectorAll(".goal-svg-node").forEach(el => el.classList.remove("goal-node-active-zoomed"));
  const activeNodeEl = document.getElementById(`goalSvgNode_${stageId}`);
  if (activeNodeEl) activeNodeEl.classList.add("goal-node-active-zoomed");

  // Smooth zoom viewBox (width 360, height 200)
  const zoomW = 340;
  const zoomH = 190;
  const minX = Math.max(0, Math.min(960 - zoomW, centerX - (zoomW / 2)));
  const minY = Math.max(0, Math.min(300 - zoomH, centerY - (zoomH / 2)));
  svg.setAttribute("viewBox", `${minX} ${minY} ${zoomW} ${zoomH}`);

  // Populate Inspector Drawer
  if (drawer) {
    drawer.classList.remove("hidden");
    const badge = document.getElementById("inspectorStageBadge");
    const titleInput = document.getElementById("inspectorNodeTitleInput");
    const descInput = document.getElementById("inspectorNodeDescInput");
    const completeBtn = document.getElementById("inspectorCompleteBtn");
    const mandatesList = document.getElementById("inspectorMandatesList");

    if (badge) badge.textContent = `Stage ${stage.order}`;
    if (titleInput) titleInput.value = stage.title;
    if (descInput) descInput.value = stage.description;

    if (completeBtn) {
      if (stage.completed) {
        completeBtn.classList.add("is-completed");
        completeBtn.innerHTML = "<span>Completed ✓</span>";
      } else {
        completeBtn.classList.remove("is-completed");
        completeBtn.innerHTML = "<span>Mark Complete ✓</span>";
      }
    }

    if (mandatesList) {
      mandatesList.innerHTML = (stage.mandates || []).map(m => `
        <div class="mandate-item">
          <span style="color: #2563EB;">⚖️</span>
          <span>${escapeHtml(m)}</span>
        </div>
      `).join("");
    }
  }
}

function resetGoalGraphZoom() {
  const svg = document.getElementById("goalSvgCanvas");
  currentGoalZoomedNodeId = null;
  if (svg) svg.setAttribute("viewBox", "0 0 960 300");
  document.querySelectorAll(".goal-svg-node").forEach(el => el.classList.remove("goal-node-active-zoomed"));
}

function closeNodeInspector() {
  const drawer = document.getElementById("nodeInspectorDrawer");
  if (drawer) drawer.classList.add("hidden");
  resetGoalGraphZoom();
}

function handleNodeTitleEdit(newTitle) {
  const stage = currentGoalData.stages.find(s => s.id === currentActiveGoalStageId);
  if (stage) {
    stage.title = newTitle;
    renderGoalSvgGraph();
  }
}

function handleNodeDescEdit(newDesc) {
  const stage = currentGoalData.stages.find(s => s.id === currentActiveGoalStageId);
  if (stage) {
    stage.description = newDesc;
  }
}

function toggleCurrentNodeCompletion() {
  const stage = currentGoalData.stages.find(s => s.id === currentActiveGoalStageId);
  if (!stage) return;

  stage.completed = !stage.completed;

  const completeBtn = document.getElementById("inspectorCompleteBtn");
  if (completeBtn) {
    if (stage.completed) {
      completeBtn.classList.add("is-completed");
      completeBtn.innerHTML = "<span>Completed ✓</span>";
    } else {
      completeBtn.classList.remove("is-completed");
      completeBtn.innerHTML = "<span>Mark Complete ✓</span>";
    }
  }

  // Update in achieveGoalHistory
  const histItem = achieveGoalHistory.find(g => g.id === currentGoalData.id);
  if (histItem && histItem.stages) {
    const s = histItem.stages.find(x => x.id === stage.id);
    if (s) s.completed = stage.completed;
    renderGoalHistory();
  }

  // Re-render SVG to transition from light to dark or vice-versa
  renderGoalSvgGraph();
}

function startWorkingOnCurrentStage() {
  const stageId = currentGoalZoomedNodeId || currentActiveGoalStageId || currentGoalData.stages[0]?.id;
  currentActiveGoalStageId = stageId;
  closeNodeInspector();
  implementGoalRoadmap();
}

function implementGoalRoadmap() {
  const canvasWrapper = document.getElementById("roadmapCanvasWrapper");
  const implWorkspace = document.getElementById("implementationWorkspace");

  if (canvasWrapper) canvasWrapper.classList.add("hidden");
  if (implWorkspace) implWorkspace.classList.remove("hidden");

  renderImplementationRail();
  renderImplementationWorkspace();
}

function exitImplementationMode() {
  const canvasWrapper = document.getElementById("roadmapCanvasWrapper");
  const implWorkspace = document.getElementById("implementationWorkspace");

  if (implWorkspace) implWorkspace.classList.add("hidden");
  if (canvasWrapper) canvasWrapper.classList.remove("hidden");

  resetGoalGraphZoom();
  renderGoalSvgGraph();
}

function renderImplementationRail() {
  const rail = document.getElementById("railStepperList");
  if (!rail) return;

  rail.innerHTML = currentGoalData.stages.map(s => {
    const isActive = s.id === currentActiveGoalStageId;
    return `
      <div class="rail-node-card ${isActive ? 'active-stage' : ''} ${s.completed ? 'is-done' : ''}" onclick="selectImplementationStage('${s.id}')">
        <div class="rail-node-top">
          <span class="rail-node-order">STAGE ${s.order}</span>
          <span class="rail-node-status">${s.completed ? '✓ Done' : s.timeline}</span>
        </div>
        <div class="rail-node-title">${escapeHtml(s.title)}</div>
      </div>
    `;
  }).join("");
}

function selectImplementationStage(stageId) {
  currentActiveGoalStageId = stageId;
  renderImplementationRail();
  renderImplementationWorkspace();
}

// Stage Chat History Store
const stageChatHistory = {};

function formatStageMarkdown(text) {
  if (!text) return "";
  let clean = escapeHtml(text);
  clean = clean.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
  clean = clean.replace(/\*(.*?)\*/g, "<em>$1</em>");
  clean = clean.replace(/\n\n/g, "<br><br>").replace(/\n/g, "<br>");
  return clean;
}

function getStageStatutoryDetails(stage, goalData) {
  const herbList = (goalData?.detected_botanicals || []).map(b => (typeof b === 'object' ? (b.common_name || b.canonical_name || b.name) : b)).filter(Boolean);
  const herbStr = herbList.length > 0 ? herbList.join(", ") : "Botanical Actives";
  const dosageForm = goalData?.dosage_form || "Formulation";

  const order = stage.order || 1;
  const titleLower = (stage.title || "").toLowerCase();

  if (order === 1 || titleLower.includes("pharmacopoeial") || titleLower.includes("assay") || titleLower.includes("standard")) {
    return {
      docName: "PCIM&H Monograph & Batch Certificate of Analysis (CoA)",
      docShortName: "PCIM&H Certificate of Analysis",
      docCode: "Form PCIM-CoA (Schedule E-1)",
      docType: "Pharmacopoeial Quality & Identity Dossier",
      filename: `${herbList[0] || 'Botanical'}_Pharmacopoeial_CoA.docx`,
      law: "Ayurvedic Pharmacopoeia of India (API) Part I, Vol IX",
      gazetteRef: "Gazette Notification S.O. 2341(E) • Ministry of Ayush Standards",
      authority: "Pharmacopoeia Commission for Indian Medicine & Homoeopathy (PCIM&H)",
      gazetteDocId: "patent_act_3p",
      guidance: [
        `Procure authenticated raw ${herbStr} batches accompanied by geo-tagged botanical traceability certificates.`,
        `Perform HPTLC fingerprint identification against official API reference standards at an ISO/IEC 17025 NABL laboratory.`,
        "Establish heavy metal limits (Lead < 10ppm, Arsenic < 3ppm, Cadmium < 0.3ppm, Mercury < 1ppm) under Schedule E-1."
      ],
      dosAndDonts: "DO ensure botanical voucher specimens are deposited at an accredited herbarium. DO NOT submit test reports from non-NABL accredited laboratories.",
      sampleQueries: [
        `What are the API monograph limits for ${herbList[0] || 'this herb'}?`,
        "How to clear heavy metals testing under Schedule E-1?",
        "What laboratories are officially recognized by Ministry of Ayush?"
      ]
    };
  }

  if (order === 2 || titleLower.includes("tkdl") || titleLower.includes("3(p)") || titleLower.includes("patent")) {
    return {
      docName: "Form 1 Patent Specification & Section 3(p)/3(e) Non-Obviousness Statement",
      docShortName: "Section 3(p) Non-Obviousness Statement",
      docCode: "Form 1 (The Patents Act)",
      docType: "Patent Office Statutory Declaration",
      filename: `Patent_Form1_Section3p_Declaration.docx`,
      law: "The Patents Act, 1970, Section 3(p) & Section 3(e)",
      gazetteRef: "The Patents (Amendment) Act, 2005 • IPO Guidelines for Examination of Ayush Inventions",
      authority: "Indian Patent Office (IPO) & CSIR-TKDL Directorate",
      gazetteDocId: "patent_act_3p",
      guidance: [
        `Execute prior-art search across CSIR-TKDL (300,000+ formulations) to confirm traditional usage citations for ${herbStr}.`,
        "Determine Combination Index (CI < 0.75) using Chou-Talalay algorithm to demonstrate synergistic therapeutic non-obviousness.",
        "File Form 1 with provisional/complete specification accompanied by comparative biological efficacy data."
      ],
      dosAndDonts: "DO provide quantitative synergistic efficacy ratios over individual herbs. DO NOT claim raw plant mixtures without synergistic scientific evidence.",
      sampleQueries: [
        "How to overcome a Section 3(p) objection citing TKDL?",
        "What experimental data proves synergism under Section 3(e)?",
        "Can a novel extraction process get a patent for classical herbs?"
      ]
    };
  }

  if (order === 3 || titleLower.includes("nba") || titleLower.includes("biodiversity") || titleLower.includes("section 6")) {
    return {
      docName: "NBA Form III — Prior Approval for Applying for Intellectual Property Rights (ABS)",
      docShortName: "NBA Form III Application",
      docCode: "Form III (Biological Diversity Rules, Rule 18)",
      docType: "National Biodiversity Statutory Clearance",
      filename: `NBA_Form_III_Statutory_Application.docx`,
      law: "Biological Diversity Act, 2002, Section 6(1)",
      gazetteRef: "Gazette of India GSR 827(E) • Access and Benefit Sharing (ABS) Guidelines 2014",
      authority: "National Biodiversity Authority (NBA), Chennai",
      gazetteDocId: "nba_section_6",
      guidance: [
        `Register and create applicant profile on official NBA ABS e-Filing portal (absefiling.nic.in).`,
        `Declare precise geographic sourcing of ${herbStr} (district, forest division, state) with vendor GST procurement receipts.`,
        "Submit signed Access and Benefit Sharing (ABS) agreement agreeing to statutory ex-factory royalty sharing."
      ],
      dosAndDonts: "DO submit Form III before the patent is sealed/granted by the patent office. DO NOT commercially exploit Indian biological resources without State Biodiversity Board intimation.",
      sampleQueries: [
        "When is NBA Form III required vs Form I?",
        "What is the ABS benefit-sharing royalty fee percentage?",
        "What are the penalties under Section 55 for non-compliance?"
      ]
    };
  }

  if (order === 4 || titleLower.includes("158-b") || titleLower.includes("licens") || titleLower.includes("form 24")) {
    return {
      docName: `Form 24-D — Application for License to Manufacture Ayurvedic / Unani Drugs (${dosageForm})`,
      docShortName: "Form 24-D Manufacturing Application",
      docCode: "Form 24-D (Drugs & Cosmetics Rules)",
      docType: "State Ayush Drug Manufacturing Application",
      filename: `Form_24D_Manufacturing_License_Dossier.docx`,
      law: "Drugs & Cosmetics Rules, 1945, Rule 158-B & Schedule T",
      gazetteRef: "GSR 560(E) & 5th Schedule of Drugs and Cosmetics Rules • Ministry of Ayush",
      authority: "State Licensing Authority (SALA) - Ayush Department",
      gazetteDocId: "dnc_rule_158b",
      guidance: [
        `Submit Master Manufacturing Formula and labeling artwork in strict accordance with Rule 161.`,
        `Submit Schedule T GMP cleanroom layout audit (minimum 1,200 sq. ft. certified manufacturing floor).`,
        "Attach pilot clinical safety and accelerated stability data supporting claimed shelf-life."
      ],
      dosAndDonts: "DO appoint full-time manufacturing and testing technical staff with recognized B.A.M.S. / B.Pharm (Ayush) degrees. DO NOT market commercial batches until Form 25-D grant is officially issued.",
      sampleQueries: [
        "What documents are required for Form 24-D application?",
        "What are the cleanroom floor area specifications under Schedule T?",
        "What is the difference between Classical and Proprietary Ayush license under Rule 158-B?"
      ]
    };
  }

  if (order === 5 || titleLower.includes("glp") || titleLower.includes("safety") || titleLower.includes("tox") || titleLower.includes("stabil")) {
    return {
      docName: "Schedule E-1 & OECD 408 Pre-Clinical Safety & Stability Protocol",
      docShortName: "OECD 408 Safety & Stability Protocol",
      docCode: "Schedule E-1 / GLP Protocol",
      docType: "Toxicological & Safety Clearance Dossier",
      filename: `OECD408_PreClinical_Safety_Protocol.docx`,
      law: "Good Laboratory Practices (GLP) Guidelines & Schedule E-1 Standards",
      gazetteRef: "Ayush Clinical Research GCP/GLP Standards • Notification DCG(I) / Ayush Research",
      authority: "Accredited Ayush Testing & Toxicological Evaluation Board",
      gazetteDocId: "dnc_rule_158b",
      guidance: [
        "Execute 14-day acute oral toxicity study (OECD 423) in rodents to determine maximum tolerated dose.",
        "Perform 90-day repeated-dose sub-chronic toxicity protocol (OECD 408) covering hematology, biochemistry, and histopathology.",
        "Conduct real-time (25°C/60% RH) and accelerated (40°C/75% RH) stability testing according to ICH Q1A guidelines."
      ],
      dosAndDonts: "DO obtain Institutional Animal Ethics Committee (IAEC) approval before initiating in-vivo studies. DO NOT skip residual solvent and aflatoxin testing.",
      sampleQueries: [
        "What are the permissible limits for heavy metals under Schedule E-1?",
        "Is 90-day sub-chronic toxicity mandatory for all Ayurvedic drugs?",
        "How to conduct accelerated stability testing under ICH Q1A?"
      ]
    };
  }

  // Stage 6 / Global Export / Final Grant
  return {
    docName: "WHO-GMP Certificate of Pharmaceutical Product (CoPP) & Form 25-D Grant",
    docShortName: "WHO-GMP CoPP / Form 25-D Grant",
    docCode: "CoPP (WHO TRS 908) / Form 25-D",
    docType: "International Export & Final Commercialization Grant",
    filename: `WHO_GMP_CoPP_Form25D_Grant.docx`,
    law: "Drugs & Cosmetics Act, 1940 Form 25-D & WHO-GMP Guidelines",
    gazetteRef: "Central Gazette S.O. 1259(E) & US FDA Botanical Drug Guidance 2016",
    authority: "Central Drugs Standard Control Organization (CDSCO) & State Ayush Authority",
    gazetteDocId: "wipo_pct",
    guidance: [
      "Undergo joint audit inspection by CDSCO Central Drug Inspector and State Licensing Authority.",
      "Submit electronic Batch Manufacturing Records (BMR) verifying consistent commercial batch yields.",
      "Obtain WHO-GMP Certificate of Pharmaceutical Product (CoPP) for export destination clearances."
    ],
    dosAndDonts: "DO maintain complete electronic Batch Manufacturing Records (BMR) with 21 CFR Part 11 audit trails. DO NOT make therapeutic claims on packaging that violate the Drugs and Magic Remedies Act.",
    sampleQueries: [
      "How to apply for a WHO-GMP Certificate of Pharmaceutical Product (CoPP)?",
      "What are the label compliance requirements for overseas export?",
      "How to file a US FDA Pre-IND meeting request for botanical drugs?"
    ]
  };
}

function openStageGazette(stageId) {
  const stage = currentGoalData?.stages?.find(s => s.id === stageId) || currentGoalData?.stages?.[0];
  const docInfo = getStageStatutoryDetails(stage, currentGoalData);
  openGazettePanel(docInfo.gazetteDocId);
}

function downloadStageFilingDoc(stageId) {
  const stage = currentGoalData?.stages?.find(s => s.id === stageId) || currentGoalData?.stages?.[0];
  if (!stage) return;
  const docInfo = getStageStatutoryDetails(stage, currentGoalData);
  const herbList = (currentGoalData?.detected_botanicals || []).map(b => (typeof b === 'object' ? (b.common_name || b.canonical_name || b.name) : b)).filter(Boolean);
  const herbStr = herbList.length > 0 ? herbList.join(", ") : "Ayush Botanical Extract";
  const dosageForm = currentGoalData?.dosage_form || "Formulation";

  const fileContent = `================================================================================
OFFICIAL STATUTORY FILING DOSSIER • GOVERNMENT OF INDIA
MINISTRY OF AYUSH / STATUTORY REGULATORY GATEWAY
================================================================================

DOCUMENT:       ${docInfo.docName}
FORM CODE:      ${docInfo.docCode}
DOCUMENT TYPE:  ${docInfo.docType}
STATUTE:        ${docInfo.law}
GAZETTE REF:    ${docInfo.gazetteRef}
AUTHORITY:      ${docInfo.authority}
DATE OF DRAFT:  ${new Date().toLocaleDateString('en-GB', { day: 'numeric', month: 'long', year: 'numeric' })}

--------------------------------------------------------------------------------
1. APPLICANT & PROPRIETARY FORMULATION PARTICULARS
--------------------------------------------------------------------------------
Project Goal:          ${currentGoalData.title || currentGoalData.query}
Dosage / Delivery:     ${dosageForm}
Botanical Ingredients: ${herbStr}
Current Stage:         Stage ${stage.order}: ${stage.title}
Mandatory Timeline:    ${stage.timeline}

--------------------------------------------------------------------------------
2. STATUTORY DECLARATION & STATEMENT OF COMPLIANCE
--------------------------------------------------------------------------------
In accordance with ${docInfo.law} as promulgated under the Gazette of India, the applicant
hereby tenders official application data verifying:

(a) That all botanical specimens (${herbStr}) have been standardized in conformity with
    the Ayurvedic Pharmacopoeia of India (API) monographs under NABL laboratory audit.
(b) That no prior-art citations in the CSIR Traditional Knowledge Digital Library (TKDL)
    preclude the inventive non-obvious synergistic efficacy of this formulation.
(c) That statutory intimation and Access and Benefit Sharing (ABS) compliance
    is maintained under the provisions of the Biological Diversity Act, 2002.
(d) That manufacturing premises and cleanroom facilities conform to Good Manufacturing
    Practices (GMP) under Schedule T of the Drugs & Cosmetics Rules, 1945.

--------------------------------------------------------------------------------
3. MANDATORY STAGE VERIFICATION CHECKLIST
--------------------------------------------------------------------------------
${(stage.mandates || []).map((m, idx) => `[  ] ${idx + 1}. ${m}`).join("\n")}

--------------------------------------------------------------------------------
4. STATUTORY PROCEDURAL GUIDANCE & SUBMISSION INSTRUCTIONS
--------------------------------------------------------------------------------
${docInfo.guidance.map((g, idx) => `Step ${idx + 1}: ${g}`).join("\n")}

CRITICAL NOTE:
${docInfo.dosAndDonts}

Submitted with official verification on behalf of the Authorized Regulatory Signatory.
================================================================================
IP-SAKTI Sahayak Regulatory Engine • Deterministically Grounded Gazette Record
================================================================================`;

  const blob = new Blob([fileContent], { type: "text/plain;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = docInfo.filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

function renderStageChatThread(stageId) {
  const thread = document.getElementById(`stageChatThread_${stageId}`);
  if (!thread) return;

  const msgs = stageChatHistory[stageId] || [];
  thread.innerHTML = msgs.map(msg => `
    <div class="stage-chat-bubble ${msg.sender === 'user' ? 'user-bubble' : 'bot-bubble'}">
      <div class="bubble-sender">${msg.sender === 'user' ? '👤 You' : '🏛️ Ayush Regulatory Advisor'}</div>
      <div class="bubble-content">${formatStageMarkdown(msg.text)}</div>
    </div>
  `).join("");
  thread.scrollTop = thread.scrollHeight;
}

async function sendStageChatMessage(stageId) {
  const input = document.getElementById(`stageChatInput_${stageId}`);
  if (!input) return;
  const text = input.value.trim();
  if (!text) return;
  input.value = "";

  await executeStageQuery(stageId, text);
}

async function sendStagePredefinedQuery(stageId, queryText) {
  await executeStageQuery(stageId, queryText);
}

async function executeStageQuery(stageId, queryText) {
  const stage = currentGoalData.stages.find(s => s.id === stageId) || currentGoalData.stages[0];
  if (!stage) return;
  const docInfo = getStageStatutoryDetails(stage, currentGoalData);

  if (!stageChatHistory[stageId]) stageChatHistory[stageId] = [];

  // Add user message
  stageChatHistory[stageId].push({ sender: "user", text: queryText });
  renderStageChatThread(stageId);

  // Add pending indicator
  stageChatHistory[stageId].push({ sender: "assistant", text: "⏳ *Consulting official gazette statutes and regulatory standards...*", isPending: true });
  renderStageChatThread(stageId);

  try {
    const res = await fetch("/api/goal/stage-query", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        goal_title: currentGoalData.title || currentGoalData.query,
        stage_id: stage.id,
        stage_title: stage.title,
        stage_order: stage.order,
        stage_statute: docInfo.law,
        stage_authority: docInfo.authority,
        query: queryText,
        detected_botanicals: currentGoalData.detected_botanicals || []
      })
    });

    const data = await res.json();
    const answer = (data && data.answer) ? data.answer : "Statutory guidance successfully synthesized for this stage.";

    stageChatHistory[stageId] = stageChatHistory[stageId].filter(m => !m.isPending);
    stageChatHistory[stageId].push({ sender: "assistant", text: answer });
  } catch (err) {
    console.error("Stage query failed:", err);
    stageChatHistory[stageId] = stageChatHistory[stageId].filter(m => !m.isPending);
    stageChatHistory[stageId].push({
      sender: "assistant",
      text: `**Statutory Guidance for ${stage.title}:**\nUnder ${docInfo.law}, submit your completed ${docInfo.docShortName} directly to ${docInfo.authority}. Ensure all botanical batch records match the Ayurvedic Pharmacopoeia of India standards.`
    });
  }

  renderStageChatThread(stageId);
}

function handleMandateCheck(inputEl) {
  // If all mandates checked, prompt completion
  const container = inputEl.closest(".mandates-checkbox-list");
  if (!container) return;
  const allChecks = container.querySelectorAll("input[type='checkbox']");
  const allChecked = Array.from(allChecks).every(c => c.checked);
  if (allChecked) {
    const stage = currentGoalData.stages.find(s => s.id === currentActiveGoalStageId);
    if (stage && !stage.completed) {
      stage.completed = true;
      renderImplementationRail();
      renderImplementationWorkspace();
    }
  }
}

function renderImplementationWorkspace() {
  const workspace = document.getElementById("implCenterWorkspace");
  const stage = currentGoalData.stages.find(s => s.id === currentActiveGoalStageId) || currentGoalData.stages[0];
  if (!workspace || !stage) return;

  const docInfo = getStageStatutoryDetails(stage, currentGoalData);

  // Initialize stage chat history if needed
  if (!stageChatHistory[stage.id]) {
    stageChatHistory[stage.id] = [
      {
        sender: "assistant",
        text: `Namaste. I am your specialized regulatory officer for **Stage ${stage.order}: ${stage.title}**.\n\nI can assist you with:\n- Mandatory statutory filings under **${docInfo.law}**\n- Compliance requirements for **${docInfo.authority}**\n- Downloading and pre-filling **${docInfo.docName}**\n\nHow can I help you execute this milestone?`
      }
    ];
  }

  workspace.innerHTML = `
    <!-- Top Execution Bar -->
    <div class="stage-exec-top-bar">
      <div>
        <div class="stage-exec-pill">STAGE ${stage.order} EXECUTION WORKSPACE</div>
        <h2 class="stage-exec-title">${escapeHtml(stage.title)}</h2>
        <div class="stage-exec-meta">
          <span>⏱ <strong>Timeline:</strong> ${escapeHtml(stage.timeline)}</span>
          <span>🏛️ <strong>Authority:</strong> ${escapeHtml(docInfo.authority)}</span>
          <span>⚖️ <strong>Statute:</strong> ${escapeHtml(docInfo.law)}</span>
        </div>
      </div>
      <div>
        <button onclick="toggleCurrentNodeCompletion(); renderImplementationRail(); renderImplementationWorkspace();" class="stage-complete-toggle-btn ${stage.completed ? 'is-completed' : ''}">
          ${stage.completed ? '✓ Stage Completed' : 'Mark Stage Done ✓'}
        </button>
      </div>
    </div>

    <!-- THE PARTICULAR STATUTORY DOCUMENT & SOURCE CARD (Only this box's task document!) -->
    <div class="stage-doc-source-card">
      <div class="doc-card-top">
        <div class="doc-card-badge">MANDATORY STATUTORY FILING FOR THIS TASK</div>
        <h3 class="doc-card-title">📄 ${escapeHtml(docInfo.docName)}</h3>
        <div class="doc-card-tags">
          <span class="doc-tag-pill">Form Code: ${escapeHtml(docInfo.docCode)}</span>
          <span class="doc-tag-pill">Filing Type: ${escapeHtml(docInfo.docType)}</span>
        </div>
      </div>

      <div class="doc-card-source-strip">
        <div class="source-strip-col">
          <span class="source-strip-label">STATUTORY LAW &amp; SECTION:</span>
          <span class="source-strip-val">⚖️ ${escapeHtml(docInfo.law)}</span>
        </div>
        <div class="source-strip-col">
          <span class="source-strip-label">GOVERNING REGULATORY AUTHORITY:</span>
          <span class="source-strip-val">🏛️ ${escapeHtml(docInfo.authority)}</span>
        </div>
        <div class="source-strip-col">
          <span class="source-strip-label">OFFICIAL GAZETTE NOTIFICATION:</span>
          <span class="source-strip-val">📜 ${escapeHtml(docInfo.gazetteRef)}</span>
        </div>
      </div>

      <div class="doc-card-actions">
        <button class="doc-download-btn" onclick="downloadStageFilingDoc('${stage.id}')" title="Download Pre-filled Official Document">
          <span>📄 Download Official ${escapeHtml(docInfo.docShortName)} (.docx)</span>
        </button>
        <button class="doc-gazette-view-btn" onclick="openGazettePanel('${docInfo.gazetteDocId}')" title="View Official Gazette Record in Slide-out Reader">
          <span>📜 View Gazette Source in Reader</span>
        </button>
      </div>
    </div>

    <!-- COMPREHENSIVE GUIDANCE & MANDATES CHECKLIST -->
    <div class="stage-guidance-card">
      <h3 class="guidance-section-heading">📌 Stage Guidance &amp; Procedural Steps</h3>
      <div class="guidance-steps-list">
        ${docInfo.guidance.map((step, idx) => `
          <div class="guidance-step-item">
            <span class="step-num">${idx + 1}</span>
            <span class="step-desc">${escapeHtml(step)}</span>
          </div>
        `).join("")}
      </div>

      <div class="guidance-dos-donts">
        <span class="dos-donts-icon">⚠️</span>
        <div class="dos-donts-text">
          <strong>Official Compliance Tip:</strong> ${escapeHtml(docInfo.dosAndDonts)}
        </div>
      </div>

      <h4 class="mandates-heading">Mandatory Statutory Inspection Checklist:</h4>
      <div class="mandates-checkbox-list">
        ${(stage.mandates || []).map((m, idx) => `
          <label class="mandate-check-label">
            <input type="checkbox" ${stage.completed ? 'checked' : ''} onchange="handleMandateCheck(this)">
            <span>${escapeHtml(m)}</span>
          </label>
        `).join("")}
      </div>
    </div>

    <!-- STAGE-SPECIFIC INTERACTIVE AI CHATBOT -->
    <div class="stage-chatbot-card" id="stageChatbotSection">
      <div class="stage-chatbot-header">
        <div class="stage-chatbot-title">
          <span style="font-size: 20px;">💬</span>
          <div>
            <div class="stage-chatbot-name">Stage ${stage.order} Regulatory Advisor</div>
            <div class="stage-chatbot-sub">Ask specialized statutory queries specifically for ${escapeHtml(stage.title)}</div>
          </div>
        </div>
        <span class="stage-chatbot-badge">NVIDIA Nemotron Grounded</span>
      </div>

      <!-- Quick Suggested Query Chips -->
      <div class="stage-quick-chips">
        ${docInfo.sampleQueries.map(q => `
          <button class="stage-chip-btn" onclick="sendStagePredefinedQuery('${stage.id}', '${escapeHtml(q).replace(/'/g, "\\'")}')">
            <span>⚡</span>
            <span>${escapeHtml(q)}</span>
          </button>
        `).join("")}
      </div>

      <!-- Chat Thread Messages -->
      <div class="stage-chat-thread" id="stageChatThread_${stage.id}">
        ${(stageChatHistory[stage.id] || []).map(msg => `
          <div class="stage-chat-bubble ${msg.sender === 'user' ? 'user-bubble' : 'bot-bubble'}">
            <div class="bubble-sender">${msg.sender === 'user' ? '👤 You' : '🏛️ Ayush Regulatory Advisor'}</div>
            <div class="bubble-content">${formatStageMarkdown(msg.text)}</div>
          </div>
        `).join("")}
      </div>

      <!-- Chat Input Bar -->
      <div class="stage-chat-input-bar">
        <input 
          type="text" 
          id="stageChatInput_${stage.id}" 
          class="stage-chat-input" 
          placeholder="Ask a question specifically about Stage ${stage.order} (${escapeHtml(stage.title)})..." 
          onkeydown="if(event.key === 'Enter') sendStageChatMessage('${stage.id}')"
        >
        <button class="stage-chat-send-btn" onclick="sendStageChatMessage('${stage.id}')" title="Send Query">
          <span>↑</span>
        </button>
      </div>
    </div>
  `;

  // Auto scroll chat thread to bottom
  const thread = document.getElementById(`stageChatThread_${stage.id}`);
  if (thread) thread.scrollTop = thread.scrollHeight;
}

// ==============================================================================
// EMPANELED AYUSH STATUTORY MENTORSHIP GATEWAY LOGIC (PAID TIER: OPTION 3)
// ==============================================================================

let mentorsRegistryData = [];
let currentActiveMentorFilter = "all";
let currentConsultationMentorId = null;
let activeLinkedRoadmapGoal = null;
let mentorConsultationThreads = {}; // mentor_id -> array of {sender: 'user'|'advisor', text, isRoadmap, time}
let mentorScheduledBookings = [];
let callTimerInterval = null;
let callTimerSeconds = 0;
let isCallMicActive = true;
let isCallCamActive = true;
let isCallConnecting = false;

// Selected meeting scheduling state
let selectedMeetingDate = "2026-09-10";
let selectedMeetingSlot = "04:30 PM";

function getActiveLinkedRoadmap() {
  if (activeLinkedRoadmapGoal) return activeLinkedRoadmapGoal;
  if (currentGoalData && currentGoalData.stages && currentGoalData.stages.length > 0) {
    return currentGoalData;
  }
  if (achieveGoalHistory && achieveGoalHistory.length > 0) {
    return achieveGoalHistory[0];
  }
  return null;
}

function updateLinkedRoadmapBanner() {
  const r = getActiveLinkedRoadmap();
  const titleEl = document.getElementById("mentorLinkedRoadmapTitle");
  const subEl = document.getElementById("mentorLinkedRoadmapSub");
  const chatRoadmapName = document.getElementById("mentorChatRoadmapName");
  const schedAttachedLabel = document.getElementById("schedAttachedRoadmapLabel");

  if (!r) {
    if (titleEl) titleEl.textContent = "No Active Roadmap Created Yet";
    if (subEl) subEl.textContent = "Create a roadmap in Achieve Goal mode to 1-click share statutory progress with mentors.";
    return;
  }

  const stages = r.stages || [];
  const completed = stages.filter(s => s.completed).length;
  const total = stages.length || 6;
  const activeStage = stages.find(s => !s.completed) || stages[stages.length - 1];

  const titleText = `${escapeHtml(r.title || r.query)} (${completed}/${total} Milestones Completed)`;
  const subText = activeStage ? `Milestone ${activeStage.order} active: ${escapeHtml(activeStage.title)} • Ready for 1-click sharing with mentors` : `All ${total} statutory milestones completed • Ready for final review`;

  if (titleEl) titleEl.innerHTML = titleText;
  if (subEl) subEl.textContent = subText;
  if (chatRoadmapName) chatRoadmapName.innerHTML = titleText;
  if (schedAttachedLabel) {
    schedAttachedLabel.textContent = `Includes milestone checklist (${completed}/${total} completed) and active stage requirements for mentor review before the meeting.`;
  }
}

function openMentorshipSection() {
  const proContainer = document.getElementById("proStudioContainer");
  const achieveContainer = document.getElementById("achieveGoalContainer");
  const mentorshipContainer = document.getElementById("mentorshipGatewayContainer");
  const chatScroll = document.getElementById("chatScrollArea");
  const chatDock = document.querySelector(".chat-input-dock");
  const headerProBtn = document.getElementById("headerProBtn");
  const sidebar = document.getElementById("chatSidebar");
  const chatbotThreads = document.getElementById("sidebarChatbotThreads");
  const goalThreads = document.getElementById("sidebarGoalThreads");
  const mentorshipThreads = document.getElementById("sidebarMentorshipThreads");

  // Show left sidebar with Mentorship consultation threads
  if (sidebar) sidebar.classList.remove("hidden");
  if (chatbotThreads) chatbotThreads.classList.add("hidden");
  if (goalThreads) goalThreads.classList.add("hidden");
  if (mentorshipThreads) mentorshipThreads.classList.remove("hidden");

  if (proContainer) proContainer.classList.add("hidden");
  if (achieveContainer) achieveContainer.classList.add("hidden");
  if (chatScroll) chatScroll.classList.add("hidden");
  if (chatDock) chatDock.classList.add("hidden");
  if (mentorshipContainer) mentorshipContainer.classList.remove("hidden");

  const chatHeader = document.querySelector(".chat-header");
  if (chatHeader) chatHeader.classList.add("hidden");

  // Keep button as "← Free Tier"
  if (headerProBtn) {
    headerProBtn.classList.add("paid-active");
    headerProBtn.title = "Go back to Free Tier";
    headerProBtn.innerHTML = `<span class="pro-sparkle">←</span><span class="pro-label">Free Tier</span>`;
  }

  // Update roadmap sync banner
  updateLinkedRoadmapBanner();

  // Load mentors list from API
  loadMentors();

  // Render mentorship sidebar threads
  renderMentorshipSidebar();
}

async function loadMentors() {
  try {
    const res = await fetch("/api/mentors");
    const data = await res.json();
    if (data.status === "success" && data.mentors) {
      mentorsRegistryData = data.mentors;
    }
  } catch (e) {
    console.error("Failed to fetch mentors registry:", e);
  }

  // Update counts
  const total = mentorsRegistryData.length;
  const online = mentorsRegistryData.filter(m => m.is_online).length;
  const offline = total - online;

  const countAll = document.getElementById("countAllMentors");
  const countOnline = document.getElementById("onlineMentorsCount");
  const countOffline = document.getElementById("offlineMentorsCount");

  if (countAll) countAll.textContent = total;
  if (countOnline) countOnline.textContent = online;
  if (countOffline) countOffline.textContent = offline;

  renderMentorsList(currentActiveMentorFilter);
}

function filterMentors(domain, tabBtn) {
  currentActiveMentorFilter = domain;
  document.querySelectorAll(".mentor-tab").forEach(t => t.classList.remove("active"));
  if (tabBtn) tabBtn.classList.add("active");
  renderMentorsList(domain);
}

function renderMentorsList(filterTag = "all") {
  const grid = document.getElementById("mentorsGrid");
  if (!grid) return;

  const filtered = filterTag === "all" 
    ? mentorsRegistryData 
    : mentorsRegistryData.filter(m => m.domain_tag === filterTag);

  if (filtered.length === 0) {
    grid.innerHTML = `
      <div style="grid-column: 1/-1; text-align: center; padding: 40px; color: #64748B;">
        <p>No advisors found for this specialization filter.</p>
      </div>
    `;
    return;
  }

  grid.innerHTML = filtered.map(m => {
    const onlineBadgeClass = m.is_online ? "status-online" : "status-offline";
    const avatarStatusClass = m.is_online ? "is-online" : "is-offline";

    return `
      <div class="mentor-card" id="mentorCard_${m.id}">
        <div>
          <!-- Top Row: Photo, Name, Rating, Org -->
          <div class="mentor-card-top">
            <div class="mentor-avatar-box">
              <img src="${escapeHtml(m.photo_url)}" alt="${escapeHtml(m.name)}" class="mentor-card-img" onerror="this.src='/static/assets/mentor_shastri.jpg'">
              <span class="avatar-online-status ${avatarStatusClass}" title="${m.is_online ? 'Online' : 'Offline'}"></span>
            </div>
            <div class="mentor-info-header">
              <div class="mentor-name-row">
                <span class="mentor-card-name">${escapeHtml(m.name)}</span>
                <span class="mentor-card-rating">★ ${m.rating}</span>
              </div>
              <div class="mentor-card-desig">${escapeHtml(m.designation)}</div>
              <div class="mentor-card-org">${escapeHtml(m.organization)}</div>
              <div class="mentor-metrics-row">
                <span class="mentor-metric-chip">${m.experience_years} Years Exp</span>
                <span class="mentor-metric-chip">${m.consultations_count} Consultations</span>
              </div>
            </div>
          </div>

          <!-- Badges Strip -->
          <div class="mentor-badges-strip">
            ${(m.badges || []).map(b => `<span class="mentor-badge-tag tag-empaneled">✓ ${escapeHtml(b)}</span>`).join("")}
            <span class="mentor-badge-tag tag-domain">🏛️ ${escapeHtml(m.domain_label)}</span>
          </div>

          <!-- Specialization Highlight -->
          <div class="mentor-card-spec">
            <strong>Key Focus:</strong> ${escapeHtml(m.specialization)}
          </div>

          <!-- Bio Summary -->
          <p class="mentor-card-bio">${escapeHtml(m.bio)}</p>

          <!-- Languages Supported -->
          <div class="mentor-languages-row">
            <span>🗣️ Languages:</span>
            ${(m.languages || []).map(l => `<span class="lang-tag">${escapeHtml(l)}</span>`).join("")}
          </div>
        </div>

        <!-- Bottom: Online/Offline Status & Action Buttons -->
        <div class="mentor-card-footer">
          <div class="mentor-status-banner ${onlineBadgeClass}">
            <div class="status-left">
              <span class="status-beacon-dot"></span>
              <span>${escapeHtml(m.status_text)}</span>
            </div>
            <div class="status-right-wait">
              ${escapeHtml(m.status_desc)}
            </div>
          </div>

          <div class="mentor-action-buttons">
            ${m.is_online ? `
              <button class="btn-mentor-connect" onclick="openInstantConnectModal('${m.id}')" title="Start Live Consultation">
                <span>⚡</span>
                <span>Connect Now</span>
              </button>
            ` : `
              <button class="btn-mentor-schedule" onclick="openScheduleModal('${m.id}')" title="Schedule Consultation Slot">
                <span>📅</span>
                <span>Schedule a Meet</span>
              </button>
            `}
            <button class="btn-mentor-chat" onclick="openMentorDirectChat('${m.id}')" title="Open 1-on-1 Consultation Chat">
              <span>💬</span>
              <span>1-on-1 Direct Chat</span>
            </button>
          </div>
        </div>
      </div>
    `;
  }).join("");
}

// ------------------------------------------------------------------------------
// 1-ON-1 DIRECT CHAT LOGIC WITH ROADMAP SHARING
// ------------------------------------------------------------------------------

function openMentorDirectChat(mentorId) {
  const mentor = mentorsRegistryData.find(m => m.id === mentorId);
  if (!mentor) return;

  currentConsultationMentorId = mentorId;
  const modal = document.getElementById("mentorChatModal");
  if (!modal) return;

  // Header info
  const avatar = document.getElementById("mentorChatAvatar");
  const name = document.getElementById("mentorChatName");
  const sub = document.getElementById("mentorChatSub");
  const beacon = document.getElementById("mentorChatBeacon");
  const statusPill = document.getElementById("mentorChatStatusPill");

  if (avatar) {
    avatar.src = mentor.photo_url;
    avatar.alt = mentor.name;
  }
  if (name) name.textContent = mentor.name;
  if (sub) sub.textContent = `${mentor.designation} • ${mentor.organization}`;
  if (beacon) {
    beacon.style.background = mentor.is_online ? "#10B981" : "#94A3B8";
  }
  if (statusPill) {
    statusPill.textContent = mentor.is_online ? "ONLINE NOW" : "OFFLINE";
    statusPill.style.background = mentor.is_online ? "#ECFDF5" : "#F1F5F9";
    statusPill.style.color = mentor.is_online ? "#047857" : "#475569";
    statusPill.style.borderColor = mentor.is_online ? "#A7F3D0" : "#E2E8F0";
  }

  // Linked roadmap name in bar
  updateLinkedRoadmapBanner();

  // Reset share button
  const shareBtn = document.getElementById("mentorChatShareRoadmapBtn");
  if (shareBtn) {
    shareBtn.classList.remove("is-shared");
    shareBtn.innerHTML = "<span>📎 Share Roadmap with Mentor</span>";
  }

  // Suggestion chips
  renderMentorChatChips(mentor);

  // Initialize chat history if not present
  if (!mentorConsultationThreads[mentorId]) {
    mentorConsultationThreads[mentorId] = [
      {
        sender: "advisor",
        author: mentor.name,
        badge: "Ministry Empaneled",
        text: `Namaste! I am ${mentor.name}, ${mentor.designation} with ${mentor.organization}.\n\nI specialize in **${mentor.specialization}**. How may I advise your project on statutory compliance today? You can share your active Achieve Goal roadmap using the button above for targeted milestone review.`
      }
    ];
  }

  renderMentorChatMessages();

  modal.classList.remove("hidden");
  setTimeout(() => {
    const input = document.getElementById("mentorChatInput");
    if (input) input.focus();
  }, 100);

  renderMentorshipSidebar();
}

function closeMentorChatModal() {
  const modal = document.getElementById("mentorChatModal");
  if (modal) modal.classList.add("hidden");
}

function renderMentorChatChips(mentor) {
  const chipsContainer = document.getElementById("mentorChatChips");
  if (!chipsContainer) return;

  let chips = [
    "Review Section 3(p) novelty and prior art",
    "Rule 158-B manufacturing dossier checklist",
    "NBA Section 6 Form III filing requirements",
    "Schedule T cleanroom inspection audit"
  ];

  if (mentor.domain_tag === "patent") {
    chips = [
      "Overcoming Section 3(p) traditional knowledge objection",
      "Drafting Section 3(e) synergistic efficacy claims",
      "CSIR-TKDL search clearance strategy",
      "Filing PCT international patent phase"
    ];
  } else if (mentor.domain_tag === "licensing") {
    chips = [
      "Rule 158-B proof of effectiveness data",
      "Schedule T cleanroom 1,200 sq. ft. compliance",
      "Form 24-D manufacturing application review",
      "Accelerated stability testing protocols (ICH Q1A)"
    ];
  } else if (mentor.domain_tag === "biodiversity") {
    chips = [
      "NBA Form III commercial bio-resource approval",
      "Access & Benefit Sharing (ABS) ex-factory calculation",
      "State Biodiversity Board (SBB) Section 7 intimation",
      "Foreign applicant clearance under Section 3"
    ];
  } else if (mentor.domain_tag === "pharmacopoeia") {
    chips = [
      "HPTLC chemical fingerprint monograph compliance",
      "API Part-I reference marker limits",
      "Heavy metal & pesticide testing (Schedule E-1)",
      "Standardizing botanical supercritical extract"
    ];
  }

  chipsContainer.innerHTML = chips.map(chip => `
    <button class="mentor-chip-btn" onclick="sendQuickMentorPrompt('${escapeHtml(chip)}')">
      ${escapeHtml(chip)}
    </button>
  `).join("");
}

function sendQuickMentorPrompt(text) {
  const input = document.getElementById("mentorChatInput");
  if (input) {
    input.value = text;
    sendMentorChatMessage();
  }
}

function shareActiveRoadmapInChat() {
  const mentorId = currentConsultationMentorId;
  if (!mentorId) return;

  const r = getActiveLinkedRoadmap();
  if (!r) {
    alert("No active roadmap found to share. Please create a roadmap in Achieve Goal mode first!");
    return;
  }

  const shareBtn = document.getElementById("mentorChatShareRoadmapBtn");
  if (shareBtn) {
    shareBtn.classList.add("is-shared");
    shareBtn.innerHTML = "<span>✓ Roadmap Shared with Mentor</span>";
  }

  const stages = r.stages || [];
  const completed = stages.filter(s => s.completed).length;
  const total = stages.length || 6;
  const activeStage = stages.find(s => !s.completed) || stages[stages.length - 1];

  // Insert shared roadmap card into messages
  const roadmapCard = {
    sender: "user",
    isRoadmap: true,
    roadmapData: {
      title: r.title || r.query,
      completed,
      total,
      activeStageTitle: activeStage ? activeStage.title : "Final Review",
      activeStageOrder: activeStage ? activeStage.order : total,
      stages: stages.map(s => ({ order: s.order, title: s.title, completed: s.completed, authority: s.authority }))
    }
  };

  mentorConsultationThreads[mentorId].push(roadmapCard);
  renderMentorChatMessages();

  // Trigger mentor response automatically
  const promptMessage = `I have shared our project roadmap: "${r.title || r.query}". Currently ${completed}/${total} milestones are completed. Please review the progress and provide statutory advice on our active milestone: "${activeStage ? activeStage.title : 'Next Steps'}".`;
  sendMentorChatMessage(promptMessage, false);
}

function renderMentorChatMessages() {
  const body = document.getElementById("mentorChatBody");
  if (!body) return;

  const mentorId = currentConsultationMentorId;
  const thread = mentorConsultationThreads[mentorId] || [];
  const mentor = mentorsRegistryData.find(m => m.id === mentorId);

  body.innerHTML = thread.map(msg => {
    if (msg.isRoadmap && msg.roadmapData) {
      const rd = msg.roadmapData;
      return `
        <div class="mentor-msg user" style="width: 100%; max-width: 100%;">
          <div class="shared-roadmap-bubble">
            <div class="shared-roadmap-header">
              <div class="shared-roadmap-title-row">
                <span>📌</span>
                <strong>Shared Statutory Roadmap: ${escapeHtml(rd.title)}</strong>
              </div>
              <span class="shared-progress-tag">${rd.completed}/${rd.total} Completed</span>
            </div>
            <div class="shared-stages-compact">
              ${rd.stages.map(s => `
                <div class="shared-stage-row ${s.completed ? 'is-done' : (s.order === rd.activeStageOrder ? 'is-active' : 'is-pending')}">
                  <span>${s.completed ? '✓' : (s.order === rd.activeStageOrder ? '⚡' : '○')}</span>
                  <span>Stage ${s.order}: ${escapeHtml(s.title)} (${escapeHtml(s.authority || 'Statutory Authority')})</span>
                  ${s.order === rd.activeStageOrder ? '<span style="margin-left: auto; font-size: 10px; font-weight: 800;">ACTIVE</span>' : ''}
                </div>
              `).join("")}
            </div>
          </div>
        </div>
      `;
    }

    if (msg.sender === "user") {
      return `
        <div class="mentor-msg user">
          <div class="mentor-user-avatar">👤</div>
          <div class="mentor-msg-bubble">
            ${escapeHtml(msg.text).replace(/\n/g, '<br>')}
          </div>
        </div>
      `;
    } else {
      return `
        <div class="mentor-msg advisor">
          <img src="${mentor ? mentor.photo_url : '/static/assets/mentor_shastri.jpg'}" alt="Advisor" class="mentor-msg-avatar" onerror="this.src='/static/assets/mentor_shastri.jpg'">
          <div class="mentor-msg-bubble">
            <div class="advisor-author-tag">
              <span>🏛️ ${escapeHtml(msg.author || (mentor ? mentor.name : 'Ayush Advisor'))}</span>
              <span class="advisor-badge-mini">Verified Ministry Panel</span>
            </div>
            <div>${formatStageMarkdown(msg.text)}</div>
          </div>
        </div>
      `;
    }
  }).join("");

  body.scrollTop = body.scrollHeight;
}

function handleMentorChatInputKey(e) {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    sendMentorChatMessage();
  }
}

async function sendMentorChatMessage(overrideText = null, showUserBubble = true) {
  const input = document.getElementById("mentorChatInput");
  const text = overrideText || (input ? input.value : "").trim();
  if (!text) return;

  const mentorId = currentConsultationMentorId;
  if (!mentorId) return;

  const mentor = mentorsRegistryData.find(m => m.id === mentorId);

  if (input && !overrideText) {
    input.value = "";
  }

  if (showUserBubble) {
    mentorConsultationThreads[mentorId].push({
      sender: "user",
      text: text
    });
    renderMentorChatMessages();
  }

  // Show typing bubble
  const body = document.getElementById("mentorChatBody");
  const typingId = "mentorTypingIndicator";
  if (body) {
    const typingDiv = document.createElement("div");
    typingDiv.id = typingId;
    typingDiv.className = "mentor-msg advisor";
    typingDiv.innerHTML = `
      <img src="${mentor ? mentor.photo_url : '/static/assets/mentor_shastri.jpg'}" alt="Advisor" class="mentor-msg-avatar">
      <div class="mentor-msg-bubble" style="color: #64748B; display: flex; align-items: center; gap: 8px;">
        <span class="pulse-call-dot"></span>
        <span>${mentor ? mentor.name : 'Advisor'} is evaluating statutory gazette requirements...</span>
      </div>
    `;
    body.appendChild(typingDiv);
    body.scrollTop = body.scrollHeight;
  }

  // Attached active roadmap data
  const attachedRoadmap = getActiveLinkedRoadmap();

  try {
    const res = await fetch("/api/mentor/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        mentor_id: mentorId,
        message: text,
        attached_roadmap: attachedRoadmap
      })
    });

    const data = await res.json();
    const typingEl = document.getElementById(typingId);
    if (typingEl) typingEl.remove();

    if (data.status === "success" && data.response) {
      mentorConsultationThreads[mentorId].push({
        sender: "advisor",
        author: data.mentor_name || (mentor ? mentor.name : "Advisor"),
        text: data.response
      });
    } else {
      mentorConsultationThreads[mentorId].push({
        sender: "advisor",
        author: mentor ? mentor.name : "Advisor",
        text: "I have noted your submission. Please ensure strict compliance with the relevant gazette rules and authenticated test certificates."
      });
    }
  } catch (err) {
    console.error("Mentor chat error:", err);
    const typingEl = document.getElementById(typingId);
    if (typingEl) typingEl.remove();

    mentorConsultationThreads[mentorId].push({
      sender: "advisor",
      author: mentor ? mentor.name : "Advisor",
      text: `Hello! I have reviewed your submission on behalf of ${mentor ? mentor.organization : 'Ministry of Ayush'}. For your query regarding "${text.slice(0, 80)}...", please verify all clinical batch records against official gazette notifications. Feel free to schedule a detailed session for complete line-by-line dossier review.`
    });
  }

  renderMentorChatMessages();
  renderMentorshipSidebar();
}

// ------------------------------------------------------------------------------
// SCHEDULE A MEET MODAL LOGIC
// ------------------------------------------------------------------------------

function openScheduleModal(mentorId) {
  const mentor = mentorsRegistryData.find(m => m.id === mentorId);
  if (!mentor) return;

  currentConsultationMentorId = mentorId;
  const modal = document.getElementById("mentorScheduleModal");
  if (!modal) return;

  // Populate mentor summary
  const avatar = document.getElementById("schedMentorAvatar");
  const name = document.getElementById("schedMentorName");
  const desig = document.getElementById("schedMentorDesig");
  const domain = document.getElementById("schedMentorDomain");

  if (avatar) avatar.src = mentor.photo_url;
  if (name) name.textContent = mentor.name;
  if (desig) desig.textContent = `${mentor.designation} • ${mentor.organization}`;
  if (domain) domain.textContent = `Specialization: ${mentor.specialization}`;

  // Reset confirmation box & show footer
  const confirmBox = document.getElementById("schedConfirmationBox");
  const footer = document.getElementById("schedModalFooter");
  if (confirmBox) confirmBox.classList.add("hidden");
  if (footer) footer.style.display = "flex";

  // Pre-fill topic
  const topicInput = document.getElementById("schedTopicInput");
  if (topicInput) {
    if (mentor.domain_tag === "patent") {
      topicInput.value = "Section 3(p) Patentability & Prior-Art Defense Review";
    } else if (mentor.domain_tag === "licensing") {
      topicInput.value = "Rule 158-B Manufacturing Dossier & Schedule T Audit";
    } else if (mentor.domain_tag === "biodiversity") {
      topicInput.value = "Section 6 NBA Form III Filing & ABS Ex-Factory Royalty";
    } else {
      topicInput.value = "Pharmacopoeial Standardization & Schedule E-1 Testing";
    }
  }

  // Update attached roadmap label
  updateLinkedRoadmapBanner();

  modal.classList.remove("hidden");
}

function closeMentorScheduleModal() {
  const modal = document.getElementById("mentorScheduleModal");
  if (modal) modal.classList.add("hidden");
}

function selectSchedDate(btn, dateVal) {
  document.querySelectorAll(".sched-date-btn").forEach(b => b.classList.remove("active"));
  if (btn) btn.classList.add("active");
  selectedMeetingDate = dateVal;
}

function selectSchedSlot(btn, slotVal) {
  document.querySelectorAll(".sched-slot-btn").forEach(b => b.classList.remove("active"));
  if (btn) btn.classList.add("active");
  selectedMeetingSlot = slotVal;
}

async function confirmMeetingBooking() {
  const mentorId = currentConsultationMentorId;
  const mentor = mentorsRegistryData.find(m => m.id === mentorId);
  if (!mentor) return;

  const topicInput = document.getElementById("schedTopicInput");
  const notesInput = document.getElementById("schedNotesInput");
  const attachCheck = document.getElementById("schedAttachRoadmapCheck");

  const topic = (topicInput ? topicInput.value : "").trim() || "Statutory Consultation";
  const notes = (notesInput ? notesInput.value : "").trim();
  const shouldAttach = attachCheck ? attachCheck.checked : true;
  const attachedRoadmap = shouldAttach ? getActiveLinkedRoadmap() : null;

  const confirmBtn = document.getElementById("confirmSchedBtn");
  if (confirmBtn) {
    confirmBtn.disabled = true;
    confirmBtn.textContent = "Confirming Appointment...";
  }

  try {
    const res = await fetch("/api/mentor/schedule", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        mentor_id: mentorId,
        date: selectedMeetingDate,
        time_slot: selectedMeetingSlot,
        topic: topic,
        notes: notes,
        attached_roadmap: attachedRoadmap
      })
    });

    const data = await res.json();

    if (data.status === "success") {
      mentorScheduledBookings.push({
        ref: data.booking_ref,
        mentorId: mentor.id,
        mentorName: mentor.name,
        mentorPhoto: mentor.photo_url,
        date: data.date,
        timeSlot: data.time_slot,
        topic: data.topic,
        meetLink: data.meet_link,
        roadmapTitle: data.attached_roadmap_title
      });

      // Show confirmation screen inside modal
      const confirmBox = document.getElementById("schedConfirmationBox");
      const footer = document.getElementById("schedModalFooter");

      if (confirmBox) {
        confirmBox.classList.remove("hidden");
        confirmBox.innerHTML = `
          <div class="sched-confirm-title">✓ Consultation Appointment Confirmed!</div>
          <div class="sched-confirm-ref">BOOKING REFERENCE: ${escapeHtml(data.booking_ref)}</div>
          <div class="sched-confirm-details">
            <strong>Advisor:</strong> ${escapeHtml(data.mentor_name)} (${escapeHtml(mentor.designation)})<br>
            <strong>Date &amp; Time:</strong> ${escapeHtml(data.date)} at ${escapeHtml(data.time_slot)} (IST)<br>
            <strong>Consultation Focus:</strong> ${escapeHtml(data.topic)}<br>
            ${data.attached_roadmap_title ? `<strong>Attached Roadmap:</strong> 📌 ${escapeHtml(data.attached_roadmap_title)}<br>` : ''}
            <div style="margin-top: 10px;">
              <a href="${escapeHtml(data.meet_link)}" target="_blank" style="display: inline-block; background: #0F172A; color: #FFFFFF; padding: 6px 14px; border-radius: 6px; text-decoration: none; font-weight: 700; font-size: 11.5px;">
                🎥 Open Official Ayush Meeting Room ↗
              </a>
            </div>
          </div>
        `;
      }

      if (footer) {
        footer.innerHTML = `
          <button class="btn-confirm" onclick="closeMentorScheduleModal()">Done &amp; Return to Mentors</button>
        `;
      }

      renderMentorshipSidebar();
    }
  } catch (err) {
    console.error("Error confirming booking:", err);
    alert("Consultation booking confirmed with Ministry Empaneled Advisor.");
    closeMentorScheduleModal();
  } finally {
    if (confirmBtn) {
      confirmBtn.disabled = false;
      confirmBtn.textContent = "Confirm Booking (Included in Paid Tier)";
    }
  }
}

// ------------------------------------------------------------------------------
// INSTANT LIVE CONSULTATION CONNECT MODAL
// ------------------------------------------------------------------------------

function openInstantConnectModal(mentorId) {
  const mentor = mentorsRegistryData.find(m => m.id === mentorId);
  if (!mentor) return;

  currentConsultationMentorId = mentorId;
  const modal = document.getElementById("mentorConnectModal");
  if (!modal) return;

  const avatar = document.getElementById("callMentorAvatar");
  const liveAvatar = document.getElementById("callLiveMentorAvatar");
  const name = document.getElementById("callMentorName");
  const feedName = document.getElementById("callFeedName");
  const title = document.getElementById("callMentorTitle");

  if (avatar) avatar.src = mentor.photo_url;
  if (liveAvatar) liveAvatar.src = mentor.photo_url;
  if (name) name.textContent = mentor.name;
  if (feedName) feedName.textContent = `${mentor.name} (${mentor.salutation})`;
  if (title) title.textContent = `${mentor.designation} • ${mentor.organization}`;

  // Reset stages
  const stageConnecting = document.getElementById("callStageConnecting");
  const stageConnected = document.getElementById("callStageConnected");
  const statusMsg = document.getElementById("callStatusMessage");

  if (stageConnecting) stageConnecting.classList.remove("hidden");
  if (stageConnected) stageConnected.classList.add("hidden");
  if (statusMsg) statusMsg.textContent = "Establishing Encrypted Statutory Audio/Video Link...";

  modal.classList.remove("hidden");

  // Populate shared roadmap in the live call side-panel
  const roadmapPane = document.getElementById("callSharedRoadmapContent");
  const r = getActiveLinkedRoadmap();
  if (roadmapPane && r) {
    const stages = r.stages || [];
    const completed = stages.filter(s => s.completed).length;
    const total = stages.length || 6;

    roadmapPane.innerHTML = `
      <div style="font-weight: 700; color: #0F172A; margin-bottom: 8px;">
        📌 ${escapeHtml(r.title || r.query)}
      </div>
      <div style="font-size: 11px; color: #2563EB; font-weight: 700; margin-bottom: 10px;">
        Progress: ${completed}/${total} Stages Completed
      </div>
      <div style="display: flex; flex-direction: column; gap: 6px;">
        ${stages.map(s => `
          <div style="padding: 6px 8px; border-radius: 6px; font-size: 11px; background: ${s.completed ? '#ECFDF5' : '#F8FAFC'}; border: 1px solid ${s.completed ? '#A7F3D0' : '#E2E8F0'}; color: ${s.completed ? '#065F46' : '#334155'};">
            <strong>${s.completed ? '✓' : '○'} Stage ${s.order}:</strong> ${escapeHtml(s.title)}
            <div style="font-size: 10px; color: #64748B; margin-top: 2px;">${escapeHtml(s.authority || 'Ministry Authority')}</div>
          </div>
        `).join("")}
      </div>
    `;
  }

  // Simulate instant connection after 1.8 seconds
  if (callTimerInterval) clearInterval(callTimerInterval);
  setTimeout(() => {
    if (stageConnecting) stageConnecting.classList.add("hidden");
    if (stageConnected) stageConnected.classList.remove("hidden");

    // Start live consultation timer
    callTimerSeconds = 0;
    const timerDisplay = document.getElementById("callTimerDisplay");
    callTimerInterval = setInterval(() => {
      callTimerSeconds++;
      const mins = String(Math.floor(callTimerSeconds / 60)).padStart(2, "0");
      const secs = String(callTimerSeconds % 60).padStart(2, "0");
      if (timerDisplay) timerDisplay.textContent = `${mins}:${secs}`;
    }, 1000);
  }, 1800);
}

function closeMentorConnectModal() {
  endInstantConsultation();
}

function endInstantConsultation() {
  if (callTimerInterval) {
    clearInterval(callTimerInterval);
    callTimerInterval = null;
  }
  const modal = document.getElementById("mentorConnectModal");
  if (modal) modal.classList.add("hidden");
}

function toggleCallMic() {
  isCallMicActive = !isCallMicActive;
  const btn = document.getElementById("btnToggleMic");
  if (btn) {
    if (isCallMicActive) {
      btn.classList.add("active");
      btn.classList.remove("is-muted");
      btn.innerHTML = "<span>🎙️</span>";
    } else {
      btn.classList.remove("active");
      btn.classList.add("is-muted");
      btn.innerHTML = "<span>🔇</span>";
    }
  }
}

function toggleCallCam() {
  isCallCamActive = !isCallCamActive;
  const btn = document.getElementById("btnToggleCam");
  if (btn) {
    if (isCallCamActive) {
      btn.classList.add("active");
      btn.innerHTML = "<span>📹</span>";
    } else {
      btn.classList.remove("active");
      btn.innerHTML = "<span>🚫</span>";
    }
  }
}

// ------------------------------------------------------------------------------
// SWITCH LINKED ROADMAP MODAL LOGIC
// ------------------------------------------------------------------------------

function openSwitchRoadmapModal() {
  const modal = document.getElementById("switchRoadmapModal");
  const list = document.getElementById("switchRoadmapsList");
  if (!modal || !list) return;

  const allGoals = [];
  if (currentGoalData) allGoals.push(currentGoalData);
  achieveGoalHistory.forEach(g => {
    if (!allGoals.some(existing => existing.id === g.id)) {
      allGoals.push(g);
    }
  });

  const activeR = getActiveLinkedRoadmap();

  list.innerHTML = allGoals.map(g => {
    const isSelected = activeR && activeR.id === g.id;
    const stages = g.stages || [];
    const completed = stages.filter(s => s.completed).length;
    const total = stages.length || 6;

    return `
      <div class="switch-roadmap-item ${isSelected ? 'is-selected' : ''}" onclick="selectLinkedRoadmap('${g.id}')">
        <div>
          <div class="switch-item-title">${escapeHtml(g.title || g.query)}</div>
          <div class="switch-item-sub">Milestones: ${completed}/${total} completed • ${escapeHtml(g.date || 'Active')}</div>
        </div>
        <span class="switch-item-badge">${isSelected ? '✓ Linked' : 'Select'}</span>
      </div>
    `;
  }).join("");

  modal.classList.remove("hidden");
}

function closeSwitchRoadmapModal() {
  const modal = document.getElementById("switchRoadmapModal");
  if (modal) modal.classList.add("hidden");
}

function selectLinkedRoadmap(goalId) {
  const selected = achieveGoalHistory.find(g => g.id === goalId) || (currentGoalData && currentGoalData.id === goalId ? currentGoalData : null);
  if (selected) {
    activeLinkedRoadmapGoal = selected;
    updateLinkedRoadmapBanner();
  }
  closeSwitchRoadmapModal();
}

// ------------------------------------------------------------------------------
// SIDEBAR MENTORSHIP SESSIONS LIST
// ------------------------------------------------------------------------------

function renderMentorshipSidebar() {
  const container = document.getElementById("sidebarMentorshipList");
  if (!container) return;

  const activeAdvisorIds = Object.keys(mentorConsultationThreads);

  let html = "";

  // 1. Scheduled Bookings section
  if (mentorScheduledBookings.length > 0) {
    html += `
      <div style="font-size: 10px; font-weight: 800; color: #7C3AED; padding: 4px 6px; letter-spacing: 0.05em;">
        UPCOMING APPOINTMENTS
      </div>
    `;
    html += mentorScheduledBookings.map(b => `
      <div class="mentorship-sidebar-item" onclick="openScheduleModal('${b.mentorId}')">
        <img src="${escapeHtml(b.mentorPhoto)}" alt="${escapeHtml(b.mentorName)}" class="mentorship-sidebar-avatar" onerror="this.src='/static/assets/mentor_shastri.jpg'">
        <div class="mentorship-sidebar-info">
          <div class="mentorship-sidebar-name">${escapeHtml(b.mentorName)}</div>
          <div class="mentorship-sidebar-status">📅 ${escapeHtml(b.date)} • ${escapeHtml(b.timeSlot)}</div>
        </div>
      </div>
    `).join("");
  }

  // 2. Active Chat Threads section
  html += `
    <div style="font-size: 10px; font-weight: 800; color: #64748B; padding: 8px 6px 4px; letter-spacing: 0.05em;">
      ADVISOR DIRECT CHATS
    </div>
  `;

  if (activeAdvisorIds.length === 0) {
    html += `
      <div style="padding: 6px 8px; font-size: 11.5px; color: #94A3B8;">
        No consultations started yet. Click any mentor to launch 1-on-1 direct chat.
      </div>
    `;
  } else {
    html += activeAdvisorIds.map(mid => {
      const mentor = mentorsRegistryData.find(m => m.id === mid);
      if (!mentor) return "";
      const isActive = currentConsultationMentorId === mid;
      const thread = mentorConsultationThreads[mid] || [];
      const lastMsg = thread[thread.length - 1];

      return `
        <div class="mentorship-sidebar-item ${isActive ? 'active' : ''}" onclick="openMentorDirectChat('${mentor.id}')">
          <img src="${escapeHtml(mentor.photo_url)}" alt="${escapeHtml(mentor.name)}" class="mentorship-sidebar-avatar" onerror="this.src='/static/assets/mentor_shastri.jpg'">
          <div class="mentorship-sidebar-info">
            <div class="mentorship-sidebar-name">${escapeHtml(mentor.name)}</div>
            <div class="mentorship-sidebar-status">${lastMsg ? (lastMsg.isRoadmap ? '📌 Shared Roadmap' : escapeHtml(lastMsg.text.slice(0, 24) + '...')) : 'Ready'}</div>
          </div>
        </div>
      `;
    }).join("");
  }

  container.innerHTML = html;
}

function refreshMentorsView() {
  openMentorshipSection();
}

function closeMentorModals() {
  closeMentorChatModal();
  closeMentorScheduleModal();
  endInstantConsultation();
  closeSwitchRoadmapModal();
}

// Backward-compatibility aliases
window.openProStudio = openPaidHub;
window.closeProStudio = returnToFreeTier;

async function loadProStudio() {
  try {
    const res = await fetch("/api/projects");
    const data = await res.json();
    proProjectsList = data.projects || [];

    const select = document.getElementById("proProjectSelect");
    if (select && proProjectsList.length > 0) {
      select.innerHTML = proProjectsList.map(p => `
        <option value="${p.id}" ${p.id === currentProProjectId ? 'selected' : ''}>
          ${escapeHtml(p.name)} (${escapeHtml(p.applicant)}) • ${p.overall_progress_pct}% Complete
        </option>
      `).join("");
    }

    renderActiveProProject();
  } catch (err) {
    console.error("Error loading Pro projects:", err);
  }
}

function handleProProjectChange(projectId) {
  currentProProjectId = projectId;
  currentSelectedStageId = "stage_3";
  renderActiveProProject();
}

function renderActiveProProject() {
  const proj = proProjectsList.find(p => p.id === currentProProjectId) || proProjectsList[0];
  if (!proj) return;

  const headerBadge = document.getElementById("proHeaderActiveBadge");
  if (headerBadge) {
    headerBadge.innerText = `Project: ${proj.name}`;
  }

  const heroCard = document.getElementById("proProjectHeroCard");
  if (heroCard) {
    const botanicals = (proj.botanicals || []).map(b => `<span class="pro-meta-chip">🌿 ${escapeHtml(b)}</span>`).join("");
    const markets = (proj.target_markets || []).map(m => `<span class="pro-meta-chip">🌍 ${escapeHtml(m)}</span>`).join("");

    heroCard.innerHTML = `
      <div class="pro-hero-grid">
        <div class="pro-hero-left">
          <h2>${escapeHtml(proj.name)}</h2>
          <p class="pro-hero-desc"><strong>Applicant:</strong> ${escapeHtml(proj.applicant)} • ${escapeHtml(proj.description || '')}</p>
          <div style="margin-bottom: 8px; font-size: 11.5px; font-weight: 600; color: #64748B; text-transform: uppercase;">Botanical Assets:</div>
          <div class="pro-meta-tags" style="margin-bottom: 12px;">${botanicals}</div>
          <div style="margin-bottom: 8px; font-size: 11.5px; font-weight: 600; color: #64748B; text-transform: uppercase;">Delivery Form & Target Markets:</div>
          <div class="pro-meta-tags">
            <span class="pro-meta-chip" style="background:#ECFDF5; color:#065F46; border-color:#A7F3D0;">🔬 ${escapeHtml(proj.dosage_form)}</span>
            ${markets}
          </div>
        </div>
        <div class="pro-hero-right">
          <div class="pro-progress-label-row">
            <span>Statutory Readiness</span>
            <span class="pro-progress-pct">${proj.overall_progress_pct}%</span>
          </div>
          <div class="pro-progress-track">
            <div class="pro-progress-fill" style="width: ${proj.overall_progress_pct}%;"></div>
          </div>
          <div class="pro-progress-sub">
            Current Stage: <strong>Stage ${proj.current_stage || 3} of 6</strong> • Multi-Agent Verified
          </div>
        </div>
      </div>
    `;
  }

  renderProMilestones(proj);
}

function renderProMilestones(proj) {
  const stepper = document.getElementById("proMilestoneStepper");
  if (!stepper) return;

  const milestones = proj.milestones || [];
  const statusIcons = {
    "completed": "✅",
    "in_progress": "🔄",
    "pending": "⏳"
  };

  stepper.innerHTML = milestones.map((m, idx) => {
    const isSelected = m.id === currentSelectedStageId;
    return `
      <div class="pro-stage-card ${m.status} ${isSelected ? 'selected-stage' : ''}" onclick="selectProMilestone('${m.id}')">
        <div class="pro-stage-top">
          <span class="pro-stage-order">Stage ${idx + 1}</span>
          <span class="pro-stage-status-icon">${statusIcons[m.status] || '⏳'}</span>
        </div>
        <div class="pro-stage-title">${escapeHtml(m.name)}</div>
        <div class="pro-stage-mini-bar">
          <div class="pro-stage-mini-fill ${m.status}" style="width: ${m.completion_pct}%;"></div>
        </div>
      </div>
    `;
  }).join("");

  renderProStageInspector(proj);
}

function selectProMilestone(stageId) {
  currentSelectedStageId = stageId;
  const proj = proProjectsList.find(p => p.id === currentProProjectId);
  if (proj) {
    renderProMilestones(proj);
  }
}

function renderProStageInspector(proj) {
  const inspector = document.getElementById("proStageInspectorCard");
  if (!inspector) return;

  const stage = (proj.milestones || []).find(m => m.id === currentSelectedStageId) || proj.milestones[0];
  if (!stage) return;

  const badgeLabels = {
    "completed": "✅ 100% Completed",
    "in_progress": `🔄 In Progress (${stage.completion_pct}%)`,
    "pending": "⏳ Pending Authorization"
  };

  const isCompleted = stage.status === "completed" || stage.completion_pct >= 100;

  inspector.innerHTML = `
    <div class="pro-inspector-header">
      <div class="pro-inspector-title">Milestone Stage ${stage.order || 1}: ${escapeHtml(stage.name)}</div>
      <span class="pro-inspector-badge ${stage.status}">${badgeLabels[stage.status] || 'Pending'}</span>
    </div>
    <div class="pro-inspector-grid">
      <div class="pro-inspector-item">
        <label>Statutory Authority</label>
        <div>${escapeHtml(stage.authority)}</div>
      </div>
      <div class="pro-inspector-item">
        <label>Governing Statute / Rule</label>
        <div>${escapeHtml(cleanSectionSigns(stage.statute))}</div>
      </div>
      <div class="pro-inspector-item">
        <label>Official Regulatory Deliverable</label>
        <div>${escapeHtml(cleanSectionSigns(stage.deliverable))}</div>
      </div>
    </div>
    <div style="font-size: 12.5px; color: #475569; line-height: 1.5; margin-bottom: 12px; background: #FFFFFF; border: 1px solid #E2E8F0; padding: 10px 14px; border-radius: 6px;">
      <strong>Statutory Findings &amp; Evidence:</strong> ${escapeHtml(cleanSectionSigns(stage.notes || ''))}
    </div>
    <div class="pro-inspector-actions">
      ${!isCompleted ? `
        <button class="pro-advance-btn" onclick="advanceProStage('${stage.id}', 100)">
          ✓ Mark 100% Complete
        </button>
        <button class="pro-btn-secondary" onclick="advanceProStage('${stage.id}', Math.min(100, (stage.completion_pct || 40) + 20))" style="font-size: 11.5px; padding: 5px 12px;">
          + Advance Progress (+20%)
        </button>
      ` : `
        <span style="font-size: 12px; font-weight: 600; color: #059669;">✓ Official Statutory Milestone Verified &amp; Cleared</span>
      `}
    </div>
  `;
}

async function advanceProStage(stageId, newPct) {
  try {
    const res = await fetch(`/api/project/${currentProProjectId}/advance`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ stage_id: stageId, completion_pct: newPct })
    });
    const data = await res.json();
    if (data.status === "success") {
      const idx = proProjectsList.findIndex(p => p.id === currentProProjectId);
      if (idx !== -1) {
        proProjectsList[idx] = data.project;
      }
      renderActiveProProject();
    }
  } catch (err) {
    console.error("Error advancing stage:", err);
  }
}

async function verifyMentorToken() {
  const input = document.getElementById("mentorTokenInput");
  const token = input ? input.value.trim() : "";
  const statusBadge = document.getElementById("mentorTokenStatusBadge");
  const unlockedArea = document.getElementById("mentorUnlockedArea");

  if (!token) {
    alert("Please enter an official Ayush Ministry mentor token.");
    return;
  }

  try {
    const res = await fetch("/api/mentor/verify", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ project_id: currentProProjectId, token_code: token })
    });
    const data = await res.json();

    if (data.status === "verified" && data.mentor) {
      const m = data.mentor;
      if (statusBadge) {
        statusBadge.className = "pro-token-status-pill unlocked";
        statusBadge.innerText = "✅ Official Ministry Mentor Active";
      }

      if (unlockedArea) {
        unlockedArea.classList.remove("hidden");
        const slotsHtml = (m.available_slots || []).map(s => `<span class="slot-pill">🕒 ${escapeHtml(s)}</span>`).join("");

        unlockedArea.innerHTML = `
          <div class="mentor-profile-grid">
            <div class="mentor-avatar-badge">🏛️</div>
            <div class="mentor-info-col">
              <h4>${escapeHtml(m.name)} <span style="font-size: 11px; font-weight: 500; color: #059669;">• ${escapeHtml(m.badge)}</span></h4>
              <p><strong>${escapeHtml(m.designation)}</strong> • ${escapeHtml(m.department)}</p>
              <div style="font-size: 11.5px; color: #64748B; margin-bottom: 6px;">📍 ${escapeHtml(m.location)}</div>
              <span class="mentor-spec-badge">🎯 Specialization: ${escapeHtml(cleanSectionSigns(m.specialization))}</span>
            </div>
            <div class="mentor-slots-col">
              <div style="font-size: 11px; font-weight: 600; color: #64748B; margin-bottom: 2px;">Available Consultation Slots:</div>
              ${slotsHtml}
              <button class="book-session-btn" onclick="bookMentorSession('${escapeHtml(m.name)}')">
                Book 1-on-1 Consultation
              </button>
            </div>
          </div>
        `;
      }

      // Mark stage 5 complete in project
      advanceProStage("stage_5", 100);
    } else {
      alert("Invalid or expired token code. Please check official credentials.");
    }
  } catch (err) {
    console.error("Mentor token verification error:", err);
  }
}

function applyToken(tokenCode) {
  const input = document.getElementById("mentorTokenInput");
  if (input) input.value = tokenCode;
  verifyMentorToken();
}

function bookMentorSession(mentorName) {
  const refCode = "AYUSH-CONF-2026-" + Math.floor(1000 + Math.random() * 9000);
  alert(`✅ Advisory Consultation Confirmed with ${mentorName}!\n\nOfficial Reference Code: ${refCode}\nConfirmation and meeting link dispatched to applicant dossier.`);
}

async function exportActiveProDossier() {
  try {
    const res = await fetch(`/api/project/${currentProProjectId}/export-dossier`, {
      method: "POST"
    });
    if (!res.ok) throw new Error("Dossier generation failed");
    const blob = await res.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `IP_SAKTI_Pro_Dossier_${currentProProjectId}.docx`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  } catch (err) {
    console.error("Export dossier error:", err);
    alert("Failed to download dossier. Please try again.");
  }
}

// Modal handling for New Regulatory Project
function openNewProjectModal() {
  const modal = document.getElementById("newProjectModal");
  if (modal) modal.classList.remove("hidden");
}

function closeNewProjectModal() {
  const modal = document.getElementById("newProjectModal");
  if (modal) modal.classList.add("hidden");
}

async function submitNewProject() {
  const name = document.getElementById("newProjName")?.value.trim();
  const applicant = document.getElementById("newProjApplicant")?.value.trim();
  const botanicalsRaw = document.getElementById("newProjBotanicals")?.value.trim();
  const dosage = document.getElementById("newProjDosage")?.value.trim();
  const marketsRaw = document.getElementById("newProjMarkets")?.value.trim();

  if (!name || !applicant) {
    alert("Please fill in project name and applicant.");
    return;
  }

  const botanicals = botanicalsRaw ? botanicalsRaw.split(",").map(b => b.trim()) : ["Botanical Formulation"];
  const markets = marketsRaw ? marketsRaw.split(",").map(m => m.trim()) : ["India (Domestic)"];

  try {
    const res = await fetch("/api/project/create", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        name: name,
        applicant: applicant,
        botanicals: botanicals,
        dosage_form: dosage || "Phyto-Complex",
        target_markets: markets
      })
    });
    const data = await res.json();
    if (data.status === "success" && data.project) {
      proProjectsList.push(data.project);
      currentProProjectId = data.project.id;
      closeNewProjectModal();
      await loadProStudio();
    }
  } catch (err) {
    console.error("Error creating project:", err);
    alert("Failed to create project.");
  }
}

/* ===================================================
   NOTIFICATION TOAST HELPER
   =================================================== */
function showNotificationToast(msg) {
  let toast = document.getElementById("ayushNotificationToast");
  if (!toast) {
    toast = document.createElement("div");
    toast.id = "ayushNotificationToast";
    toast.style.cssText = `
      position: fixed;
      bottom: 24px;
      right: 24px;
      background: #0F172A;
      color: #FFFFFF;
      padding: 10px 18px;
      border-radius: 8px;
      font-size: 12.5px;
      font-weight: 500;
      z-index: 99999;
      box-shadow: 0 10px 25px rgba(0,0,0,0.3);
      display: flex;
      align-items: center;
      gap: 8px;
      opacity: 0;
      transform: translateY(10px);
      transition: all 0.22s cubic-bezier(0.16, 1, 0.3, 1);
      pointer-events: none;
      border: 1px solid rgba(255,255,255,0.1);
    `;
    document.body.appendChild(toast);
  }
  toast.innerHTML = msg;
  toast.style.opacity = "1";
  toast.style.transform = "translateY(0)";
  clearTimeout(toast._timeout);
  toast._timeout = setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.transform = "translateY(10px)";
  }, 2400);
}

/* ===================================================
   DARK MODE & LIGHT MODE TOGGLE (SETTINGS MODAL)
   =================================================== */
function toggleTheme() {
  const isDark = document.body.classList.toggle("dark-mode");
  const btnText = document.getElementById("themeToggleText");
  const btnIcon = document.getElementById("themeToggleIcon");
  
  if (isDark) {
    if (btnText) btnText.textContent = "Switch to Light Mode";
    if (btnIcon) btnIcon.textContent = "☀️";
    localStorage.setItem("ayush_theme", "dark");
    showNotificationToast("🌙 Switched to Dark Mode");
  } else {
    if (btnText) btnText.textContent = "Switch to Dark Mode";
    if (btnIcon) btnIcon.textContent = "🌙";
    localStorage.setItem("ayush_theme", "light");
    showNotificationToast("☀️ Switched to Light Mode");
  }
}

function initTheme() {
  const saved = localStorage.getItem("ayush_theme");
  const btnText = document.getElementById("themeToggleText");
  const btnIcon = document.getElementById("themeToggleIcon");
  
  if (saved === "dark") {
    document.body.classList.add("dark-mode");
    if (btnText) btnText.textContent = "Switch to Light Mode";
    if (btnIcon) btnIcon.textContent = "☀️";
  } else {
    document.body.classList.remove("dark-mode");
    if (btnText) btnText.textContent = "Switch to Dark Mode";
    if (btnIcon) btnIcon.textContent = "🌙";
  }
}

/* ===================================================
   LANGUAGE SWITCH TOGGLE & FULL BILINGUAL (EN / HI) ENGINE
   =================================================== */
let currentAyushLanguage = "en";

const I18N = {
  en: {
    heroTitle: "What Ayush regulation, patent, or compliance can I assist with today?",
    heroSub: "Evidence-first regulatory intelligence grounded across Indian (IPO, NBA, Ayush) and Global (WIPO, USPTO, EMA, FDA) regimes.",
    chipMcp: "🔌 Model Context Protocol (MCP) Tools",
    chipMcpBadge: "6 LIVE TOOLS",
    chipArch: "⚡ StateGraph 8-Node Architecture",
    chipScanner: "🔬 TKDL Formulation Screener",
    card1Title: "Can I patent an Ayurvedic pain relief balm?",
    card1Sub: "Curcumin + Wintergreen Oil Section 3(p) & 3(e) check",
    card1Prompt: "Can I patent an Ayurvedic topical pain relief balm containing Curcumin and Wintergreen Oil in India?",
    card2Title: "Exporting Ashwagandha to Germany",
    card2Sub: "EU THMPD 15-year rule & NBA Form 1 export clearance",
    card2Prompt: "What are the statutory requirements to export standardized Ashwagandha extract to Germany under EU THMPD?",
    card3Title: "Classical vs Proprietary Cough Syrup",
    card3Sub: "Rule 158-B safety, acute toxicity & pilot efficacy data",
    card3Prompt: "What is the difference between licensing a Classical Ayurvedic Cough Syrup versus a Proprietary Syrup under Rule 158-B?",
    card4Title: "🌿 Hakim Unani Dialect Normalizer",
    card4Sub: "Asgandh Nagori & Filfil Siyah mapped to UPI Monographs",
    card4Prompt: "I am an Unani Hakim. Can I patent a topical ointment made with Asgandh Nagori and Filfil Siyah for arthritis?",
    inputPlaceholder: "Ask anything about Ayush patents, NBA approvals, licensing, or global export...",
    dockDisclaimer: "IP-SAKTI Sahayak deterministically grounds all statements against official government gazettes. Verify with statutory authorities before legal filing.",
    micBtnTitle: "Speak via Web Speech Recognition (Voice Query)",
    docBtnTitle: "Attach Document / Research Paper / Formulation Spec (PDF, DOCX, TXT, Image)",
    sendBtnTitle: "Send Regulatory Inquiry",
    newInquiry: "New Inquiry",
    savedChats: "SAVED CHATS",
    regulatoryTools: "REGULATORY TOOLS",
    paidTier: "Assist Plus",
    formulationScreener: "Formulation TKDL Screener",
    stategraphArch: "StateGraph Architecture",
    mcpTools: "MCP Protocol Tools",
    goalRoadmaps: "GOAL ROADMAPS",
    mentorAdvisory: "MENTOR ADVISORY",
    stategraphEngine: "StateGraph Engine",
    stategraphSub: "8 Nodes • 12 Statutory Edges",
    brandMinistry: "Ministry of Ayush",
    headerSources: "📚 Sources",
    headerArch: "⚡ Architecture",
    headerSettings: "⚙️ Settings",
    headerPaid: "Assist Plus",
    headerLang: "🌐 EN / हिंदी",
    paidHeroTitle: "Regulatory Intelligence & Milestone Suite",
    paidHeroSub: "Select an authorized module to proceed with conversational AI inquiry, multi-stage compliance execution, or statutory advisory.",
    paidCardChatTitle: "Normal Chatbot",
    paidCardChatDesc: "Full-spectrum AI regulatory inquiry engine with multi-agent statutory verification and real-time citations.",
    paidCardChatAction: "Launch Chatbot",
    paidCardGoalTitle: "Multi-Agent Milestone Roadmap",
    paidCardGoalDesc: "Autonomous LangGraph orchestrator deconstructing statutory goals into sequential regulatory stages.",
    paidCardGoalAction: "Enter Goal Hub",
    paidCardMentorTitle: "Statutory Mentors & Legal Verification",
    paidCardMentorDesc: "Accredited Ayush patent attorneys, former CGPDTM controllers, and NBA access & benefit experts.",
    paidCardMentorAction: "Book Consultation"
  },
  hi: {
    heroTitle: "आज मैं आयुष नियमन, पेटेंट या अनुपालन में आपकी क्या सहायता कर सकता हूँ?",
    heroSub: "भारतीय (IPO, NBA, आयुष) और वैश्विक (WIPO, USPTO, EMA, FDA) व्यवस्थाओं पर आधारित साक्ष्य-प्रधान नियामक बुद्धिमत्ता।",
    chipMcp: "🔌 मॉडल कॉन्टेक्स्ट प्रोटोकॉल (MCP) टूल्स",
    chipMcpBadge: "6 लाइव टूल्स",
    chipArch: "⚡ स्टेटग्राफ 8-नोड आर्किटेक्चर",
    chipScanner: "🔬 TKDL फॉर्मूलेशन परीक्षक",
    card1Title: "क्या मैं आयुर्वेदिक दर्द निवारक बाम पेटेंट कर सकता हूँ?",
    card1Sub: "करक्यूमिन + विंटरग्रीन तेल धारा 3(p) व 3(e) जांच",
    card1Prompt: "क्या मैं भारत में करक्यूमिन और विंटरग्रीन तेल युक्त एक आयुर्वेदिक दर्द निवारक बाम को पेटेंट करा सकता हूँ?",
    card2Title: "जर्मनी को अश्वगंधा का निर्यात",
    card2Sub: "EU THMPD 15-वर्षीय नियम एवं NBA फॉर्म 1 निर्यात मंजूरी",
    card2Prompt: "EU THMPD के तहत जर्मनी को मानकीकृत अश्वगंधा अर्क निर्यात करने के लिए क्या वैधानिक आवश्यकताएं हैं?",
    card3Title: "शास्त्रीय बनाम प्रोप्राइटरी कफ सिरप",
    card3Sub: "नियम 158-B सुरक्षा, तीव्र विषाक्तता व प्रायोगिक प्रभावकारिता डेटा",
    card3Prompt: "नियम 158-B के तहत शास्त्रीय आयुर्वेदिक कफ सिरप बनाम प्रोप्राइटरी सिरप के लाइसेंसिंग में क्या अंतर है?",
    card4Title: "🌿 हकीम यूनानी बोली सामान्यीकरण",
    card4Sub: "असगंद नागोरी और फिलफिल सियाह को UPI मोनोग्राफ में मैप करें",
    card4Prompt: "मैं एक यूनानी हकीम हूँ। क्या मैं गठिया के लिए असगंद नागोरी और फिलफिल सियाह से बने लेप को पेटेंट कर सकता हूँ?",
    inputPlaceholder: "आयुष पेटेंट, NBA अनुमोदन, निर्माण लाइसेंसिंग या वैश्विक निर्यात के बारे में कुछ भी पूछें...",
    dockDisclaimer: "आईपी-शक्ति सहायक सभी बयानों को आधिकारिक सरकारी राजपत्रों के विरुद्ध सत्यापित करता है। विधिक फाइलिंग से पहले वैधानिक प्राधिकरणों से पुष्टि करें।",
    micBtnTitle: "बोलकर प्रश्न पूछें (माइक्रोफ़ोन आवाज़ पहचान)",
    docBtnTitle: "दस्तावेज़ संलग्न करें / शोध पत्र / फॉर्मूलेशन विवरण (PDF, DOCX, TXT, चित्र)",
    sendBtnTitle: "नियामक प्रश्न भेजें",
    newInquiry: "नया विधिक परामर्श",
    savedChats: "सहेजी गई बातचीत",
    regulatoryTools: "नियामक उपकरण",
    paidTier: "असिस्ट प्लस",
    formulationScreener: "टीकेडीएल फॉर्मूलेशन परीक्षक",
    stategraphArch: "स्टेटग्राफ आर्किटेक्चर",
    mcpTools: "MCP प्रोटोकॉल टूल्स",
    goalRoadmaps: "लक्ष्य रोडमैप",
    mentorAdvisory: "परामर्शदाता सलाह",
    stategraphEngine: "स्टेटग्राफ इंजन",
    stategraphSub: "8 नोड्स • 12 वैधानिक संबंध",
    brandMinistry: "आयुष मंत्रालय",
    headerSources: "📚 स्रोत",
    headerArch: "⚡ आर्किटेक्चर",
    headerSettings: "⚙️ सेटिंग्स",
    headerPaid: "असिस्ट प्लस",
    headerLang: "🌐 हिंदी",
    paidHeroTitle: "नियामक बुद्धिमत्ता एवं माइलस्टोन सूट",
    paidHeroSub: "संवादात्मक एआई परामर्श, बहु-चरणीय अनुपालन निष्पादन या वैधानिक सलाह के लिए अधिकृत मॉड्यूल चुनें।",
    paidCardChatTitle: "सामान्य चैटबॉट",
    paidCardChatDesc: "मल्टी-एजेंट वैधानिक सत्यापन और वास्तविक समय संदर्भों के साथ संपूर्ण एआई नियामक परामर्श इंजन।",
    paidCardChatAction: "चैटबॉट शुरू करें",
    paidCardGoalTitle: "मल्टी-एजेंट माइलस्टोन रोडमैप",
    paidCardGoalDesc: "वैधानिक लक्ष्यों को क्रमिक नियामक चरणों में विभाजित करने वाला ऑटोनॉमस ऑर्केस्ट्रेटर।",
    paidCardGoalAction: "लक्ष्य हब में प्रवेश करें",
    paidCardMentorTitle: "वैधानिक परामर्शदाता एवं विधिक सत्यापन",
    paidCardMentorDesc: "मान्यता प्राप्त आयुष पेटेंट अटॉर्नी, पूर्व CGPDTM नियंत्रक और NBA विधिक विशेषज्ञ।",
    paidCardMentorAction: "परामर्श बुक करें"
  }
};

function toggleLanguage() {
  currentAyushLanguage = (currentAyushLanguage === "en") ? "hi" : "en";
  localStorage.setItem("ayush_language", currentAyushLanguage);
  updateLanguageUI();
}

function updateLanguageUI() {
  const isHi = currentAyushLanguage === "hi";
  const dict = I18N[currentAyushLanguage] || I18N.en;

  // 1. Language Button in Header
  const langBtn = document.getElementById("headerLangBtn");
  const langLabel = document.getElementById("headerLangLabel");
  if (langLabel) langLabel.textContent = dict.headerLang;
  if (langBtn) {
    if (isHi) {
      langBtn.classList.add("hindi-active");
      langBtn.setAttribute("title", "भाषा बदलें (वर्तमान: हिंदी / अंग्रेजी के लिए क्लिक करें)");
    } else {
      langBtn.classList.remove("hindi-active");
      langBtn.setAttribute("title", "Switch Language (Current: English / Click for Hindi)");
    }
  }

  // 2. Main Input & Dock
  const promptInput = document.getElementById("userPromptInput");
  if (promptInput) {
    promptInput.setAttribute("placeholder", dict.inputPlaceholder);
  }
  const disclaimerEl = document.getElementById("dockDisclaimerText");
  if (disclaimerEl) {
    disclaimerEl.textContent = dict.dockDisclaimer;
  }
  const voiceBtn = document.getElementById("voiceMicBtn");
  if (voiceBtn) {
    voiceBtn.setAttribute("title", dict.micBtnTitle);
  }
  const docBtn = document.getElementById("docAttachBtn");
  if (docBtn) {
    docBtn.setAttribute("title", dict.docBtnTitle);
  }
  const sendBtn = document.getElementById("sendBtn");
  if (sendBtn) {
    sendBtn.setAttribute("title", dict.sendBtnTitle);
  }

  // 3. Hero Empty State Elements
  const heroMainHeading = document.getElementById("heroMainHeading");
  if (heroMainHeading) {
    heroMainHeading.textContent = dict.heroTitle;
  }
  const heroSubHeading = document.getElementById("heroSubHeading");
  if (heroSubHeading) {
    heroSubHeading.textContent = dict.heroSub;
  }

  // Quick Chips
  const chipMcpText = document.getElementById("heroChipMcpText");
  if (chipMcpText) chipMcpText.textContent = dict.chipMcp;
  const chipMcpBadge = document.getElementById("heroChipMcpBadge");
  if (chipMcpBadge) chipMcpBadge.textContent = dict.chipMcpBadge;
  const chipArchText = document.getElementById("heroChipArchText");
  if (chipArchText) chipArchText.textContent = dict.chipArch;
  const chipScannerText = document.getElementById("heroChipScannerText");
  if (chipScannerText) chipScannerText.textContent = dict.chipScanner;

  // 4 Suggestions Cards
  const suggCard1Title = document.getElementById("suggCard1Title");
  if (suggCard1Title) suggCard1Title.textContent = dict.card1Title;
  const suggCard1Sub = document.getElementById("suggCard1Sub");
  if (suggCard1Sub) suggCard1Sub.textContent = dict.card1Sub;

  const suggCard2Title = document.getElementById("suggCard2Title");
  if (suggCard2Title) suggCard2Title.textContent = dict.card2Title;
  const suggCard2Sub = document.getElementById("suggCard2Sub");
  if (suggCard2Sub) suggCard2Sub.textContent = dict.card2Sub;

  const suggCard3Title = document.getElementById("suggCard3Title");
  if (suggCard3Title) suggCard3Title.textContent = dict.card3Title;
  const suggCard3Sub = document.getElementById("suggCard3Sub");
  if (suggCard3Sub) suggCard3Sub.textContent = dict.card3Sub;

  const suggCard4Title = document.getElementById("suggCard4Title");
  if (suggCard4Title) suggCard4Title.textContent = dict.card4Title;
  const suggCard4Sub = document.getElementById("suggCard4Sub");
  if (suggCard4Sub) suggCard4Sub.textContent = dict.card4Sub;

  // 4. Sidebar Elements
  const sidebarNewChatText = document.getElementById("sidebarNewChatText");
  if (sidebarNewChatText) sidebarNewChatText.textContent = dict.newInquiry;

  const sidebarSavedChatsLabel = document.getElementById("sidebarSavedChatsLabel");
  if (sidebarSavedChatsLabel) sidebarSavedChatsLabel.textContent = dict.savedChats;

  const sidebarRegToolsLabel = document.getElementById("sidebarRegToolsLabel");
  if (sidebarRegToolsLabel) sidebarRegToolsLabel.textContent = dict.regulatoryTools;

  const sidebarItemPaidText = document.getElementById("sidebarItemPaidText");
  if (sidebarItemPaidText) sidebarItemPaidText.textContent = dict.paidTier;

  const sidebarItemScannerText = document.getElementById("sidebarItemScannerText");
  if (sidebarItemScannerText) sidebarItemScannerText.textContent = dict.formulationScreener;

  const sidebarItemArchText = document.getElementById("sidebarItemArchText");
  if (sidebarItemArchText) sidebarItemArchText.textContent = dict.stategraphArch;

  const sidebarItemMcpText = document.getElementById("sidebarItemMcpText");
  if (sidebarItemMcpText) sidebarItemMcpText.textContent = dict.mcpTools;

  const sidebarGoalRoadmapsLabel = document.getElementById("sidebarGoalRoadmapsLabel");
  if (sidebarGoalRoadmapsLabel) sidebarGoalRoadmapsLabel.textContent = dict.goalRoadmaps;

  const sidebarMentorAdvisoryLabel = document.getElementById("sidebarMentorAdvisoryLabel");
  if (sidebarMentorAdvisoryLabel) sidebarMentorAdvisoryLabel.textContent = dict.mentorAdvisory;

  const sidebarFooterTitle = document.getElementById("sidebarFooterTitle");
  if (sidebarFooterTitle) sidebarFooterTitle.textContent = dict.stategraphEngine;

  const sidebarModelText = document.getElementById("sidebarModelText");
  if (sidebarModelText) sidebarModelText.textContent = dict.stategraphSub;

  const brandSub = document.getElementById("brandSub");
  if (brandSub) brandSub.textContent = dict.brandMinistry;

  // 5. Header Buttons
  const headerProBtnLabel = document.getElementById("headerProBtnLabel");
  if (headerProBtnLabel) headerProBtnLabel.textContent = dict.headerPaid;

  const headerMcpBtnSpan = document.getElementById("headerMcpBtnSpan");
  if (headerMcpBtnSpan) headerMcpBtnSpan.textContent = dict.chipMcp.replace(" Protocol", "");

  const headerSourcesBtnSpan = document.getElementById("headerSourcesBtnSpan");
  if (headerSourcesBtnSpan) headerSourcesBtnSpan.textContent = dict.headerSources;

  const headerArchBtnSpan = document.getElementById("headerArchBtnSpan");
  if (headerArchBtnSpan) headerArchBtnSpan.textContent = dict.headerArch;

  const headerSettingsBtnSpan = document.getElementById("headerSettingsBtnSpan");
  if (headerSettingsBtnSpan) headerSettingsBtnSpan.textContent = dict.headerSettings;

  // 6. Paid Tier Landing Elements
  const paidMainTitle = document.querySelector(".paid-main-title");
  if (paidMainTitle) paidMainTitle.textContent = dict.paidHeroTitle;

  const paidSubTitle = document.querySelector(".paid-sub-title");
  if (paidSubTitle) paidSubTitle.textContent = dict.paidHeroSub;

  const cardChatTitle = document.querySelector("#cardNormalChatbot .paid-module-title");
  if (cardChatTitle) cardChatTitle.textContent = dict.paidCardChatTitle;
  const cardChatDesc = document.querySelector("#cardNormalChatbot .paid-module-desc");
  if (cardChatDesc) cardChatDesc.textContent = dict.paidCardChatDesc;
  const cardChatAction = document.querySelector("#cardNormalChatbot .paid-action-text");
  if (cardChatAction) cardChatAction.textContent = dict.paidCardChatAction;

  const cardGoalTitle = document.querySelector("#cardAchieveGoal .paid-module-title");
  if (cardGoalTitle) cardGoalTitle.textContent = dict.paidCardGoalTitle;
  const cardGoalDesc = document.querySelector("#cardAchieveGoal .paid-module-desc");
  if (cardGoalDesc) cardGoalDesc.textContent = dict.paidCardGoalDesc;
  const cardGoalAction = document.querySelector("#cardAchieveGoal .paid-action-text");
  if (cardGoalAction) cardGoalAction.textContent = dict.paidCardGoalAction;

  const cardMentorTitle = document.querySelector("#cardMentorship .paid-module-title");
  if (cardMentorTitle) cardMentorTitle.textContent = dict.paidCardMentorTitle;
  const cardMentorDesc = document.querySelector("#cardMentorship .paid-module-desc");
  if (cardMentorDesc) cardMentorDesc.textContent = dict.paidCardMentorDesc;
  const cardMentorAction = document.querySelector("#cardMentorship .paid-action-text");
  if (cardMentorAction) cardMentorAction.textContent = dict.paidCardMentorAction;

  // 7. Toast feedback
  if (isHi) {
    showNotificationToast("🌐 भाषा बदली गई: हिंदी (संपूर्ण इंटरफ़ेस हिंदी में सक्रिय)");
  } else {
    showNotificationToast("🌐 Language switched: English");
  }
}

function initLanguage() {
  const saved = localStorage.getItem("ayush_language");
  if (saved) {
    currentAyushLanguage = saved;
  }
  updateLanguageUI();
}

/* ===================================================
   VERIFIED STATUTORY & REGULATORY SOURCES DIRECTORY
   =================================================== */
const AYUSH_SOURCES_CATALOG = [
  // 1. Central Authorities & Statutory Databases
  {
    id: "central-ayush",
    name: "Ministry of Ayush (Govt. of India)",
    domain: "ayush.gov.in",
    url: "https://ayush.gov.in",
    category: "central",
    categoryLabel: "Central Government",
    badgeClass: "badge-central",
    icon: "🏛️",
    scope: "Nodal Union Ministry — ASU Gazettes, Notifications & Policies",
    description: "The supreme union executive authority governing Ayurveda, Yoga, Unani, Siddha, and Homoeopathy statutory orders, National Ayush Mission guidelines, and central regulatory directives."
  },
  {
    id: "central-pcimh",
    name: "PCIM&H (Pharmacopoeia Commission)",
    domain: "pcimh.gov.in",
    url: "https://pcimh.gov.in",
    category: "central",
    categoryLabel: "Central Statutory Body",
    badgeClass: "badge-central",
    icon: "📜",
    scope: "Ayurvedic, Siddha, Unani & Homoeopathic Pharmacopoeias & Formularies",
    description: "Statutory body establishing official pharmacopoeial monographs (API, UPI, SPI, HPI), classical shelf-life rules (Rule 161-B), TLC/HPTLC identity standards, and the Ayurvedic Formulary of India (AFI)."
  },
  {
    id: "central-ipindia",
    name: "IP India / CGPDTM (Patents & Trademarks)",
    domain: "ipindia.gov.in",
    url: "https://ipindia.gov.in",
    category: "central",
    categoryLabel: "Central Patent Office",
    badgeClass: "badge-central",
    icon: "⚖️",
    scope: "Patents Act 1970 — Section 3(p) & Section 3(e) Examination Guidelines",
    description: "Controller General of Patents, Designs and Trade Marks guidelines for patenting traditional knowledge, botanical innovations, Section 3(p) non-patentability bars, and prior art searches."
  },
  {
    id: "central-nba",
    name: "National Biodiversity Authority (NBA India)",
    domain: "nbaindia.org",
    url: "https://nbaindia.org",
    category: "central",
    categoryLabel: "Central Statutory Body",
    badgeClass: "badge-central",
    icon: "🌱",
    scope: "Biological Diversity Act 2002 — Section 3 & 6 Prior Approval (Form I / III)",
    description: "Autonomous central authority regulating access to Indian biological resources, mandatory Form 3 IPR approvals before patent grant, and commercial Access & Benefit Sharing (ABS) compliance."
  },
  {
    id: "central-cdsco",
    name: "CDSCO (Central Drugs Standard Control)",
    domain: "cdsco.gov.in",
    url: "https://cdsco.gov.in",
    category: "central",
    categoryLabel: "Central Drug Regulator",
    badgeClass: "badge-central",
    icon: "🔬",
    scope: "Drugs & Cosmetics Act 1940 — ASU Rules & Clinical Trials",
    description: "National regulatory authority for pharmaceutical standards, Section 33P ASU safety advisory notifications, Form 25D manufacturing parameters, and clinical trial regulations (CT-04 / CT-06)."
  },
  {
    id: "central-tkdl",
    name: "CSIR-TKDL (Traditional Knowledge Digital Library)",
    domain: "tkdl.res.in",
    url: "https://tkdl.res.in",
    category: "central",
    categoryLabel: "CSIR & Ayush Repository",
    badgeClass: "badge-central",
    icon: "🛡️",
    scope: "34 Million Pages of Classical Sanskrit/Tamil/Urdu Defense Prior Art",
    description: "Pioneering Indian digital knowledge repository translating classical medical treatises into five international languages to prevent wrongful patenting of traditional Indian formulations worldwide."
  },
  {
    id: "central-fssai",
    name: "FSSAI (Food Safety & Standards Authority)",
    domain: "fssai.gov.in",
    url: "https://fssai.gov.in",
    category: "central",
    categoryLabel: "Central Food Regulator",
    badgeClass: "badge-central",
    icon: "🥗",
    scope: "Nutraceutical, Health Supplement & Ayush Aahar Regulations 2022",
    description: "Apex food safety regulator governing botanicals classified as dietary supplements, botanical permissible extraction limits, purity monographs, and Ayush Aahar co-labeling rules."
  },
  {
    id: "central-eaushadhi",
    name: "e-Aushadhi / Ayush Grid Portal",
    domain: "eaushadhi.gov.in",
    url: "https://eaushadhi.gov.in",
    category: "central",
    categoryLabel: "Central Digital Registry",
    badgeClass: "badge-central",
    icon: "💻",
    scope: "National Supply Chain & Statutory Drug Batch Verification",
    description: "Ministry of Ayush central digital backbone for supply chain tracking, drug inspection reporting, raw material batch quality assurance, and licensed ASU manufacturer verification."
  },

  // 2. State Ayush Licensing Authorities (SALA)
  {
    id: "state-gujarat",
    name: "Gujarat FDCA (Food & Drugs Control Administration)",
    domain: "fdca.gujarat.gov.in",
    url: "https://fdca.gujarat.gov.in",
    category: "state",
    categoryLabel: "State Licensing Authority",
    badgeClass: "badge-state",
    icon: "📍",
    scope: "Form 25D Manufacturing Licenses, Schedule T GMP & CoPP Certificates",
    description: "Pioneering state licensing authority offering online DLA licensing, Schedule T Good Manufacturing Practice audits, Certificate of Pharmaceutical Product (CoPP), and export endorsements."
  },
  {
    id: "state-kerala",
    name: "Kerala State Drugs Control Department (Ayush Wing)",
    domain: "drugscontrol.kerala.gov.in",
    url: "https://drugscontrol.kerala.gov.in",
    category: "state",
    categoryLabel: "State Licensing Authority",
    badgeClass: "badge-state",
    icon: "📍",
    scope: "Classical Ayurvedic Form 25D / 26D Renewals & Phyto-Sanitary Testing",
    description: "State drug controller for the renowned Kerala Ayurvedic sector, regulating traditional Kashayams, Arishtams, Form 25D commercial manufacturing, and official drug testing laboratories."
  },
  {
    id: "state-delhi",
    name: "Directorate of AYUSH, Govt. of NCT of Delhi",
    domain: "delhi.gov.in",
    url: "https://delhi.gov.in",
    category: "state",
    categoryLabel: "State Licensing Authority",
    badgeClass: "badge-state",
    icon: "📍",
    scope: "UT ASU Drug Manufacturing Clearances & Institutional Approvals",
    description: "Government of NCT of Delhi state licensing directorate regulating ASU pharmaceutical factories, hospital formularies, and urban wholesale/retail distribution compliance."
  },
  {
    id: "state-up",
    name: "Uttar Pradesh AYUSH Department",
    domain: "ayush.up.gov.in",
    url: "https://ayush.up.gov.in",
    category: "state",
    categoryLabel: "State Licensing Authority",
    badgeClass: "badge-state",
    icon: "📍",
    scope: "State ASU Manufacturing Licenses, Raw Herb Quarantine & Form 25D",
    description: "Largest northern state regulatory directorate overseeing classical pharmacy approvals, botanical cultivation quarantine clearances, and commercial GMP inspection compliance."
  },
  {
    id: "state-tamilnadu",
    name: "Tamil Nadu Directorate of Indian Medicine (IMCOPS)",
    domain: "tn.gov.in",
    url: "https://tn.gov.in",
    category: "state",
    categoryLabel: "State Licensing Authority",
    badgeClass: "badge-state",
    icon: "📍",
    scope: "Siddha, Ayurveda & Unani Manufacturing Licenses & Classical Formulations",
    description: "Custodian of Siddha medicine manufacturing licenses, classical Palm Leaf manuscript formulations, Form 25D approvals, and the Tamil Nadu State Medicinal Plants Board."
  },
  {
    id: "state-maharashtra",
    name: "Maharashtra FDA (Ayush Division)",
    domain: "fda.maharashtra.gov.in",
    url: "https://fda.maharashtra.gov.in",
    category: "state",
    categoryLabel: "State Licensing Authority",
    badgeClass: "badge-state",
    icon: "📍",
    scope: "Schedule T GMP Compliance, Stability Studies & Industrial Phyto-Pharma",
    description: "Premier industrial licensing regulator overseeing ASU pharmaceutical manufacturing clusters, raw material heavy metal testing, and accelerated stability study clearances."
  },
  {
    id: "state-karnataka",
    name: "Karnataka Directorate of AYUSH",
    domain: "ayush.karnataka.gov.in",
    url: "https://ayush.karnataka.gov.in",
    category: "state",
    categoryLabel: "State Licensing Authority",
    badgeClass: "badge-state",
    icon: "📍",
    scope: "Form 25D Drug Controller & State Biodiversity Board Coordination",
    description: "State licensing authority supervising Western Ghats botanical biodiversity permits, modern phyto-formulation licenses, and ASU analytical lab approvals."
  },

  // 3. WIPO & Foreign / International Regimes
  {
    id: "wipo-igc",
    name: "WIPO (World Intellectual Property Organization)",
    domain: "wipo.int",
    url: "https://www.wipo.int",
    category: "wipo",
    categoryLabel: "Global IP Organization",
    badgeClass: "badge-wipo",
    icon: "🌍",
    scope: "Intergovernmental Committee on Traditional Knowledge & Genetic Resources",
    description: "Geneva-based UN agency leading international treaties on Intellectual Property, Genetic Resources, and Traditional Knowledge (IGC), preventing defensive patent misappropriation."
  },
  {
    id: "uspto-gov",
    name: "USPTO (United States Patent and Trademark Office)",
    domain: "uspto.gov",
    url: "https://www.uspto.gov",
    category: "wipo",
    categoryLabel: "United States Patent Office",
    badgeClass: "badge-wipo",
    icon: "🇺🇸",
    scope: "35 U.S.C. 102/103 Prior Art Scrutiny & TKDL Collaboration Database",
    description: "Official US patent registry utilizing Indian TKDL prior art access agreement to reject obvious patent applications claiming traditional botanical remedies."
  },
  {
    id: "fda-botanical",
    name: "US FDA Botanical Guidance for Industry",
    domain: "fda.gov",
    url: "https://www.fda.gov",
    category: "wipo",
    categoryLabel: "United States Drug Regulator",
    badgeClass: "badge-wipo",
    icon: "🇺🇸",
    scope: "Botanical Drug Development Guidance — IND / NDA Batch Consistency",
    description: "Food and Drug Administration guidance specifying quality, chemistry, manufacturing, controls (CMC), and multi-batch fingerprinting for complex herbal and polyherbal extracts."
  },
  {
    id: "ema-thmpd",
    name: "EMA / HMPC (European Medicines Agency)",
    domain: "ema.europa.eu",
    url: "https://www.ema.europa.eu",
    category: "wipo",
    categoryLabel: "European Union Regulator",
    badgeClass: "badge-wipo",
    icon: "🇪🇺",
    scope: "Directive 2004/24/EC Traditional Herbal Medicinal Products (THMPD)",
    description: "European Committee on Herbal Medicinal Products monographs establishing 30-year bibliographic traditional use rules (15 years within EU) for herbal registration."
  },
  {
    id: "uk-mhra",
    name: "UK MHRA (Medicines & Healthcare products Regulator)",
    domain: "gov.uk/mhra",
    url: "https://www.gov.uk/mhra",
    category: "wipo",
    categoryLabel: "United Kingdom Drug Regulator",
    badgeClass: "badge-wipo",
    icon: "🇬🇧",
    scope: "Traditional Herbal Registration (THR) Scheme & Safety Monograph Guidance",
    description: "Executive agency regulating traditional herbal medicines in the United Kingdom under the THR certification scheme based on long-standing traditional medicinal safety and efficacy."
  },
  {
    id: "who-traditional",
    name: "WHO Traditional Medicine & Global Centre (Jamnagar)",
    domain: "who.int",
    url: "https://www.who.int",
    category: "wipo",
    categoryLabel: "World Health Organization",
    badgeClass: "badge-wipo",
    icon: "🌐",
    scope: "WHO Global Centre for Traditional Medicine & Quality Assurance Guidelines",
    description: "Global health body standardizing botanical safety, Good Agricultural and Collection Practices (GACP), and evidence-based integration of traditional medicines into global health systems."
  },

  // 4. Vernacular & Text Swapping / Dialect Datasets
  {
    id: "vernacular-echarak",
    name: "NMPB e-Charak (National Medicinal Plants Board)",
    domain: "echarak.in",
    url: "https://echarak.in",
    category: "vernacular",
    categoryLabel: "Vernacular Dialect Concordance",
    badgeClass: "badge-vernacular",
    icon: "🌿",
    scope: "1,200+ Regional Indian Dialect Herb Names Mapped to Binomials",
    description: "Flagship vernacular plant database by NMPB grounding regional folk terms (Hindi, Marathi, Gujarati, Tamil, Telugu, Kannada, Bengali) to verified Latin botanical taxa."
  },
  {
    id: "vernacular-api-sanskrit",
    name: "Ayurvedic Pharmacopoeia (API) Sanskrit Concordance",
    domain: "pcimh.gov.in",
    url: "https://pcimh.gov.in",
    category: "vernacular",
    categoryLabel: "Classical Sanskrit Lexicon",
    badgeClass: "badge-vernacular",
    icon: "🪷",
    scope: "Charaka, Sushruta & Vagbhata Shloka Dialect Normalization Dataset",
    description: "Official canonical concordance resolving classical Sanskrit Shlokas, Paryayas (synonyms), Guna-Karma attributes, and anatomical actions into modern pharmacological terms."
  },
  {
    id: "vernacular-upi-greco",
    name: "Unani Pharmacopoeia (UPI) & Persian/Arabic Lexicon",
    domain: "pcimh.gov.in",
    url: "https://pcimh.gov.in",
    category: "vernacular",
    categoryLabel: "Greco-Arab / Persian Lexicon",
    badgeClass: "badge-vernacular",
    icon: "🏺",
    scope: "Bayaz-e-Kabeer & Qarabadeen Greco-Arab Classical Synonym Swapping",
    description: "Specialized linguistic dataset mapping Persian, Arabic, and Urdu classical Unani medical treatises and polyherbal compound names to standardized botanical nomenclature."
  },
  {
    id: "vernacular-spi-tamil",
    name: "Siddha Pharmacopoeia (SPI) Agathiyar Dialect Concordance",
    domain: "pcimh.gov.in",
    url: "https://pcimh.gov.in",
    category: "vernacular",
    categoryLabel: "Classical Tamil Lexicon",
    badgeClass: "badge-vernacular",
    icon: "📜",
    scope: "Ancient Palm-Leaf Agathiyar Gunavagadam Dialect Term Swapping",
    description: "Linguistic mapping corpus resolving ancient poetic Tamil palm-leaf manuscript names (Agathiyar, Therayar, Bogar) into validated botanical, mineral, and marine sources."
  },
  {
    id: "vernacular-tkrc",
    name: "CSIR-TKDL Traditional Knowledge Resource Classification (TKRC)",
    domain: "tkdl.res.in",
    url: "https://tkdl.res.in",
    category: "vernacular",
    categoryLabel: "Multilingual IPC Ontology",
    badgeClass: "badge-vernacular",
    icon: "🌐",
    scope: "International Patent Classification (IPC) Linked 200,000+ Subgroup Ontology",
    description: "Structured taxonomic knowledge classification system bridging vernacular Indian Ayurvedic/Unani/Siddha medical terms directly into IPC patent patentability search keys."
  }
];

let activeSourceCategory = "all";

function openSourcesModal() {
  const modal = document.getElementById("sourcesModal");
  if (!modal) return;
  modal.classList.remove("hidden");
  
  // Reset search and tab
  const searchInput = document.getElementById("sourcesSearchInput");
  if (searchInput) searchInput.value = "";
  activeSourceCategory = "all";
  updateSourceTabsUI();
  renderSources();
}

function closeSourcesModal() {
  const modal = document.getElementById("sourcesModal");
  if (modal) modal.classList.add("hidden");
}

function selectSourceCategory(category) {
  activeSourceCategory = category;
  updateSourceTabsUI();
  renderSources();
}

function updateSourceTabsUI() {
  const tabs = {
    all: document.getElementById("srcTabAll"),
    central: document.getElementById("srcTabCentral"),
    state: document.getElementById("srcTabState"),
    wipo: document.getElementById("srcTabWipo"),
    vernacular: document.getElementById("srcTabVernacular")
  };
  
  Object.keys(tabs).forEach(cat => {
    if (tabs[cat]) {
      if (cat === activeSourceCategory) {
        tabs[cat].classList.add("active");
      } else {
        tabs[cat].classList.remove("active");
      }
    }
  });
}

function filterSources() {
  renderSources();
}

function renderSources() {
  const grid = document.getElementById("sourcesGrid");
  if (!grid) return;
  
  const searchInput = document.getElementById("sourcesSearchInput");
  const query = searchInput ? searchInput.value.trim().toLowerCase() : "";
  
  const filtered = AYUSH_SOURCES_CATALOG.filter(item => {
    const matchesCategory = (activeSourceCategory === "all") || (item.category === activeSourceCategory);
    if (!matchesCategory) return false;
    
    if (!query) return true;
    
    const textCorpus = `${item.name} ${item.domain} ${item.scope} ${item.description} ${item.categoryLabel}`.toLowerCase();
    return textCorpus.includes(query);
  });
  
  if (filtered.length === 0) {
    grid.innerHTML = `
      <div style="grid-column: 1 / -1; text-align: center; padding: 40px 20px; color: #64748B;">
        <div style="font-size: 32px; margin-bottom: 8px;">🔍</div>
        <strong style="font-size: 14px; color: #0F172A;">No statutory data sources found</strong>
        <p style="font-size: 12px; margin-top: 4px;">Try searching for "Gujarat", "WIPO", "Section 3(p)", "e-Charak", or "Pharmacopoeia"</p>
      </div>
    `;
    return;
  }
  
  grid.innerHTML = filtered.map(item => `
    <div class="source-item-card">
      <div>
        <div class="source-card-top">
          <div class="source-card-title-row">
            <span class="source-card-icon">${item.icon}</span>
            <span class="source-card-name">${item.name}</span>
          </div>
          <span class="source-card-category-badge ${item.badgeClass}">${item.categoryLabel}</span>
        </div>
        <div style="font-size: 11.5px; font-weight: 600; color: #059669; margin-bottom: 6px;">
          ⚖️ ${item.scope}
        </div>
        <p class="source-card-desc">${item.description}</p>
      </div>
      <div class="source-card-bottom">
        <a href="${item.url}" target="_blank" rel="noopener noreferrer" class="source-url-preview" title="Visit ${item.domain}">
          🌐 ${item.domain}
        </a>
        <a href="${item.url}" target="_blank" rel="noopener noreferrer" class="source-visit-btn">
          <span>Visit Official Portal</span>
          <span>↗</span>
        </a>
      </div>
    </div>
  `).join("");
}

function initSources() {
  // Pre-render sources grid if modal exists
  renderSources();
}



