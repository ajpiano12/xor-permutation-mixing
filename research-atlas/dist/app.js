(() => {
  "use strict";
  const {branches, topics, sources} = window.ATLAS;
  const topicById = new Map(topics.map(topic => [topic.id, topic]));
  const sourceById = new Map(sources.map(source => [source.id, source]));
  const branchById = new Map(branches.map(branch => [branch.id, branch]));
  const statuses = [...new Set(topics.map(topic => topic.status))];
  const provenanceOrder = ["Published", "Corollary", "Project derivation", "Project experiment", "Open question"];
  const provenanceNotes = {
    Published: "A linked publication establishes the underlying result.",
    Corollary: "The result follows here by applying cited published results.",
    "Project derivation": "A proof developed in this project. Each topic records its prior-art review and any remaining question of priority.",
    "Project experiment": "Measurements made in this project, with links to the data and method.",
    "Open question": "A question still under investigation."
  };
  const branchTopics = id => topics.filter(topic => topic.branch === id);
  const primary = topicById.get("three-bit-census") || topics[0];
  const tree = document.getElementById("tree");
  const inspector = document.getElementById("inspector");
  const search = document.getElementById("search");
  const filter = document.getElementById("filter");
  const library = document.getElementById("library-list");
  const progress = document.getElementById("progress-list");
  const expanded = new Set([primary.branch]);
  const foldedMatches = new Set();
  let selected = primary;
  let activeView;
  let libraryType = "All";
  let latestNavigation = "";

  const glyphs = {
    tree: '<rect x="2.5" y="3" width="6" height="5.5" rx="1.4"/><rect x="15.5" y="2" width="6" height="5.5" rx="1.4"/><rect x="15.5" y="15.5" width="6" height="5.5" rx="1.4"/><path d="M8.5 5.7h3a2 2 0 0 1 2 2v8.7a2 2 0 0 0 2 2M12 5.7h3.5"/>',
    model: '<path d="m3 8 9-4 9 4-9 4-9-4Zm1 5 8 3.6 8-3.6M4 17.5l8 3.6 8-3.6"/>',
    counts: '<path d="M4 20V13m5 7V8m5 12V4m5 16v-9"/>',
    structure: '<circle cx="6" cy="7" r="2.7"/><circle cx="18" cy="6" r="2.7"/><circle cx="13" cy="18" r="2.7"/><path d="m8.7 7 6.5-.7M7.5 9.3l4.1 6.3m5.2-7.1-2.7 7.1"/>',
    algorithms: '<path d="m8 6-5 6 5 6m8-12 5 6-5 6m-3-14-2 16"/>',
    chevron: '<path d="m9 5.5 6.5 6.5L9 18.5"/>',
    file: '<path d="M6 3h8l4.5 4.5V20H6z"/><path d="M14 3v5h4M9 12h6m-6 4h6"/>',
    book: '<path d="M12 6.5C9 4.3 6 4 3 5.3v13c3-1.3 6-1 9 1.2 3-2.2 6-2.5 9-1.2v-13c-3-1.3-6-1-9 1.2Zm0 0v13"/>',
    data: '<ellipse cx="12" cy="6" rx="8" ry="3"/><path d="M4 6v12c0 1.7 3.6 3 8 3s8-1.3 8-3V6M4 12c0 1.7 3.6 3 8 3s8-1.3 8-3"/>',
    figure: '<rect x="3" y="4" width="18" height="16" rx="2"/><path d="m4 17 5-5 4 3 4-6 3 3"/>',
    check: '<path d="m5.5 12.5 4.4 4.3L18.7 8"/>',
    open: '<circle cx="12" cy="12" r="6.5"/>',
    search: '<circle cx="10" cy="10" r="6"/><path d="m15 15 5 5"/>'
  };
  function icon(name, className = "") {
    return '<svg class="ui-icon ' + className + '" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.65" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' + (glyphs[name] || glyphs.file) + '</svg>';
  }
  function esc(value) {
    return String(value ?? "").replace(/[&<>"']/g, ch => ({"&":"&amp;", "<":"&lt;", ">":"&gt;", '"':"&quot;", "'":"&#39;"})[ch]);
  }
  function token(s) { return String(s).toLowerCase().replace(/[^a-z0-9]+/g, "-"); }
  function routeToTopic(id) { return "#topic/" + encodeURIComponent(id); }
  function safeHref(value) {
    const text = String(value ?? "");
    if (!text || /^[\s]*\/\//.test(text) || /[\\\x00-\x1f]/.test(text)) return "";
    if (/^[a-z][a-z0-9+.-]*:/i.test(text) && !/^https?:\/\//i.test(text)) return "";
    return text;
  }
  function statusBadge(status) {
    return '<span class="status-badge status-' + token(status) + '"><span class="status-mark" aria-hidden="true"></span>' + esc(status) + '</span>';
  }
  function linkIcon(kind) {
    return ({Code:"algorithms", Data:"data", Figure:"figure", Paper:"book"})[kind] || "file";
  }
  function resourceLink(resource, className = "source-link") {
    const href = safeHref(resource.href);
    if (!href) return "";
    return '<a class="' + className + '" href="' + esc(href) + '"><span class="resource-icon">' + icon(linkIcon(resource.kind)) + '</span><span class="source-text"><span class="source-name">' + esc(resource.label) + '</span><span class="source-type">' + esc(resource.kind) + '</span></span></a>';
  }
  function paperIds(topic) { return (topic.sourceIds || []).map(id => sourceById.get(id)).filter(Boolean); }
  function matchTopic(topic, query, status) {
    return (!status || topic.status === status) && (!query || [
      topic.title, topic.summary, topic.provenance, topic.status, topic.attribution,
      branchById.get(topic.branch)?.title, ...(topic.body || []), ...paperIds(topic).map(s => s.title)
    ].join(" ").toLowerCase().includes(query));
  }
  function node(topic) {
    const current = topic.id === selected.id;
    return '<a class="topic-node' + (current ? ' selected' : '') + '" href="' + esc(routeToTopic(topic.id)) + '" data-topic="' + esc(topic.id) + '"' + (current ? ' aria-current="true"' : '') + '><span class="topic-mark mark-' + token(topic.status) + '" aria-hidden="true"></span><span class="node-text"><span class="node-title">' + esc(topic.title) + '</span><span class="node-meta">' + esc(topic.status) + '</span></span>' + icon("chevron", "node-chevron") + '</a>';
  }
  function drawTree() {
    const query = search.value.trim().toLowerCase();
    const status = statuses.includes(filter.value) ? filter.value : "";
    const isFiltering = Boolean(query || status);
    const rows = [];
    let count = 0;
    for (const branch of branches) {
      const matches = branchTopics(branch.id).filter(topic => matchTopic(topic, query, status));
      if (!matches.length) continue;
      count += matches.length;
      const open = isFiltering ? !foldedMatches.has(branch.id) : expanded.has(branch.id);
      rows.push('<div class="tree-branch" data-branch="' + esc(branch.id) + '"><button class="branch-heading" type="button" data-toggle="' + esc(branch.id) + '" aria-expanded="' + open + '" aria-controls="children-' + esc(branch.id) + '"><span class="branch-icon">' + icon(branch.id) + '</span><span class="branch-name">' + esc(branch.title) + '</span><span class="branch-count" aria-label="' + matches.length + ' topics">' + matches.length + '</span>' + icon("chevron", "chevron") + '</button><div class="branch-topics" id="children-' + esc(branch.id) + '"' + (open ? '' : ' hidden') + '>' + matches.map(node).join("") + '</div></div>');
    }
    const root = '<div class="tree-root"><span class="root-icon">' + icon("tree") + '</span><span class="root-text"><span class="root-title">t-wise mixing</span><span class="root-caption">' + topics.length + ' research topics</span></span></div>';
    tree.innerHTML = root + '<div class="tree-branches">' + rows.join("") + '</div>' + (!count ? '<div class="empty-state">No topics match your filters. <button type="button" data-clear-search>Clear filters</button></div>' : "");
    const result = document.getElementById("search-count");
    if (result) result.textContent = isFiltering ? count + (count === 1 ? " matching topic" : " matching topics") : "";
  }
  function drawInspector() {
    const topic = selected, branch = branchById.get(topic.branch);
    const metric = topic.metric;
    const papers = paperIds(topic);
    const resources = topic.resources || [];
    const evidence = resources.map(resource => resourceLink(resource)).join("");
    const paperHTML = papers.map(s => resourceLink({label:s.title, kind:"Paper", href:s.url})).join("");
    inspector.setAttribute("tabindex", "-1");
    inspector.innerHTML = '<div class="detail-kicker"><span class="detail-branch-icon">' + icon(topic.branch) + '</span>' + esc(branch.title) + '</div>' +
      '<h2 class="detail-title">' + esc(topic.title) + '</h2>' +
      '<div class="detail-badges">' + statusBadge(topic.status) + '<span class="provenance-badge">' + esc(topic.provenance) + '</span></div>' +
      '<p class="detail-summary">' + esc(topic.summary) + '</p>' +
      (metric ? '<div class="detail-metric"><span class="metric-value">' + esc(metric.value) + '</span><span class="metric-label">' + esc(metric.label) + '</span></div>' : "") +
      (evidence ? '<section class="detail-section"><h3>Proofs and evidence</h3><div class="source-list">' + evidence + '</div></section>' : "") +
      ((topic.body || []).length ? '<details class="detail-explanation"><summary>Explanation ' + icon("chevron", "chevron") + '</summary><div>' + topic.body.map(p => '<p>' + esc(p) + '</p>').join("") + '</div></details>' : "") +
      '<section class="detail-attribution"><h3>Attribution</h3><p>' + esc(topic.attribution) + '</p>' + (paperHTML ? '<div class="source-list">' + paperHTML + '</div>' : '') + '</section>';
  }

  function libraryRows() {
    const byHref = new Map();
    for (const topic of topics) {
      for (const item of topic.resources || []) {
        if (!safeHref(item.href)) continue;
        let row = byHref.get(item.href);
        if (!row) {
          row = {...item, topics:[]};
          byHref.set(item.href, row);
        }
        if (!row.topics.includes(topic)) row.topics.push(topic);
      }
    }
    return [...byHref.values()];
  }
  function drawLibrary() {
    const resources = libraryRows();
    const papers = sources.map(s => ({href:s.url, label:s.title, kind:"Paper", meta:[s.authors, s.year].filter(Boolean).join(" · "), note:s.note, topics:topics.filter(t => (t.sourceIds || []).includes(s.id))}));
    const all = [...resources, ...papers];
    const kinds = ["Proof", "Notes", "Code", "Data", "Figure", "Paper"].filter(k => all.some(item => item.kind === k));
    const plural = {Proof:"Proofs", Notes:"Notes", Code:"Code", Data:"Data", Figure:"Figures", Paper:"Published sources"};
    const groups = kinds.filter(kind => libraryType === "All" || libraryType === kind).map(kind => {
      const entries = all.filter(r => r.kind === kind);
      return '<section class="library-group" id="library-' + token(kind) + '"><h3>' + esc(plural[kind] || kind) + ' <span class="group-count">' + entries.length + '</span></h3>' + entries.map(item => {
        const related = item.topics.map(topic => '<a href="' + esc(routeToTopic(topic.id)) + '">' + esc(topic.title) + '</a>').join('<span aria-hidden="true"> · </span>');
        return '<article class="library-row">' + resourceLink(item) + (item.meta ? '<p class="library-meta">' + esc(item.meta) + '</p>' : "") + (item.note ? '<p class="library-note">' + esc(item.note) + '</p>' : "") + (related ? '<div class="linked-topics"><span>Topics </span>' + related + '</div>' : "") + '</article>';
      }).join("") + '</section>';
    });
    library.innerHTML = '<div class="view-toolbar"><label for="library-kind">Resource type</label><select id="library-kind"><option value="All">All resources</option>' + kinds.map(k => '<option value="' + esc(k) + '"' + (k === libraryType ? " selected" : "") + '>' + esc(plural[k]) + '</option>').join("") + '</select></div>' + groups.join("");
  }
  function drawProgress(byAttribution) {
    const key = byAttribution ? "provenance" : "status";
    const groups = byAttribution ? [...new Set([...provenanceOrder, ...topics.map(t => t.provenance)])] : ["Open", ...statuses.filter(s => s !== "Open")];
    const order = groups.filter(name => topics.some(t => t[key] === name));
    const counts = new Map(order.map(name => [name, topics.filter(t => t[key] === name)]));
    const base = byAttribution ? "#progress/attribution/" : "#progress/";
    progress.innerHTML = '<div class="view-toolbar"><label for="progress-grouping">Group by</label><select id="progress-grouping"><option value="status">Research status</option><option value="attribution"' + (byAttribution ? ' selected' : '') + '>Attribution</option></select></div>' +
      '<div class="progress-summary">' + order.map(name => '<a href="' + base + token(name) + '" class="progress-stat"><strong>' + counts.get(name).length + '</strong><span>' + esc(name) + '</span></a>').join("") + '</div>' +
      order.map(name => '<section class="progress-group" id="progress-' + token(name) + '"><h3>' + esc(name === "Open" ? "Open questions" : name) + '</h3>' + (byAttribution && provenanceNotes[name] ? '<p class="group-note">' + esc(provenanceNotes[name]) + '</p>' : '') + counts.get(name).map(topic => '<a class="progress-topic" href="' + esc(routeToTopic(topic.id)) + '"><span><span class="node-title">' + esc(topic.title) + '</span><span class="node-meta">' + esc(branchById.get(topic.branch).title) + ' · ' + esc(byAttribution ? topic.status : topic.provenance) + '</span></span>' + icon("chevron", "node-chevron") + '</a>').join("") + '</section>').join("");
  }
  function navigate() {
    let route;
    try { route = decodeURIComponent(location.hash.slice(1)); } catch { route = ""; }
    // The native skip link targets the current main landmark in every view.
    if (route === "workspace" && activeView) return;
    const [routeName, id, subgroup] = route.split("/");
    const view = routeName === "library" || routeName === "progress" ? routeName : "map";
    const topic = routeName === "topic" ? topicById.get(id) : undefined;
    const hadView = Boolean(activeView);
    if (topic) {
      selected = topic;
      expanded.add(topic.branch);
      if (!matchTopic(topic, search.value.trim().toLowerCase(), statuses.includes(filter.value) ? filter.value : "")) {
        search.value = "";
        filter.selectedIndex = 0;
      }
      foldedMatches.delete(topic.branch);
    }
    for (const section of ["map", "library", "progress"]) {
      document.getElementById("app-" + section).hidden = section !== view;
    }
    for (const el of document.querySelectorAll("nav a[data-view]")) {
      const active = el.dataset.view === view;
      el.classList.toggle("active", active);
      if (active) el.setAttribute("aria-current", "page");
      else el.removeAttribute("aria-current");
    }
    document.body.dataset.view = view;
    // Redraw once per navigation. Reuse the active node as the keyboard focus target.
    const focusWasInTree = tree.contains(document.activeElement);
    if (view === "map") {
      drawTree();
      drawInspector();
      if (topic && window.matchMedia("(max-width: 800px)").matches) {
        requestAnimationFrame(() => { inspector.focus({preventScroll:true}); inspector.scrollIntoView({block:"start"}); });
      } else if (focusWasInTree && topic) {
        tree.querySelector('[aria-current="true"]')?.focus({preventScroll:true});
      } else if (hadView && activeView !== view) {
        document.getElementById("app-map").scrollIntoView({block:"start"});
      }
    } else if (view === "library") {
      drawLibrary();
    } else {
      const byAttribution = id === "attribution";
      const focusedGrouping = document.activeElement?.id === "progress-grouping";
      drawProgress(byAttribution);
      if (focusedGrouping) document.getElementById("progress-grouping")?.focus({preventScroll:true});
      const group = byAttribution ? subgroup : id;
      if (group) requestAnimationFrame(() => document.getElementById("progress-" + group)?.scrollIntoView({block:"start"}));
    }
    if (hadView && activeView !== view && view !== "map" && !id) window.scrollTo(0,0);
    document.title = (topic ? topic.title : view === "library" ? "Proof library" : view === "progress" ? "Research progress" : "Research map") + " · Difference Atlas";
    activeView = view;
    latestNavigation = location.hash;
  }

  filter.innerHTML = '<option value="">All statuses</option>' + statuses.map(s => '<option value="' + esc(s) + '">' + esc(s) + '</option>').join("");
  function updateFilter() { foldedMatches.clear(); drawTree(); }
  search.addEventListener("input", updateFilter);
  filter.addEventListener("change", updateFilter);
  tree.addEventListener("click", event => {
    const toggle = event.target.closest("button[data-toggle]");
    if (toggle) {
      const id = toggle.dataset.toggle;
      const filtering = Boolean(search.value.trim() || statuses.includes(filter.value));
      const remembered = filtering ? foldedMatches : expanded;
      if (remembered.has(id)) remembered.delete(id);
      else remembered.add(id);
      drawTree();
      tree.querySelector('button[data-toggle="' + id + '"]')?.focus({preventScroll:true});
    } else if (event.target.closest("[data-clear-search]")) {
      search.value = "";
      filter.selectedIndex = 0;
      updateFilter();
      search.focus();
    } else if (event.target.closest(".topic-node")?.hash === latestNavigation && window.matchMedia("(max-width: 800px)").matches) {
      inspector.focus({preventScroll:true});
      inspector.scrollIntoView({block:"start"});
    }
  });
  library.addEventListener("change", event => {
    if (event.target.id === "library-kind") {
      libraryType = event.target.value;
      drawLibrary();
      document.getElementById("library-kind").focus({preventScroll:true});
    }
  });
  progress.addEventListener("change", event => {
    if (event.target.id === "progress-grouping") location.hash = event.target.value === "attribution" ? "#progress/attribution" : "#progress";
  });
  window.addEventListener("hashchange", navigate);
  navigate();
})();
