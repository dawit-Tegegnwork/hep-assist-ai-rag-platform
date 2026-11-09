/* Side workspace for MediMind, opened from the right edge of a Bahmni chart. WAVE_B_AUTOLOAD */
(function () {
  if (window.__medimindSideLoaded) return;
  window.__medimindSideLoaded = true;
  var API = "/openmrs/ws/rest/v1/medimind";
  var UUID_RE = /patient\/([0-9a-fA-F-]{36})/;
  var pollTimer = null;
  var startedAt = 0;
  var currentUuid = "";

  function patientUuid() {
    var match = (location.hash || "").match(UUID_RE);
    return match ? match[1] : "";
  }

  function el(tag, className, text) {
    var node = document.createElement(tag);
    if (className) node.className = className;
    if (text) node.textContent = text;
    return node;
  }

  function sparkSvg(points) {
    var vals = points || [12, 18, 14, 22, 19, 28, 24, 30];
    var max = Math.max.apply(null, vals) || 1;
    var w = 160;
    var h = 36;
    var step = w / Math.max(1, vals.length - 1);
    var d = vals.map(function (v, i) {
      var x = (i * step).toFixed(1);
      var y = (h - (v / max) * (h - 4) - 2).toFixed(1);
      return (i ? "L" : "M") + x + " " + y;
    }).join(" ");
    return '<svg class="mm-spark" viewBox="0 0 ' + w + ' ' + h + '" preserveAspectRatio="none"><path d="' + d + '" fill="none" stroke="rgba(255,255,255,0.95)" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg>';
  }

  function vitalTile(key, label) {
    var tile = el("div", "mm-vital");
    tile.dataset.key = key;
    var title = el("span", "mm-vital-label", label);
    var val = el("span", "mm-vital-val", "—");
    var note = el("span", "mm-vital-note", "");
    tile.appendChild(title);
    tile.appendChild(val);
    tile.appendChild(note);
    tile._label = title;
    tile._val = val;
    tile._note = note;
    return tile;
  }

  function buildEmrShell() {
    var wrap = el("div", "medimind-side-body mm-emr-host");
    var root = el("div", "mm-copilot");

    var patientCard = el("div", "mm-card mm-patient-card");
    var top = el("div", "mm-patient-top");
    var left = el("div", "mm-patient-left");
    var patientName = el("div", "mm-patient-name", "Open a patient");
    var patientMeta = el("div", "mm-patient-meta", "Select a chart to begin");
    var patientId = el("span", "mm-patient-id", "");
    patientId.hidden = true;
    left.appendChild(patientName);
    left.appendChild(patientMeta);
    var deptTag = el("span", "mm-tag mm-visit-pill", "");
    deptTag.hidden = true;
    top.appendChild(left);
    top.appendChild(deptTag);
    patientCard.appendChild(top);
    var adm = el("span", "mm-adm", "");
    adm.hidden = true;

    var urgency = el("div", "mm-urgency");
    var urgRoutine = el("button", null, "Routine");
    var urgUrgent = el("button", null, "Urgent");
    var urgEmergency = el("button", null, "Emergency");
    [urgRoutine, urgUrgent, urgEmergency].forEach(function (btn) { btn.type = "button"; });
    urgency.appendChild(urgRoutine);
    urgency.appendChild(urgUrgent);
    urgency.appendChild(urgEmergency);
    patientCard.appendChild(urgency);

    var vitalsCard = el("div", "mm-vitals-card");
    var vitalsHead = el("div", "mm-vitals-head");
    vitalsHead.appendChild(el("span", "mm-vitals-title", "VITALS"));
    var vitalsStatus = el("span", "mm-vitals-status");
    var vitalsDot = el("span", "mm-vitals-dot");
    var vitalsStatusText = el("span", null, "No vitals");
    vitalsStatus.appendChild(vitalsDot);
    vitalsStatus.appendChild(vitalsStatusText);
    vitalsHead.appendChild(vitalsStatus);
    var vitals = el("div", "mm-vitals");
    var vitalBp = vitalTile("bp", "BP");
    var vitalHr = vitalTile("hr", "HR");
    var vitalSpo2 = vitalTile("spo2", "SpO₂");
    var vitalPlatelet = vitalTile("temp", "Temp");
    vitals.appendChild(vitalBp);
    vitals.appendChild(vitalHr);
    vitals.appendChild(vitalSpo2);
    vitals.appendChild(vitalPlatelet);
    vitalsCard.appendChild(vitalsHead);
    vitalsCard.appendChild(vitals);

    var assessCard = el("div", "mm-card mm-assess-card");
    var assessH = el("div", "mm-assess-h");
    assessH.appendChild(el("span", null, "Clinical Summary"));
    var assessBody = el("div", "mm-assess-body");
    var summaryText = el("div", "mm-assess-text", "Open a patient to load the chart summary.");
    var labChips = el("div", "mm-lab-chips");
    assessBody.appendChild(summaryText);
    assessBody.appendChild(labChips);
    assessCard.appendChild(assessH);
    assessCard.appendChild(assessBody);

    var boardTabs = el("div", "mm-board-tabs mm-board-tabs-5");
    var tabDx = el("button", "active", "Diagnoses");
    var tabMed = el("button", null, "Meds");
    var tabTime = el("button", null, "Timeline");
    var tabHist = el("button", null, "History");
    var tabChat = el("button", null, "Chat");
    [tabDx, tabMed, tabTime, tabHist, tabChat].forEach(function (btn) { btn.type = "button"; });
    boardTabs.appendChild(tabDx);
    boardTabs.appendChild(tabMed);
    boardTabs.appendChild(tabTime);
    boardTabs.appendChild(tabHist);
    boardTabs.appendChild(tabChat);

    var boardCard = el("div", "mm-card");
    var dxPanel = el("div", "mm-board-panel");
    var medPanel = el("div", "mm-board-panel");
    var timePanel = el("div", "mm-board-panel");
    var histPanel = el("div", "mm-board-panel");
    var chatPanel = el("div", "mm-board-panel");
    medPanel.hidden = true;
    timePanel.hidden = true;
    histPanel.hidden = true;
    chatPanel.hidden = true;
    dxPanel.appendChild(el("p", "mm-lab-empty", "No diagnosis in this window."));
    medPanel.appendChild(el("p", "mm-lab-empty", "No medicine in this window."));
    timePanel.appendChild(el("p", "mm-lab-empty", "No dated events in this window."));
    histPanel.appendChild(el("p", "mm-lab-empty", "No medical/surgical history in this window."));
    var chatLog = el("div", "mm-chat-log");
    chatLog.appendChild(el("p", "mm-lab-empty", "Ask ClinicDx about this chart. Draft only — not saved to Bahmni."));
    var chatForm = el("div", "mm-chat-form");
    var chatInput = el("textarea", "mm-chat-input");
    chatInput.rows = 2;
    chatInput.placeholder = "e.g. What labs should I repeat?";
    var chatSend = el("button", "mm-footer-primary", "Ask ClinicDx");
    chatSend.type = "button";
    chatForm.appendChild(chatInput);
    chatForm.appendChild(chatSend);
    chatPanel.appendChild(chatLog);
    chatPanel.appendChild(chatForm);
    boardCard.appendChild(dxPanel);
    boardCard.appendChild(medPanel);
    boardCard.appendChild(timePanel);
    boardCard.appendChild(histPanel);
    boardCard.appendChild(chatPanel);

    var protocol = el("div", "mm-protocol");
    protocol.hidden = true;

    var footer = el("div", "mm-footer");
    var noteBtn = el("button", "mm-footer-primary", "+ Add Clinical Note");
    noteBtn.type = "button";
    var ackBtn = el("button", "mm-footer-secondary", "Acknowledge Protocol");
    ackBtn.type = "button";
    var openBtn = el("button", "mm-footer-icon", "↗");
    openBtn.type = "button";
    openBtn.title = "Open Assess tab";
    footer.appendChild(noteBtn);
    footer.appendChild(ackBtn);
    footer.appendChild(openBtn);

    root.appendChild(patientCard);
    root.appendChild(vitalsCard);
    root.appendChild(assessCard);
    root.appendChild(boardTabs);
    root.appendChild(boardCard);
    root.appendChild(protocol);
    wrap.appendChild(root);

    function showBoard(which) {
      dxPanel.hidden = which !== "dx";
      medPanel.hidden = which !== "med";
      timePanel.hidden = which !== "time";
      histPanel.hidden = which !== "hist";
      chatPanel.hidden = which !== "chat";
      tabDx.classList.toggle("active", which === "dx");
      tabMed.classList.toggle("active", which === "med");
      tabTime.classList.toggle("active", which === "time");
      tabHist.classList.toggle("active", which === "hist");
      tabChat.classList.toggle("active", which === "chat");
    }
    tabDx.addEventListener("click", function () { showBoard("dx"); });
    tabMed.addEventListener("click", function () { showBoard("med"); });
    tabTime.addEventListener("click", function () { showBoard("time"); });
    tabHist.addEventListener("click", function () { showBoard("hist"); });
    tabChat.addEventListener("click", function () { showBoard("chat"); });

    return {
      root: wrap,
      patientName: patientName,
      patientId: patientId,
      patientMeta: patientMeta,
      deptTag: deptTag,
      adm: adm,
      urgRoutine: urgRoutine,
      urgUrgent: urgUrgent,
      urgEmergency: urgEmergency,
      vitalBp: vitalBp,
      vitalHr: vitalHr,
      vitalSpo2: vitalSpo2,
      vitalPlatelet: vitalPlatelet,
      vitalsStatus: vitalsStatus,
      vitalsStatusText: vitalsStatusText,
      summaryText: summaryText,
      labChips: labChips,
      dxPanel: dxPanel,
      medPanel: medPanel,
      timePanel: timePanel,
      histPanel: histPanel,
      chatPanel: chatPanel,
      chatLog: chatLog,
      chatInput: chatInput,
      chatSend: chatSend,
      tabDx: tabDx,
      tabMed: tabMed,
      tabTime: tabTime,
      tabHist: tabHist,
      tabChat: tabChat,
      protocol: protocol,
      footer: footer,
      noteBtn: noteBtn,
      ackBtn: ackBtn,
      openBtn: openBtn,
      showBoard: showBoard,
      lastDifferentials: [],
      lastActions: [],
      lastKeyPoints: [],
      lastAssessMode: ""
    };
  }

  function linesFromSection(text) {
    return String(text || "")
      .split(/\n+/)
      .map(function (line) {
        return line.replace(/^\s*(?:[-*]|\d+[.)])\s*/, "").replace(/\*\*/g, "").trim();
      })
      .filter(function (line) {
        if (!line) return false;
        var low = line.toLowerCase();
        return low !== "none" && low !== "none." && low.indexOf("none identified") === -1;
      })
      .slice(0, 6);
  }

  /** Plain clinical text for the draft box — no Markdown ## / ** noise. */
  function formatDraftForDisplay(text) {
    var out = String(text || "");
    out = out.replace(/\r\n/g, "\n");
    out = out.replace(/^\s{0,3}#{1,6}\s*/gm, "");
    out = out.replace(/\*\*([^*]+)\*\*/g, "$1");
    out = out.replace(/__([^_]+)__/g, "$1");
    out = out.replace(/`([^`]+)`/g, "$1");
    out = out.replace(/^\s*[-*]\s+/gm, "• ");
    out = out.replace(/\n{3,}/g, "\n\n");
    return out.trim();
  }

  function plainOneLine(text) {
    return formatDraftForDisplay(text).replace(/\s+/g, " ").trim();
  }

  function escapeHtml(text) {
    return String(text || "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function inlineMdHtml(text) {
    var out = escapeHtml(text);
    out = out.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
    out = out.replace(/__([^_]+)__/g, "<strong>$1</strong>");
    out = out.replace(/`([^`]+)`/g, "<code>$1</code>");
    return out;
  }

  /** Render ClinicDx chat/safety markdown as real bold + bullets (no raw ** / ##). */
  function renderClinicalMarkdown(node, text) {
    if (!node) return;
    var raw = String(text || "").replace(/\r\n/g, "\n");
    raw = raw.replace(/^\s{0,3}#{1,6}\s*/gm, "");
    raw = raw.replace(/\n{3,}/g, "\n\n").trim();
    node.innerHTML = "";
    if (!raw) {
      node.textContent = "";
      return;
    }
    raw.split(/\n{2,}/).forEach(function (block) {
      var lines = block.split("\n").map(function (ln) { return ln.trim(); }).filter(Boolean);
      if (!lines.length) return;
      var listish = lines.every(function (ln) {
        return /^([-*•]|\d+[.)])\s+/.test(ln);
      });
      if (listish) {
        var ul = document.createElement("ul");
        ul.className = "mm-md-list";
        lines.forEach(function (ln) {
          var li = document.createElement("li");
          li.innerHTML = inlineMdHtml(ln.replace(/^([-*•]|\d+[.)])\s+/, ""));
          ul.appendChild(li);
        });
        node.appendChild(ul);
        return;
      }
      var p = document.createElement("p");
      p.className = "mm-md-p";
      p.innerHTML = lines.map(inlineMdHtml).join("<br>");
      node.appendChild(p);
    });
  }

  function renderDxSuggestions(emr) {
    if (!emr || !emr.dxPanel) return;
    emr.dxPanel.querySelectorAll(".mm-suggest-block").forEach(function (node) { node.remove(); });

    var diffs = emr.lastDifferentials || [];
    var actions = emr.lastActions || [];
    var points = emr.lastKeyPoints || [];
    var thin = emr.lastAssessMode === "thin-chart";
    var suggestCount = diffs.length + actions.length;

    if (emr.tabDx) {
      var coded = (emr.dxPanel.querySelectorAll(".mm-dx") || []).length;
      emr.tabDx.textContent = suggestCount
        ? ("Diagnoses (" + coded + ") · " + suggestCount + " AI")
        : ("Diagnoses (" + coded + ")");
    }

    if (!diffs.length && !actions.length && !thin) {
      var waiting = el("div", "mm-suggest-block");
      waiting.appendChild(el("div", "mm-kicker", "ClinicDx suggestions"));
      waiting.appendChild(el("p", "mm-lab-empty", "Waiting for ClinicDx draft… Possible diagnoses, questions to ask, and tests to order will appear here."));
      emr.dxPanel.appendChild(waiting);
      return;
    }

    var block = el("div", "mm-suggest-block");
    block.appendChild(el("div", "mm-kicker", "ClinicDx suggestions (draft only)"));

    if (thin) {
      var thinCard = el("div", "mm-suggest mm-suggest-thin");
      thinCard.appendChild(el("strong", null, "Not enough coded facts yet"));
      thinCard.appendChild(el("div", "mm-med-meta", "Ask / document chief complaint, key exam findings, and current meds — then Draft again."));
      block.appendChild(thinCard);
    }

    if (diffs.length) {
      block.appendChild(el("div", "mm-suggest-sub", "Possible diagnoses to consider"));
      diffs.forEach(function (item, idx) {
        var card = el("div", "mm-suggest");
        var head = el("div", "mm-dx-head");
        head.appendChild(el("strong", null, item));
        head.appendChild(el("span", "mm-badge mm-badge-warm", "Suggest " + (idx + 1)));
        card.appendChild(head);
        block.appendChild(card);
      });
    } else if (!thin) {
      block.appendChild(el("p", "mm-lab-empty", "No differential list in this draft. Use Chat to ask “what else should I consider?”"));
    }

    if (actions.length) {
      block.appendChild(el("div", "mm-suggest-sub", "Ask next · tests / actions"));
      var list = el("ul", "mm-diff-list mm-ask-list");
      actions.forEach(function (item) {
        list.appendChild(el("li", null, item));
      });
      block.appendChild(list);
    }

    if (points.length) {
      block.appendChild(el("div", "mm-suggest-sub", "Key points"));
      var kp = el("ul", "mm-diff-list");
      points.forEach(function (item) {
        kp.appendChild(el("li", null, item));
      });
      block.appendChild(kp);
    }

    emr.dxPanel.appendChild(block);
  }

  function build() {
    if (document.getElementById("medimind-side")) return;

    var root = el("div", "medimind-side");
    root.id = "medimind-side";

    var tab = el("button", "medimind-side-tab", "MediMind");
    tab.type = "button";
    tab.title = "Open MediMind doctor view";

    var panel = el("aside", "medimind-side-panel");
    panel.setAttribute("hidden", "hidden");

    var head = el("div", "medimind-side-head");
    head.style.position = "relative";
    var brand = el("div", "medimind-side-brand");
    brand.appendChild(el("div", "medimind-side-logo", "MM"));
    var brandText = el("div", "medimind-side-brand-text");
    brandText.appendChild(el("strong", null, "MediMind Copilot"));
    brandText.appendChild(el("small", null, "Bahmni Clinical Intelligence"));
    brand.appendChild(brandText);
    var status = el("span", "medimind-side-status preparing", "● Syncing");
    var alertBell = el("button", "mm-alert-bell", "🔔");
    alertBell.type = "button";
    alertBell.title = "Context-aware risk flagging";
    alertBell.dataset.count = "0";
    var refresh = el("button", "medimind-side-btn", "↻");
    refresh.type = "button";
    refresh.title = "Refresh";
    var close = el("button", "medimind-side-btn", "✕");
    close.type = "button";
    close.title = "Close";
    head.appendChild(brand);
    head.appendChild(status);
    head.appendChild(alertBell);
    head.appendChild(refresh);
    head.appendChild(close);

    var alertPop = el("div", "mm-alert-pop");
    alertPop.appendChild(el("div", "mm-card-h", "Point-of-care alerts"));
    var alertPopBody = el("div", "mm-card-b");
    alertPopBody.appendChild(el("p", "mm-lab-empty", "No safety alert."));
    alertPop.appendChild(alertPopBody);
    head.appendChild(alertPop);

    var who = el("div", "medimind-side-who");
    var whoName = el("div", "medimind-side-who-name", "Open a patient");
    var whoId = el("div", "medimind-side-who-id", "");
    who.appendChild(whoName);
    who.appendChild(whoId);

    var message = el("p", "medimind-side-message");
    var tabs = el("div", "mm-legacy-tabs");
    var emrTab = el("button", "active", "Copilot");
    var summaryTab = el("button", null, "Summary");
    var safetyTab = el("button", null, "Safety");
    var noteTab = el("button", null, "Note");
    var assessTab = el("button", null, "Assess");
    [emrTab, summaryTab, safetyTab, noteTab, assessTab].forEach(function (btn) { btn.type = "button"; });
    tabs.appendChild(emrTab);
    tabs.appendChild(summaryTab);
    tabs.appendChild(safetyTab);
    tabs.appendChild(noteTab);
    tabs.appendChild(assessTab);

    var emr = buildEmrShell();
    var summary = el("div", "medimind-side-body");
    var safety = el("div", "medimind-side-body");
    var note = el("div", "medimind-side-body");
    var assess = el("div", "medimind-side-body");
    summary.hidden = true;
    safety.hidden = true;
    note.hidden = true;
    assess.hidden = true;
    var assessBtn = el("button", "medimind-record", "Draft assessment");
    assessBtn.type = "button";
    var assessStatus = el("p", "medimind-transcript", "MediMind drafts Assessment, Differentials, Plan, and Safety from this chart only. Review, then press Bahmni Save yourself.");
    var assessBox = el("textarea");
    assessBox.dataset.field = "assessment";
    assessBox.rows = 12;
    assess.appendChild(assessBtn);
    assess.appendChild(assessStatus);
    assess.appendChild(assessBox);
    assessBtn.addEventListener("click", function () { askAssess(assessStatus, assessBox); });
    var recordBtn = el("button", "medimind-record", "Record");
    recordBtn.type = "button";
    var transcript = el("p", "medimind-transcript", "Record, then the full spoken words are written into the Bahmni note. The note is the transcript, unchanged.");
    note.appendChild(recordBtn);
    note.appendChild(transcript);
    ["subjective", "objective", "assessment", "plan"].forEach(function (name) {
      var label = el("label", null, name.charAt(0).toUpperCase() + name.slice(1));
      var box = el("textarea");
      box.dataset.field = name;
      box.rows = 3;
      note.appendChild(label);
      note.appendChild(box);
    });

    panel.appendChild(head);
    panel.appendChild(who);
    panel.appendChild(message);
    panel.appendChild(tabs);
    panel.appendChild(emr.root);
    panel.appendChild(summary);
    panel.appendChild(safety);
    panel.appendChild(note);
    panel.appendChild(assess);
    panel.appendChild(emr.footer);
    root.appendChild(tab);
    root.appendChild(panel);
    document.body.appendChild(root);

    function setOpen(open) {
      root.classList.toggle("open", open);
      document.body.classList.toggle("medimind-side-open", open);
      if (open) panel.removeAttribute("hidden");
      else panel.setAttribute("hidden", "hidden");
    }

    tab.addEventListener("click", function () {
      var opening = !root.classList.contains("open");
      setOpen(opening);
      if (opening) load(false);
    });
    close.addEventListener("click", function () { setOpen(false); });
    refresh.addEventListener("click", function () { load(true); });
    alertBell.addEventListener("click", function () {
      alertPop.classList.toggle("open");
    });
    function showTab(which) {
      emr.root.hidden = which !== "emr";
      summary.hidden = which !== "summary";
      safety.hidden = which !== "safety";
      note.hidden = which !== "note";
      assess.hidden = which !== "assess";
      if (emr.footer) emr.footer.hidden = which !== "emr";
      emrTab.classList.toggle("active", which === "emr");
      summaryTab.classList.toggle("active", which === "summary");
      safetyTab.classList.toggle("active", which === "safety");
      noteTab.classList.toggle("active", which === "note");
      assessTab.classList.toggle("active", which === "assess");
      if (which !== "emr") alertPop.classList.remove("open");
    }
    emrTab.addEventListener("click", function () { showTab("emr"); });
    summaryTab.addEventListener("click", function () { showTab("summary"); });
    safetyTab.addEventListener("click", function () { showTab("safety"); });
    noteTab.addEventListener("click", function () { showTab("note"); });
    assessTab.addEventListener("click", function () { showTab("assess"); });
    recordBtn.addEventListener("click", function () { toggleRecording(recordBtn, transcript, note); });
    emr.noteBtn.addEventListener("click", function () { showTab("note"); });
    emr.openBtn.addEventListener("click", function () { showTab("assess"); });
    emr.ackBtn.addEventListener("click", function () {
      if (emr.protocol) {
        emr.protocol.hidden = true;
        emr.ackBtn.textContent = "Protocol acknowledged";
      }
    });
    emr.chatSend.addEventListener("click", function () { sendChat(emr); });

    root._mm = {
      status: status,
      message: message,
      summary: summary,
      safety: safety,
      note: note,
      assess: assess,
      assessStatus: assessStatus,
      assessBox: assessBox,
      whoName: whoName,
      whoId: whoId,
      setOpen: setOpen,
      showTab: showTab,
      emr: emr,
      alertBell: alertBell,
      alertPop: alertPop,
      alertPopBody: alertPopBody
    };
  }

  function applyAssessResult(result) {
    var ui = document.getElementById("medimind-side") && document.getElementById("medimind-side")._mm;
    if (!ui || !ui.emr) return;
    var emr = ui.emr;
    var sections = result.sections || {};
    var draft = formatDraftForDisplay(result.draft || "");
    var modelSummary = stripIcdCodesInText(formatDraftForDisplay(
      sections.clinicalAssessment || sections.alertLevel || ""
    )).trim();
    if (modelSummary && emr.summaryText) {
      emr.summaryText.textContent = modelSummary;
      emr._modelSummaryLoaded = true;
    }
    // ClinicDx may raise urgency; vitals/safety floor cannot be downgraded.
    applyResolvedUrgency(emr, result.urgency || "");
    emr.lastAssessMode = result.mode || "";
    emr.lastDifferentials = result.differentials || sections.differentials || [];
    emr.lastActions = linesFromSection(sections.actions || "");
    emr.lastKeyPoints = linesFromSection(sections.keyPoints || "");
    renderDxSuggestions(emr);
    if (emr.showBoard && (emr.lastDifferentials.length || emr.lastActions.length || emr.lastAssessMode === "thin-chart")) {
      emr.showBoard("dx");
    }
    if (sections.safety && emr.protocol) {
      emr.protocol.hidden = false;
      emr.protocol.innerHTML = "";
      emr.protocol.appendChild(el("strong", "mm-chat-who", "ClinicDx safety"));
      var safetyBody = el("div", "mm-md-body");
      renderClinicalMarkdown(safetyBody, String(sections.safety).trim().slice(0, 600));
      emr.protocol.appendChild(safetyBody);
    }
    if (ui.assessBox) ui.assessBox.value = draft;
    if (ui.assessStatus) {
      if (result.mode === "thin-chart") {
        ui.assessStatus.textContent = "Thin chart — add chief complaint, exam findings, and meds.";
      } else {
        ui.assessStatus.textContent = draft
          ? "Assessment ready on the Assess tab. Review, then press Bahmni Save yourself."
          : "Model returned an empty summary.";
      }
    }
  }

  function askAssess(statusNode, box, opts) {
    var uuid = patientUuid();
    opts = opts || {};
    if (!uuid) {
      if (statusNode) statusNode.textContent = "Open a patient chart first.";
      return;
    }
    if (statusNode) {
      statusNode.hidden = false;
      statusNode.textContent = "Loading Summary....";
    }
    fetch(API + "/copilot/" + uuid + "/assess", { method: "POST", credentials: "same-origin" })
      .then(function (response) {
        return response.json().then(function (data) {
          return { ok: response.ok, status: response.status, data: data };
        });
      })
      .then(function (result) {
        if (!result.ok) {
          var msg = (result.data && result.data.detail) || "Summary needs ClinicDx.";
          if (statusNode) statusNode.textContent = msg;
          if (box) box.value = "";
          return;
        }
        applyAssessResult(result.data || {});
        if (box) box.value = formatDraftForDisplay(result.data.draft || "");
        if (statusNode) {
          statusNode.textContent = result.data.draft
            ? "Assessment ready. Review, then press Bahmni Save yourself."
            : "Model returned an empty summary.";
        }
      })
      .catch(function () {
        if (statusNode) statusNode.textContent = "Summary request failed.";
      });
  }

  function sendChat(emr) {
    var uuid = patientUuid();
    if (!uuid || !emr || !emr.chatInput) return;
    var message = String(emr.chatInput.value || "").trim();
    if (!message) return;
    var log = emr.chatLog;
    var empty = log.querySelector(".mm-lab-empty");
    if (empty) empty.remove();
    var you = el("div", "mm-chat-bubble mm-chat-you");
    you.appendChild(el("strong", "mm-chat-who", "You"));
    you.appendChild(el("div", "mm-md-body", message));
    log.appendChild(you);
    emr.chatInput.value = "";
    var wait = el("div", "mm-chat-bubble mm-chat-ai");
    wait.appendChild(el("strong", "mm-chat-who", "ClinicDx"));
    var waitBody = el("div", "mm-md-body", "Thinking…");
    wait.appendChild(waitBody);
    log.appendChild(wait);
    fetch(API + "/copilot/" + uuid + "/chat", {
      method: "POST",
      credentials: "same-origin",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: message })
    })
      .then(function (response) {
        return response.json().then(function (data) {
          return { ok: response.ok, data: data };
        });
      })
      .then(function (result) {
        wait.innerHTML = "";
        wait.appendChild(el("strong", "mm-chat-who", "ClinicDx"));
        var body = el("div", "mm-md-body");
        if (result.ok && result.data.reply) {
          renderClinicalMarkdown(body, result.data.reply);
        } else {
          body.textContent = (result.data && result.data.detail) || "Chat failed.";
        }
        wait.appendChild(body);
        log.scrollTop = log.scrollHeight;
      })
      .catch(function () {
        wait.innerHTML = "";
        wait.appendChild(el("strong", "mm-chat-who", "ClinicDx"));
        wait.appendChild(el("div", "mm-md-body", "Chat request failed."));
      });
  }

  function setStatus(kind, label) {
    var status = document.getElementById("medimind-side")._mm.status;
    status.className = "medimind-side-status " + kind;
    if (kind === "ready") status.textContent = "● Live Sync";
    else if (kind === "preparing") status.textContent = "● Syncing";
    else if (kind === "partial") status.textContent = "● Partial";
    else if (kind === "failed") status.textContent = "● Offline";
    else status.textContent = label || kind;
  }

  function findLab(labs, patterns) {
    labs = labs || [];
    for (var i = 0; i < labs.length; i++) {
      var name = String(labs[i].test || "").toLowerCase();
      for (var j = 0; j < patterns.length; j++) {
        if (patterns[j].test(name)) return labs[i];
      }
    }
    return null;
  }

  function setVital(tile, label, value, note, level) {
    if (!tile) return;
    tile.className = "mm-vital" + (level ? " " + level : "");
    if (tile._label && label) tile._label.textContent = label;
    tile._val.textContent = value || "—";
    tile._note.textContent = note || "";
  }

  function vitalLevel(key, value) {
    var num = parseFloat(String(value || "").replace(/[^\d.]/g, ""));
    if (!isFinite(num)) return "";
    if (key === "bp") {
      var parts = String(value).split("/");
      var sys = parseFloat(parts[0]);
      var dia = parseFloat(parts[1]);
      if ((isFinite(sys) && (sys >= 140 || sys < 90)) || (isFinite(dia) && (dia >= 90 || dia < 60))) return "bad";
      return "ok";
    }
    if (key === "hr") return (num > 100 || num < 50) ? "bad" : "ok";
    if (key === "spo2") return num < 94 ? "bad" : "ok";
    if (key === "temp") return (num >= 38 || num < 35.5) ? "warn" : "ok";
    return "";
  }

  function setVitalsStatus(emr, levels, presentCount) {
    if (!emr || !emr.vitalsStatus) return;
    var status = emr.vitalsStatus;
    var text = emr.vitalsStatusText;
    status.className = "mm-vitals-status";
    if (!presentCount) {
      status.classList.add("empty");
      text.textContent = "No vitals";
      return;
    }
    if (levels.indexOf("bad") >= 0) {
      status.classList.add("bad");
      text.textContent = "Out of range";
      return;
    }
    if (levels.indexOf("warn") >= 0) {
      status.classList.add("warn");
      text.textContent = "Needs review";
      return;
    }
    status.classList.add("ok");
    text.textContent = "Within range";
  }

  function fillVitals(emr, vitals) {
    vitals = vitals || {};
    var specs = [
      { key: "bp", tile: emr.vitalBp, label: "BP", unit: "mmHg", empty: "Not taken" },
      { key: "hr", tile: emr.vitalHr, label: "HR", unit: "bpm", empty: "Not taken" },
      { key: "spo2", tile: emr.vitalSpo2, label: "SpO₂", unit: "room air", empty: "Not taken" },
      { key: "temp", tile: emr.vitalPlatelet, label: "Temp", unit: "°C", empty: "Not taken" }
    ];
    var levels = [];
    var present = 0;
    specs.forEach(function (spec) {
      var row = vitals[spec.key];
      if (!row || row.value == null || row.value === "") {
        setVital(spec.tile, spec.label, "—", spec.empty, "");
        return;
      }
      present += 1;
      var raw = String(row.value).trim();
      var value = raw;
      var note = spec.unit;
      if (spec.key === "bp") {
        value = raw.replace(/\s*mmHg/i, "").trim();
        note = "mmHg";
      } else if (spec.key === "hr") {
        value = raw.replace(/\s*bpm/i, "").trim();
        note = "bpm";
      } else if (spec.key === "spo2") {
        value = raw.replace(/\s*%/g, "").trim() + "%";
        note = row.note || "room air";
      } else if (spec.key === "temp") {
        value = raw.replace(/\s*°?\s*C/i, "").trim();
        note = "°C";
      }
      if (row.note && spec.key !== "spo2") note = row.note;
      var level = vitalLevel(spec.key, row.value);
      if (level) levels.push(level);
      setVital(spec.tile, spec.label, value, note, level);
    });
    setVitalsStatus(emr, levels, present);
  }

  function urgencyRank(level) {
    if (level === "emergency") return 3;
    if (level === "urgent") return 2;
    if (level === "routine") return 1;
    return 0;
  }

  function maxUrgency() {
    var best = "";
    for (var i = 0; i < arguments.length; i += 1) {
      if (urgencyRank(arguments[i]) > urgencyRank(best)) best = arguments[i];
    }
    return best || "routine";
  }

  /** Hard clinical floor from vitals. ClinicDx / alerts may raise, never lower below this. */
  function urgencyFromVitals(vitals) {
    vitals = vitals || {};
    var worst = "";
    function raise(level) {
      if (urgencyRank(level) > urgencyRank(worst)) worst = level;
    }
    var bp = vitals.bp && vitals.bp.value != null ? String(vitals.bp.value) : "";
    if (bp) {
      var parts = bp.split("/");
      var sys = parseFloat(parts[0]);
      var dia = parseFloat(parts[1]);
      if (isFinite(sys) && (sys >= 180 || sys < 80)) raise("emergency");
      else if (isFinite(sys) && (sys >= 160 || sys < 90)) raise("urgent");
      if (isFinite(dia) && dia >= 120) raise("emergency");
      else if (isFinite(dia) && (dia >= 100 || dia < 60)) raise("urgent");
    }
    var hr = vitals.hr && vitals.hr.value != null ? parseFloat(String(vitals.hr.value).replace(/[^\d.]/g, "")) : NaN;
    if (isFinite(hr) && (hr >= 150 || hr < 40)) raise("emergency");
    else if (isFinite(hr) && (hr > 120 || hr < 50)) raise("urgent");
    var spo2 = vitals.spo2 && vitals.spo2.value != null ? parseFloat(String(vitals.spo2.value).replace(/[^\d.]/g, "")) : NaN;
    if (isFinite(spo2) && spo2 < 90) raise("emergency");
    else if (isFinite(spo2) && spo2 < 94) raise("urgent");
    var temp = vitals.temp && vitals.temp.value != null ? parseFloat(String(vitals.temp.value).replace(/[^\d.]/g, "")) : NaN;
    if (isFinite(temp) && (temp >= 40 || temp < 35)) raise("emergency");
    else if (isFinite(temp) && (temp >= 38.5 || temp < 35.5)) raise("urgent");
    return worst;
  }

  function urgencyFromAlerts(alerts) {
    alerts = alerts || [];
    if (!alerts.length) return "";
    var high = alerts.some(function (a) {
      var s = String(a.severity || "").toLowerCase();
      return s === "high" || s === "major" || s === "critical";
    });
    return high ? "emergency" : "urgent";
  }

  function applyResolvedUrgency(emr, clinicDxLevel) {
    if (!emr) return;
    var level = maxUrgency(emr.vitalsUrgency || "", emr.safetyUrgency || "", clinicDxLevel || "");
    emr.resolvedUrgency = level;
    setUrgency(emr, level);
  }

  function setUrgency(emr, level) {
    emr.urgRoutine.className = "";
    emr.urgUrgent.className = "";
    emr.urgEmergency.className = "";
    emr.urgRoutine.textContent = "Routine";
    emr.urgUrgent.textContent = "Urgent";
    emr.urgEmergency.textContent = "Emergency";
    if (level === "emergency") {
      emr.urgEmergency.className = "active-emergency";
    } else if (level === "urgent") {
      emr.urgUrgent.className = "active-urgent";
    } else {
      emr.urgRoutine.className = "active-routine";
    }
  }

  function shortVisitLabel(where) {
    var text = String(where || "").trim();
    if (!text) return "";
    if (/\bipd\b/i.test(text)) return "IPD";
    if (/\bopd\b/i.test(text)) return "OPD";
    if (/triage/i.test(text)) return "Triage";
    if (/er\b|emergency/i.test(text)) return "ER";
    // Prefer last path segment for long Bahmni location strings.
    var parts = text.split(/[>|/·-]/).map(function (p) { return p.trim(); }).filter(Boolean);
    var last = parts[parts.length - 1] || text;
    return last.length > 14 ? last.slice(0, 12) + "…" : last;
  }

  function titleCaseName(name) {
    return String(name || "")
      .trim()
      .split(/\s+/)
      .filter(Boolean)
      .map(function (part) {
        return part.charAt(0).toUpperCase() + part.slice(1).toLowerCase();
      })
      .join(" ");
  }

  function slot(value, fallback) {
    var text = String(value == null ? "" : value).replace(/\s+/g, " ").trim();
    return text || fallback;
  }

  /** ICD-11 / coded labels → disease display name only (e.g. "FA80- - - Disc…" → "Disc…"). */
  function diseaseDisplayName(raw) {
    var text = String(raw == null ? "" : raw).replace(/\s+/g, " ").trim();
    if (!text) return "";
    var dashed = text.match(/^[A-Z][A-Z0-9.]{0,14}(?:\s*-\s*)+(.+)$/i);
    if (dashed && dashed[1] && /[A-Za-z]{3,}/.test(dashed[1])) return dashed[1].trim();
    var spaced = text.match(/^[A-Z][A-Z0-9]*(?:\.[A-Z0-9]+)?\s+(.+)$/i);
    if (spaced && spaced[1] && /[A-Za-z]{3,}/.test(spaced[1])) return spaced[1].trim();
    return text;
  }

  function stripIcdCodesInText(raw) {
    return String(raw || "").replace(
      /\b[A-Z][A-Z0-9]*(?:\.[A-Z0-9]+)?(?:\s*-\s*)+/g,
      ""
    ).replace(/\s{2,}/g, " ").trim();
  }

  function vitalValue(vitals, key) {
    var row = (vitals || {})[key];
    if (!row || row.value == null || row.value === "") return "";
    return [row.value, row.unit].filter(Boolean).join(" ");
  }

  function demographicsFromPage() {
    var demo = { age: null, gender: "" };
    var nodes = document.querySelectorAll(
      ".patient-gender-age, .patient-info, .patient-attribute, .patient-value, .patient-details, [ng-bind*='age'], [ng-bind*='gender']"
    );
    for (var i = 0; i < nodes.length && (demo.age == null || !demo.gender); i++) {
      var text = String(nodes[i].innerText || nodes[i].textContent || "").replace(/\s+/g, " ").trim();
      if (!text || text.length > 80) continue;
      var ageMatch = text.match(/(\d{1,3})\s*(?:years?|yrs?|y\.?o\.?)?/i);
      if (demo.age == null && ageMatch && /year|yr|y\.?o|age|\d+\s*[MF]\b/i.test(text)) {
        demo.age = Number(ageMatch[1]);
      }
      if (!demo.gender) {
        if (/\b(female|woman|girl)\b/i.test(text) || /\bF\b/.test(text)) demo.gender = "female";
        else if (/\b(male|man|boy)\b/i.test(text) || /\bM\b/.test(text)) demo.gender = "male";
      }
    }
    return demo;
  }

  function fetchDemographics(uuid, done) {
    if (!uuid) return done(demographicsFromPage());
    var page = demographicsFromPage();
    fetch("/openmrs/ws/rest/v1/patient/" + uuid + "?v=custom:(person:(gender,age))", {
      credentials: "same-origin"
    })
      .then(function (response) { return response.ok ? response.json() : null; })
      .then(function (body) {
        var person = (body && body.person) || {};
        var gender = String(person.gender || "").toUpperCase();
        done({
          age: person.age != null ? person.age : page.age,
          gender: gender === "F" ? "female" : gender === "M" ? "male" : page.gender || ""
        });
      })
      .catch(function () { done(page); });
  }

  function chiefComplaintFromChart(data) {
    if (data.formFill && data.formFill.complaint) return diseaseDisplayName(data.formFill.complaint);
    var findings = data.noteFindings || [];
    for (var i = 0; i < findings.length; i++) {
      if (findings[i] && findings[i].line) return diseaseDisplayName(findings[i].line);
    }
    var events = data.timeline || [];
    for (var j = 0; j < events.length; j++) {
      var kind = String(events[j].kind || "");
      var text = String(events[j].text || "").trim();
      if (text && /complaint|history|note|illness/i.test(kind + " " + text)) return diseaseDisplayName(text);
    }
    if (data.diagnoses && data.diagnoses[0] && data.diagnoses[0].name) {
      return "concerns related to " + diseaseDisplayName(data.diagnoses[0].name);
    }
    return "";
  }

  function chartOnset(data) {
    var fill = data.formFill || {};
    var candidates = [fill.onset, fill.onsetDate, fill.duration, data.onset, data.onsetDate];
    for (var i = 0; i < candidates.length; i++) {
      var text = String(candidates[i] == null ? "" : candidates[i]).replace(/\s+/g, " ").trim();
      if (!text) continue;
      if (/not\s+document|unknown|n\/?a|none/i.test(text)) continue;
      return text;
    }
    return "";
  }

  function chartSymptomBits(data) {
    var fill = data.formFill || {};
    var symptoms = data.symptoms || fill.symptoms || {};
    if (typeof symptoms === "string") {
      var one = symptoms.replace(/\s+/g, " ").trim();
      return one && !/not\s+document/i.test(one) ? { narrative: one } : null;
    }
    var quality = String(symptoms.quality || fill.quality || "").trim();
    var pattern = String(symptoms.pattern || fill.pattern || "").trim();
    var triggers = String(symptoms.triggers || fill.aggravating || fill.triggers || "").trim();
    var relieved = String(symptoms.relieved || fill.relieving || fill.relieved || "").trim();
    var bits = {};
    if (quality && !/not\s+document/i.test(quality)) bits.quality = quality;
    if (pattern && !/not\s+document/i.test(pattern)) bits.pattern = pattern;
    if (triggers && !/not\s+document/i.test(triggers)) bits.triggers = triggers;
    if (relieved && !/not\s+document/i.test(relieved)) bits.relieved = relieved;
    return Object.keys(bits).length ? bits : null;
  }

  function ruleBasedSummary(data, demo) {
    demo = demo || {};
    var vitals = data.vitals || {};
    var history = data.history || {};
    var meds = (data.medications || []).map(function (m) { return m.drug; }).filter(Boolean);
    var allergies = history.allergies || [];
    var medical = (history.medical || []).map(diseaseDisplayName).filter(Boolean);
    var tempRaw = vitalValue(vitals, "temp");
    var tempNum = parseFloat(String(tempRaw).replace(/[^\d.]/g, ""), 10);
    var bp = vitalValue(vitals, "bp");
    var hr = vitalValue(vitals, "hr");
    var spo2 = vitalValue(vitals, "spo2");
    var rr = vitalValue(vitals, "rr") || vitalValue(vitals, "respiratoryRate");
    var whoBits = [];
    if (demo.age != null) whoBits.push(demo.age + "-year-old");
    if (demo.gender) whoBits.push(demo.gender);
    var who = whoBits.join(" ") || "patient";
    var complaint = chiefComplaintFromChart(data);
    var onset = chartOnset(data);
    var paragraphs = [];

    var opening = "We have a " + who;
    if (complaint) {
      opening += " presenting with " + complaint;
      if (onset) opening += " which started " + onset;
    }
    opening += ".";
    paragraphs.push(opening);

    var symptomBits = chartSymptomBits(data);
    if (symptomBits) {
      if (symptomBits.narrative) {
        paragraphs.push("Symptoms: " + symptomBits.narrative + ".");
      } else {
        var symptomParts = [];
        if (symptomBits.quality) symptomParts.push("characterized as " + symptomBits.quality);
        if (symptomBits.pattern) symptomParts.push(symptomBits.pattern);
        if (symptomBits.triggers) symptomParts.push("aggravated by " + symptomBits.triggers);
        if (symptomBits.relieved) symptomParts.push("relieved by " + symptomBits.relieved);
        if (symptomParts.length) {
          paragraphs.push("The symptoms are " + symptomParts.join(", ") + ".");
        }
      }
    }

    var historyParts = [];
    if (medical.length) {
      historyParts.push("Pertinent past medical history includes " + medical.slice(0, 3).join("; "));
    }
    if (meds.length) {
      historyParts.push("current medications are " + meds.slice(0, 4).join("; "));
    }
    if (allergies.length) {
      historyParts.push("known allergy to " + allergies.slice(0, 3).join(", "));
    }
    if (historyParts.length) {
      var hist = historyParts[0];
      for (var h = 1; h < historyParts.length; h++) {
        hist += (h === historyParts.length - 1 ? ", and " : "; ") + historyParts[h];
      }
      paragraphs.push(hist + ".");
    }

    var vitalsBits = [];
    if (bp) vitalsBits.push("BP " + bp);
    if (hr) vitalsBits.push("HR " + hr);
    if (rr) vitalsBits.push("RR " + rr);
    if (spo2) vitalsBits.push("SpO₂ " + spo2);
    var objectiveParts = [];
    if (!isNaN(tempNum)) {
      objectiveParts.push(tempNum >= 38 ? "febrile" : "afebrile");
    }
    if (vitalsBits.length) {
      objectiveParts.push("vitals " + vitalsBits.join(", "));
    }
    if (data.abnormalLabs && data.abnormalLabs[0] && data.abnormalLabs[0].test) {
      objectiveParts.push("exam notable for " + String(data.abnormalLabs[0].test));
    }
    if (objectiveParts.length) {
      paragraphs.push("On objective evaluation: " + objectiveParts.join("; ") + ".");
    }

    return paragraphs.join("\n\n");
  }

  function narrativeFromSummary(data) {
    return ruleBasedSummary(data, demographicsFromPage());
  }

  function locationFromSummary(data) {
    var sections = (data.summary && data.summary.sections) || [];
    for (var i = 0; i < sections.length; i++) {
      var lines = sections[i].lines || [];
      for (var j = 0; j < lines.length; j++) {
        var value = String(lines[j].value || "");
        var parts = value.split("·").map(function (p) { return p.trim(); });
        if (parts.length >= 2) return { when: parts[0], where: parts[1] };
      }
    }
    return { when: "", where: "" };
  }

  function clearPanel(label) {
    var ui = document.getElementById("medimind-side")._mm;
    ui.summary.textContent = "";
    ui.safety.textContent = "";
    if (ui.note) ui.note.querySelectorAll("textarea").forEach(function (box) { box.value = ""; });
    if (ui.assess) ui.assess.querySelectorAll("textarea").forEach(function (box) { box.value = ""; });
    if (ui.assessStatus) {
      ui.assessStatus.textContent = "MediMind drafts Assessment, Differentials, Plan, and Safety from this chart only. Review, then press Bahmni Save yourself.";
    }
    ui.message.textContent = "";
    ui.whoName.textContent = label || "Loading…";
    ui.whoId.textContent = "";
    setStatus("preparing", "Preparing");
  }

  function lineMap(sections) {
    var map = {};
    (sections || []).forEach(function (section) {
      (section.lines || []).forEach(function (line) {
        if (line && line.label) map[String(line.label).toLowerCase()] = line.value || "";
      });
    });
    return map;
  }

  function initials(name) {
    var parts = String(name || "MM").trim().split(/\s+/).filter(Boolean);
    if (!parts.length) return "MM";
    return ((parts[0][0] || "") + (parts[1] ? parts[1][0] : "")).toUpperCase();
  }

  function setWidgetValue(widget, text) {
    var node = widget && widget.querySelector(".mm-widget-value");
    if (node) node.textContent = text;
  }

  function prettyDate(value) {
    if (value == null || value === "") return "";
    var months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
    var date = null;
    if (typeof value === "number" || /^\d{12,}$/.test(String(value))) {
      date = new Date(Number(value));
    } else {
      var day = String(value).slice(0, 10);
      var parts = day.split("-");
      if (parts.length === 3) date = new Date(Number(parts[0]), Number(parts[1]) - 1, Number(parts[2]));
    }
    if (!date || isNaN(date.getTime())) return String(value).slice(0, 10);
    return date.getDate() + " " + months[date.getMonth()] + " " + date.getFullYear();
  }

  function fillBoard(emr, data, alerts, high) {
    var diagnoses = data.diagnoses || [];
    emr.dxPanel.textContent = "";
    if (!diagnoses.length) {
      emr.dxPanel.appendChild(el("p", "mm-lab-empty", "No coded diagnosis in this Bahmni window yet."));
    } else {
      emr.dxPanel.appendChild(el("div", "mm-kicker", "Coded in Bahmni chart"));
      diagnoses.forEach(function (item, idx) {
        var row = el("div", "mm-dx" + (idx === 0 ? " mm-dx-primary" : " mm-dx-monitored"));
        var head = el("div", "mm-dx-head");
        head.appendChild(el("strong", null, diseaseDisplayName(item.name) || "Diagnosis"));
        head.appendChild(el("span", "mm-badge " + (idx === 0 ? "mm-badge-hot" : "mm-badge-warm"), idx === 0 ? "Chart" : "Chart"));
        row.appendChild(head);
        var meta = [];
        if (item.certainty) meta.push(String(item.certainty));
        if (item.date) meta.push(prettyDate(item.date));
        if (meta.length) row.appendChild(el("div", "mm-dx-code", meta.join(" · ")));
        emr.dxPanel.appendChild(row);
      });
    }
    renderDxSuggestions(emr);

    var meds = data.medications || [];
    emr.tabMed.textContent = "Meds & Alerts (" + (meds.length + alerts.length) + ")";
    emr.medPanel.textContent = "";
    if (!meds.length && !alerts.length) {
      emr.medPanel.appendChild(el("p", "mm-lab-empty", "No medicine or alert in this window."));
    }
    alerts.forEach(function (alert) {
      var card = el("div", "mm-allergy");
      var head = el("div", "mm-allergy-head");
      head.appendChild(el("strong", null, (alert.type || "Alert").toUpperCase() + (alert.drug ? ": " + alert.drug : "")));
      head.appendChild(el("span", "mm-badge mm-badge-hot", String(alert.severity || "alert").toUpperCase()));
      card.appendChild(head);
      card.appendChild(el("div", "mm-med-meta", alert.message || ""));
      emr.medPanel.appendChild(card);
    });
    meds.forEach(function (med) {
      var card = el("div", "mm-med");
      var head = el("div", "mm-med-head");
      head.appendChild(el("strong", null, med.drug || "Medication"));
      head.appendChild(el("span", "mm-badge mm-badge-ok", "Active"));
      card.appendChild(head);
      var detail = [med.dose, med.doseUnits, med.route, med.frequency].filter(Boolean).join(" · ");
      if (detail) card.appendChild(el("div", "mm-med-meta", detail));
      emr.medPanel.appendChild(card);
    });

    var events = data.timeline || [];
    emr.tabTime.textContent = "Timeline";
    emr.timePanel.textContent = "";
    if (!events.length) {
      emr.timePanel.appendChild(el("p", "mm-lab-empty", "No dated events in this window."));
    } else {
      events.slice(0, 8).forEach(function (event) {
        var row = el("div", "mm-time");
        row.appendChild(el("div", "mm-time-date", prettyDate(event.date)));
        row.appendChild(el("strong", null, event.text || ""));
        row.appendChild(el("div", "mm-time-kind", event.kind || ""));
        emr.timePanel.appendChild(row);
      });
      if (events.length > 8) {
        var more = el("button", "mm-view-all", "View all " + events.length + " clinical notes →");
        more.type = "button";
        more.addEventListener("click", function () {
          events.slice(8).forEach(function (event) {
            var row = el("div", "mm-time");
            row.appendChild(el("div", "mm-time-date", prettyDate(event.date)));
            row.appendChild(el("strong", null, event.text || ""));
            row.appendChild(el("div", "mm-time-kind", event.kind || ""));
            emr.timePanel.insertBefore(row, more);
          });
          more.remove();
        });
        emr.timePanel.appendChild(more);
      }
    }

    if (high || alerts.length) {
      emr.protocol.hidden = false;
      var top = alerts[0] || {};
      emr.protocol.innerHTML = "";
      emr.protocol.appendChild(el("strong", null, "Risk alert active"));
      emr.protocol.appendChild(document.createTextNode((top.drug ? top.drug + " — " : "") + (top.message || (alerts.length + " safety flag(s) need review."))));
    } else if (!emr.protocol.querySelector("strong") || emr.protocol.querySelector("strong").textContent !== "ClinicDx safety") {
      emr.protocol.hidden = true;
      emr.protocol.textContent = "";
    }

    var history = data.history || {};
    if (emr.histPanel) {
      emr.histPanel.textContent = "";
      var medical = history.medical || [];
      var surgical = history.surgical || [];
      var allergyHist = history.allergies || [];
      if (!medical.length && !surgical.length && !allergyHist.length) {
        emr.histPanel.appendChild(el("p", "mm-lab-empty", "No medical/surgical history coded in this window."));
      } else {
        if (medical.length) {
          emr.histPanel.appendChild(el("div", "mm-kicker", "Medical history"));
          medical.forEach(function (row) {
            var card = el("div", "mm-med");
            card.appendChild(el("strong", null, row));
            emr.histPanel.appendChild(card);
          });
        }
        if (surgical.length) {
          emr.histPanel.appendChild(el("div", "mm-kicker", "Surgical history"));
          surgical.forEach(function (row) {
            var card = el("div", "mm-med");
            card.appendChild(el("strong", null, row));
            emr.histPanel.appendChild(card);
          });
        }
        if (allergyHist.length) {
          emr.histPanel.appendChild(el("div", "mm-kicker", "Allergy history"));
          allergyHist.forEach(function (row) {
            var card = el("div", "mm-allergy");
            card.appendChild(el("strong", null, row));
            emr.histPanel.appendChild(card);
          });
        }
      }
    }
  }

  function renderEmr(data) {
    var ui = document.getElementById("medimind-side")._mm;
    var emr = ui.emr;
    if (!emr) return;
    var name = titleCaseName(data.name || "Name not in chart");
    var id = data.identifier ? String(data.identifier) : "";
    var loc = locationFromSummary(data);
    var admit = loc.when ? ("Admitted " + prettyDate(loc.when)) : "";
    emr.patientName.textContent = name;
    emr.patientId.textContent = id;
    emr.patientMeta.textContent = [id, admit].filter(Boolean).join(" · ") || "Chart loaded";
    var pill = shortVisitLabel(loc.where);
    if (pill) {
      emr.deptTag.hidden = false;
      emr.deptTag.textContent = pill;
      emr.deptTag.title = loc.where || pill;
    } else {
      emr.deptTag.hidden = true;
      emr.deptTag.textContent = "";
      emr.deptTag.title = "";
    }
    emr.adm.textContent = admit;

    emr._lastChartData = data;
    if (data.patientUuid !== window.__mmAssessedUuid) {
      emr._modelSummaryLoaded = false;
    }
    if (!emr._modelSummaryLoaded) {
      emr.summaryText.textContent = ruleBasedSummary(data, emr._demo || demographicsFromPage());
    }

    var labs = data.abnormalLabs || [];
    emr.labChips.textContent = "";
    labs.slice(0, 3).forEach(function (lab, idx) {
      var chip = el("span", "mm-lab-chip " + (idx === 0 ? "bad" : "pending"));
      chip.textContent = (lab.test || "Lab") + ": " + [lab.result, lab.unit].filter(Boolean).join(" ");
      emr.labChips.appendChild(chip);
    });
    if (!labs.length) {
      emr.labChips.appendChild(el("span", "mm-lab-chip pending", "No abnormal labs in window"));
    }

    fillVitals(emr, data.vitals || {});

    var alerts = (data.safety && data.safety.alerts) || [];
    var high = alerts.some(function (a) {
      var s = String(a.severity || "").toLowerCase();
      return s === "high" || s === "major" || s === "critical";
    });
    emr.vitalsUrgency = urgencyFromVitals(data.vitals || {});
    emr.safetyUrgency = urgencyFromAlerts(alerts);
    applyResolvedUrgency(emr, "");
    fillBoard(emr, data, alerts, high || emr.resolvedUrgency === "emergency");

    fetchDemographics(data.patientUuid, function (demo) {
      emr._demo = demo;
      if (!emr._modelSummaryLoaded && emr._lastChartData === data) {
        emr.summaryText.textContent = ruleBasedSummary(data, demo);
      }
    });

    // Auto model summary once per patient when chart is ready
    if (data.patientUuid && data.patientUuid !== window.__mmAssessedUuid) {
      window.__mmAssessedUuid = data.patientUuid;
      askAssess(ui.assessStatus, ui.assessBox, { auto: true });
    }

    ui.alertBell.dataset.count = String(alerts.length);
    ui.alertBell.classList.toggle("has-alerts", alerts.length > 0);
    ui.alertPopBody.textContent = "";
    if (!alerts.length) {
      ui.alertPopBody.appendChild(el("p", "mm-lab-empty", "No safety alert."));
    } else {
      alerts.forEach(function (alert) {
        var card = el("div", "mm-alert sev-" + (alert.severity || "info"));
        card.appendChild(el("strong", null, (alert.type || "note").toUpperCase()));
        if (alert.drug) card.appendChild(document.createTextNode(" — " + alert.drug));
        card.appendChild(el("div", null, alert.message || ""));
        ui.alertPopBody.appendChild(card);
      });
    }
  }

  function render(data) {
    var ui = document.getElementById("medimind-side")._mm;
    if (data.patientUuid && data.patientUuid !== patientUuid()) return;
    ui.whoName.textContent = titleCaseName(data.name || "Name not in chart");
    ui.whoId.textContent = data.identifier ? String(data.identifier) : "ID not in chart";
    ui.message.textContent = data.statusMessage || "";
    if (data.status === "partial") setStatus("partial", "Partial");
    else if (data.status === "ready") setStatus("ready", "Ready");
    else setStatus("ready", "Ready");

    ui.summary.textContent = "";
    (data.summary && data.summary.sections || []).forEach(function (section) {
      var block = el("section");
      block.appendChild(el("h4", null, section.title));
      (section.lines || []).forEach(function (line) {
        var row = el("p");
        row.appendChild(el("strong", null, (line.label || "") + ": "));
        row.appendChild(document.createTextNode(line.value || ""));
        if (line.source) row.appendChild(el("span", "src", " (" + line.source + ")"));
        block.appendChild(row);
      });
      ui.summary.appendChild(block);
    });
    var placed = applyFormFill(data.formFill, null);
    var placedText = fillStatus(placed);
    if (placedText) ui.summary.appendChild(el("p", null, placedText));

    ui.safety.textContent = "";
    var alerts = (data.safety && data.safety.alerts) || [];
    if (!alerts.length) ui.safety.appendChild(el("p", null, "No safety alert."));
    alerts.forEach(function (alert) {
      var card = el("div", "mm-alert sev-" + (alert.severity || "info"));
      card.appendChild(el("strong", null, (alert.type || "note").toUpperCase()));
      if (alert.drug) card.appendChild(document.createTextNode(" — " + alert.drug));
      card.appendChild(el("div", null, alert.message || ""));
      if (alert.ruleVersion) card.appendChild(el("div", "src", "rule " + alert.ruleVersion));
      ui.safety.appendChild(card);
    });

    renderEmr(data);
  }

  function load(refresh) {
    var uuid = patientUuid();
    var ui = document.getElementById("medimind-side")._mm;
    if (!uuid) {
      ui.message.textContent = "Open a patient chart first.";
      setStatus("failed", "Failed");
      return;
    }
    if (refresh || uuid !== currentUuid) {
      currentUuid = uuid;
      startedAt = Date.now();
    }
    setStatus("preparing", "Preparing");
    var url = API + "/copilot/" + uuid + (refresh ? "?refresh=1" : "");
    fetch(url, { credentials: "same-origin" }).then(function (response) {
      return response.json().then(function (body) { return { status: response.status, body: body }; });
    }).then(function (result) {
      if (uuid !== patientUuid()) return;
      if (result.status === 202 || (result.body && result.body.status === "preparing")) {
        ui.message.textContent = (result.body && result.body.message) || "Loading chart…";
        if ((Date.now() - startedAt) / 1000 < 90) {
          pollTimer = setTimeout(function () { load(false); }, 3000);
        } else {
          ui.message.textContent = "Timed out waiting for the chart.";
          setStatus("failed", "Failed");
        }
        return;
      }
      if (result.status >= 400) {
        ui.message.textContent = (result.body && result.body.detail) || "Could not load MediMind.";
        setStatus("failed", "Failed");
        return;
      }
      render(result.body || {});
    }).catch(function () {
      ui.message.textContent = "MediMind is not reachable.";
      setStatus("failed", "Failed");
    });
  }

  var recorder = null;

  function encodeWav(samples, rate) {
    var buffer = new ArrayBuffer(44 + samples.length * 2);
    var view = new DataView(buffer);
    function write(offset, text) {
      for (var i = 0; i < text.length; i++) view.setUint8(offset + i, text.charCodeAt(i));
    }
    write(0, "RIFF");
    view.setUint32(4, 36 + samples.length * 2, true);
    write(8, "WAVE");
    write(12, "fmt ");
    view.setUint32(16, 16, true);
    view.setUint16(20, 1, true);
    view.setUint16(22, 1, true);
    view.setUint32(24, rate, true);
    view.setUint32(28, rate * 2, true);
    view.setUint16(32, 2, true);
    view.setUint16(34, 16, true);
    write(36, "data");
    view.setUint32(40, samples.length * 2, true);
    var offset = 44;
    for (var i = 0; i < samples.length; i++) {
      var sample = Math.max(-1, Math.min(1, samples[i]));
      view.setInt16(offset, sample < 0 ? sample * 0x8000 : sample * 0x7fff, true);
      offset += 2;
    }
    return new Blob([buffer], { type: "audio/wav" });
  }

  function micBlockedReason() {
    var host = location.hostname || "";
    var isLocal = host === "localhost" || host === "127.0.0.1";
    if (!window.isSecureContext && !isLocal) {
      var httpsHost = host || "192.168.1.28";
      return (
        "Microphone needs HTTPS. Open Bahmni as https://" + httpsHost + ":9543 " +
        "(not http://…:9180). Accept the certificate warning once, then allow the mic."
      );
    }
    if (!navigator.mediaDevices || typeof navigator.mediaDevices.getUserMedia !== "function") {
      return "This browser cannot access the microphone on this page. Use Chrome/Edge over HTTPS.";
    }
    if (!(window.AudioContext || window.webkitAudioContext)) {
      return "This browser cannot record audio.";
    }
    return "";
  }

  function toggleRecording(button, transcript, noteBox, targetField) {
    if (recorder) {
      recorder.stop();
      button.textContent = "Record";
      return;
    }
    var blocked = micBlockedReason();
    if (blocked) {
      transcript.textContent = blocked;
      return;
    }
    navigator.mediaDevices.getUserMedia({
      audio: { echoCancellation: true, noiseSuppression: true, autoGainControl: true, channelCount: 1 }
    }).then(function (stream) {
      var AudioCtx = window.AudioContext || window.webkitAudioContext;
      var context = new AudioCtx();
      var source = context.createMediaStreamSource(stream);
      var analyser = context.createAnalyser();
      var processor = context.createScriptProcessor(4096, 1, 1);
      var silent = context.createGain();
      var samples = [];
      analyser.fftSize = 1024;
      silent.gain.value = 0;
      source.connect(analyser);
      source.connect(processor);
      processor.connect(silent);
      silent.connect(context.destination);
      context.resume();
      var levels = new Uint8Array(analyser.fftSize);
      var peak = 0;
      var meter = window.setInterval(function () {
        analyser.getByteTimeDomainData(levels);
        var local = 0;
        for (var i = 0; i < levels.length; i += 8) {
          var value = Math.abs(levels[i] - 128) / 128;
          if (value > local) local = value;
        }
        if (local > peak) peak = local;
        transcript.textContent = "Listening  " + new Array(Math.min(10, Math.round(local * 24)) + 1).join("▮");
      }, 120);
      processor.onaudioprocess = function (event) {
        var input = event.inputBuffer.getChannelData(0);
        samples.push(new Float32Array(input));
      };
      var stopped = false;
      var handle = {
        stop: function () {
          if (stopped) return;
          stopped = true;
          window.clearInterval(meter);
          processor.disconnect();
          analyser.disconnect();
          source.disconnect();
          stream.getTracks().forEach(function (track) { track.stop(); });
          var total = 0;
          for (var i = 0; i < samples.length; i++) total += samples[i].length;
          var merged = new Float32Array(total);
          var offset = 0;
          for (var j = 0; j < samples.length; j++) {
            merged.set(samples[j], offset);
            offset += samples[j].length;
          }
          var rate = context.sampleRate || 48000;
          var targetRate = 16000;
          var pcm = merged;
          if (rate !== targetRate && merged.length) {
            var ratio = rate / targetRate;
            var down = new Float32Array(Math.max(1, Math.floor(merged.length / ratio)));
            for (var k = 0; k < down.length; k++) down[k] = merged[Math.min(merged.length - 1, Math.floor(k * ratio))];
            pcm = down;
            rate = targetRate;
          }
          context.close();
          recorder = null;
          button.textContent = "Record";
          var blob = encodeWav(pcm, rate);
          if (peak < 0.04 || pcm.length < 1600) {
            transcript.textContent = "The microphone was silent. Allow the mic, watch the bars move while you speak, then press Stop.";
            return;
          }
          sendVoice(blob, transcript, noteBox, targetField);
        }
      };
      recorder = handle;
      button.textContent = "Stop";
    }).catch(function (err) {
      var name = String((err && err.name) || "");
      var secureHint = micBlockedReason();
      if (secureHint) {
        transcript.textContent = secureHint;
        return;
      }
      if (name === "NotAllowedError" || name === "PermissionDeniedError") {
        transcript.textContent = "Microphone blocked for this site. Click the lock/tune icon in the address bar → Site settings → Microphone → Allow, then reload.";
        return;
      }
      if (name === "NotFoundError" || name === "DevicesNotFoundError") {
        transcript.textContent = "No microphone was found on this computer.";
        return;
      }
      if (name === "NotReadableError" || name === "TrackStartError") {
        transcript.textContent = "Microphone is busy in another app. Close Zoom/Teams/etc., then try Record again.";
        return;
      }
      transcript.textContent = "Could not start the microphone" + (name ? " (" + name + ")" : "") + ". Allow mic access and try again.";
    });
  }

  function fieldLabel(area) {
    var node = area;
    for (var depth = 0; depth < 8 && node; depth += 1) {
      node = node.parentElement;
      if (!node) break;
      var text = (node.innerText || "").replace(/\s+/g, " ").trim();
      if (text && text.length < 220) return text;
    }
    return "";
  }

  function setNgValue(area, next) {
    if (window.angular && angular.element) {
      var ngModel = angular.element(area).controller && angular.element(area).controller("ngModel");
      if (ngModel) {
        ngModel.$setViewValue(next);
        ngModel.$render();
        return;
      }
    }
    if (window.jQuery) {
      window.jQuery(area).val(next).trigger("input").trigger("change");
    } else {
      area.value = next;
      area.dispatchEvent(new Event("input", { bubbles: true }));
      area.dispatchEvent(new Event("change", { bubbles: true }));
    }
  }

  function findLabeledObs(pattern) {
    var labels = document.querySelectorAll("label");
    var best = null;
    var bestDepth = 99;
    Array.prototype.forEach.call(labels, function (label) {
      var text = (label.innerText || "").replace(/\s+/g, " ").trim();
      if (!pattern.test(text) || text.length > 90) return;
      var node = label;
      for (var depth = 0; depth < 8 && node; depth += 1) {
        var inputs = node.querySelectorAll('input[type="text"][ng-model="observation.value"], textarea[ng-model="observation.value"]');
        if (inputs.length && depth < bestDepth) {
          var candidate = null;
          Array.prototype.forEach.call(inputs, function (input) {
            if (!candidate && !(input.closest && input.closest("#medimind-side"))) candidate = input;
          });
          if (candidate) {
            best = candidate;
            bestDepth = depth;
          }
        }
        node = node.parentElement;
      }
    });
    return best;
  }

  function appendObs(field, text) {
    if (!field || !text) return false;
    var current = (field.value || "").trim();
    if (current.toLowerCase().indexOf(String(text).toLowerCase()) >= 0) return false;
    setNgValue(field, current ? current + "\n" + text : text);
    return true;
  }

  function diagnosisListed(name) {
    var needle = String(name || "").trim().toLowerCase();
    if (!needle) return true;
    var inputs = document.querySelectorAll('input[ng-model="diagnosis.codedAnswer.name"]');
    for (var i = 0; i < inputs.length; i += 1) {
      if ((inputs[i].value || "").trim().toLowerCase() === needle) return true;
    }
    var shown = document.querySelectorAll(".diagnosis-name");
    for (var j = 0; j < shown.length; j += 1) {
      if ((shown[j].innerText || "").toLowerCase().indexOf(needle) >= 0) return true;
    }
    return false;
  }

  function addDiagnosis(name) {
    if (diagnosisListed(name)) return false;
    var inputs = document.querySelectorAll('input[ng-model="diagnosis.codedAnswer.name"]');
    var blank = null;
    Array.prototype.forEach.call(inputs, function (input) {
      if (!blank && !(input.value || "").trim()) blank = input;
    });
    if (!blank) return false;
    setNgValue(blank, name);
    var accept = blank.parentElement && blank.parentElement.querySelector("button.accept-btn");
    if (accept && !accept.disabled) accept.click();
    return true;
  }

  function applyFormFill(fill, skipField) {
    var written = [];
    var missing = [];
    if (!fill) return { written: written, missing: missing };
    if (fill.complaint) {
      var complaint = findLabeledObs(/^Chief Complaint/i);
      if (complaint && complaint !== skipField && !(complaint.value || "").trim()) {
        if (appendObs(complaint, fill.complaint)) written.push("Chief Complaint");
      }
    }
    if (fill.past) {
      var past = findLabeledObs(/past medical/i);
      if (!past) missing.push("Past history");
      else if (past !== skipField && !(past.value || "").trim() && appendObs(past, fill.past)) written.push("Past history");
    }
    if (fill.plan) {
      var plan = findLabeledObs(/^Plan\b/i);
      if (!plan) missing.push("Plan");
      else if (plan !== skipField && appendObs(plan, fill.plan)) written.push("Plan");
    }
    var diagnoses = fill.diagnoses || [];
    var addedDx = [];
    diagnoses.forEach(function (name) {
      if (addDiagnosis(name)) addedDx.push(name);
    });
    if (addedDx.length) written.push("Diagnosis " + addedDx.join(", "));
    else if (diagnoses.length && !diagnoses.every(diagnosisListed)) missing.push("Diagnosis");
    return { written: written, missing: missing };
  }

  function fillStatus(result) {
    if (!result || (!result.written.length && !result.missing.length)) return "";
    var parts = [];
    if (result.written.length) {
      parts.push("Added to the Bahmni form: " + result.written.join(", ") + ". Press Bahmni Save.");
    }
    if (result.missing.length) {
      parts.push("Open " + result.missing.join(" and ") + " on this visit, then Refresh, so those items can be added.");
    }
    return parts.join(" ");
  }

  function writeTranscriptToBahmniNote(transcript) {
    var label = Array.prototype.slice.call(document.querySelectorAll("label")).find(function (el) {
      return /^Chief Complaint/i.test((el.innerText || "").trim());
    });
    var target = null;
    var node = label;
    for (var depth = 0; depth < 8 && node && !target; depth += 1) {
      var inputs = node.querySelectorAll ? node.querySelectorAll("input") : [];
      Array.prototype.forEach.call(inputs, function (input) {
        if (!target && input.getAttribute("ng-model") === "observation.value" && input.type === "text") {
          target = input;
        }
      });
      node = node.parentElement;
    }
    if (!target) return false;
    var current = target.value || "";
    var next = current.trim() ? current.replace(/\s*$/, " ") + transcript : transcript;
    setNgValue(target, next);
    target.focus();
    return true;
  }

  function savePending(uuid, spoken, fill) {
    try {
      sessionStorage.setItem("mmPendingNote", JSON.stringify({
        uuid: uuid,
        transcript: spoken,
        formFill: fill || {},
        at: Date.now()
      }));
    } catch (e) {}
  }

  function readPending() {
    try {
      var pending = JSON.parse(sessionStorage.getItem("mmPendingNote") || "null");
      if (!pending || !pending.uuid || Date.now() - pending.at > 120000) {
        sessionStorage.removeItem("mmPendingNote");
        return null;
      }
      return pending;
    } catch (e) {
      return null;
    }
  }

  function openHistoryForm() {
    var nodes = document.querySelectorAll("a, button, span, h2, h3, .section-title");
    for (var i = 0; i < nodes.length; i += 1) {
      var text = (nodes[i].innerText || "").replace(/\s+/g, " ").trim();
      if (text.length > 80 || !/History and Physical/i.test(text)) continue;
      if (nodes[i].closest && nodes[i].closest("#medimind-side")) continue;
      nodes[i].click();
      return true;
    }
    return false;
  }

  function openVisitForm(uuid) {
    if ((location.hash || "").indexOf("concept-set-group/observations") !== -1) return;
    var visit = (location.hash || "").match(/visit\/([0-9a-fA-F-]{36})/);
    location.hash = visit
      ? "#/default/patient/" + uuid + "/dashboard/visit/" + visit[1] + "/concept-set-group/observations"
      : "#/default/patient/" + uuid + "/dashboard/concept-set-group/observations?encounterUuid=active";
  }

  function flushPending() {
    var pending = readPending();
    var uuid = patientUuid();
    if (!pending || pending.uuid !== uuid) return;
    if (!findLabeledObs(/^Chief Complaint/i)) {
      if (!window.__mmHistoryClicked) {
        window.__mmHistoryClicked = true;
        openHistoryForm();
      }
      return;
    }
    window.__mmHistoryClicked = false;
    var written = pending.transcript ? writeTranscriptToBahmniNote(pending.transcript) : false;
    var placed = applyFormFill(pending.formFill, null);
    if (!written && !placed.written.length) return;
    sessionStorage.removeItem("mmPendingNote");
    var status = document.querySelector("#medimind-side .medimind-transcript");
    if (status) {
      var extra = fillStatus(placed);
      status.textContent = "Written into Chief Complaint. Press Bahmni Save." + (extra ? " " + extra : "");
    }
  }

  function sendVoice(blob, transcript, noteBox, targetField) {
    var uuid = patientUuid();
    transcript.textContent = "Transcribing…";
    var body = new FormData();
    var filename = (blob && blob.type === "audio/wav") ? "note.wav" : "note.webm";
    body.append("audio", blob, filename);
    fetch(API + "/copilot/" + uuid + "/voice", { method: "POST", body: body, credentials: "same-origin" })
      .then(function (response) { return response.json().then(function (data) { return { ok: response.ok, data: data }; }); })
      .then(function (result) {
        if (!result.ok) {
          transcript.textContent = (result.data && result.data.detail) || "Voice note failed.";
          return;
        }
        if (!result.data.transcript) {
          transcript.textContent = "No speech heard.";
          return;
        }
        var placed = applyFormFill(result.data.formFill, targetField || null);
        var extra = fillStatus(placed);
        if (targetField) {
          var current = targetField.value || "";
          var next = current.trim() ? current.replace(/\s*$/, " ") + result.data.transcript : result.data.transcript;
          setNgValue(targetField, next);
          transcript.textContent = extra ? "Written. " + extra : "Written.";
          return;
        }
        var fill = result.data.formFill || {};
        if (noteBox) {
          noteBox.querySelectorAll("textarea").forEach(function (box) {
            if (box.dataset.field === "subjective") box.value = result.data.transcript;
            else if (box.dataset.field === "assessment") box.value = (fill.diagnoses || []).join(", ");
            else if (box.dataset.field === "plan") box.value = fill.plan || "";
            else box.value = "";
          });
        }
        var written = writeTranscriptToBahmniNote(result.data.transcript);
        if (written || (placed.written && placed.written.length)) {
          transcript.textContent = (written ? "Written into Chief Complaint: " : "Spoken: ") + result.data.transcript + (extra ? " " + extra : "");
          return;
        }
        savePending(uuid, result.data.transcript, fill);
        openVisitForm(uuid);
        transcript.textContent = "This page is the summary, so Bahmni has nowhere to store that sentence. Opening the visit form. It will go into Chief Complaint. Then press Bahmni Save. " + result.data.transcript;
      })
      .catch(function () { transcript.textContent = "Voice note failed."; });
  }

  function attachFieldMics() {
    var fields = document.querySelectorAll('textarea[ng-model="observation.value"], input[type="text"][ng-model="observation.value"]');
    Array.prototype.forEach.call(fields, function (field) {
      if (field.closest && field.closest("#medimind-side")) return;
      if (field.getAttribute("data-mm-mic")) return;
      if (field.offsetParent === null) return;
      field.setAttribute("data-mm-mic", "1");
      var btn = el("button", "medimind-field-mic", "Record");
      btn.type = "button";
      var status = el("span", "medimind-field-status", "");
      btn.addEventListener("click", function (event) {
        event.preventDefault();
        event.stopPropagation();
        toggleRecording(btn, status, null, field);
      });
      if (field.parentNode) field.parentNode.insertBefore(status, field.nextSibling);
      if (field.parentNode) field.parentNode.insertBefore(btn, field.nextSibling);
    });
  }

  function sync() {
    build();
    attachFieldMics();
    flushPending();
    var uuid = patientUuid();
    var root = document.getElementById("medimind-side");
    root.style.display = "block";
    if (!uuid) {
      if (pollTimer) {
        clearTimeout(pollTimer);
        pollTimer = null;
      }
      if (currentUuid) {
        currentUuid = "";
        clearPanel("Open a patient chart");
      }
      return;
    }
    if (uuid !== currentUuid) {
      if (pollTimer) {
        clearTimeout(pollTimer);
        pollTimer = null;
      }
      clearPanel("Loading…");
      window.__mmAssessedUuid = "";
      // Always load chart summary when a patient dashboard opens (Wave B visibility)
      if (root._mm && root._mm.setOpen) root._mm.setOpen(true);
      else {
        root.classList.add("open");
        var panel = root.querySelector(".medimind-side-panel");
        if (panel) panel.removeAttribute("hidden");
        document.body.classList.add("medimind-side-open");
      }
      load(false);
    }
  }

  window.addEventListener("hashchange", sync);
  window.setInterval(sync, 1500);
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", sync);
  else sync();
})();
