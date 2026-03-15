<script lang="ts">
  import { page } from "$app/stores";
  import { goto } from "$app/navigation";

  let pdfContainer: HTMLDivElement | null = null;

type ClauseItem = {
  clause_text: string;
  confidence: number;
  page: number | null;
  bbox: {
    x: number;
    y: number;
    width: number;
    height: number;
  } | null;
};

  type ClauseAnalysis = {
    [category: string]: ClauseItem[];
  };

  type DocumentResponse = {
    id: number;
    filename: string;
    clause_analysis?: ClauseAnalysis;
    analysis_confidence?: number;
  };

  let documentId: string | null = null;
  let documentData: DocumentResponse | null = null;
  let loading = false;
  let error: string | null = null;

  let riskScore = 0;
  let confidence = 0;
  let selectedClauseId: string | null = null;

  let lastLoadedId: string | null = null;

  let pdfjsLib: any;
  let workerInitialized = false;
  let pdfRendered = false;
  let renderedPdf: any = null;
  let pageWrappers: Map<number, HTMLDivElement> = new Map();

  let openCategories: Set<string> = new Set();

  function toggleCategory(category: string) {
    if (openCategories.has(category)) {
      openCategories.delete(category);
    } else {
      openCategories.add(category);
    }
    openCategories = new Set(openCategories);
  }

  $: documentId = $page.params.id ?? null;

  $: if (documentId && documentId !== lastLoadedId) {
    loadDocument(documentId);
  }

async function initPDFJS() {
  if (workerInitialized) return;

  const pdfjs = await import("pdfjs-dist");
  const worker = await import("pdfjs-dist/build/pdf.worker?url");

  pdfjsLib = pdfjs;
  pdfjsLib.GlobalWorkerOptions.workerSrc = worker.default;
  workerInitialized = true;
}

  async function loadDocument(id: string) {
    loading = true;
    error = null;
    pdfRendered = false;

    try {
      await initPDFJS();

      const res = await fetch(`${import.meta.env.VITE_API_URL}/documents/${id}`);
      if (!res.ok) throw new Error("Failed to fetch document");

      documentData = await res.json();
      lastLoadedId = id;

      if (documentData?.clause_analysis) {
        riskScore = calculateRiskScore(documentData.clause_analysis);
        confidence = documentData.analysis_confidence ?? 0;
      }
    } catch (err: any) {
      error = err?.message || "Unknown error";
    } finally {
      loading = false;
    }
  }

  $: if (!loading && documentData && pdfContainer && !pdfRendered) {
    renderPDF(documentData.id);
  }

async function renderPDF(id: number) {
  if (!pdfContainer || !pdfjsLib) return;

  pdfRendered = true;
  pageWrappers.clear();

  const url = `${import.meta.env.VITE_API_URL}/documents/${id}/file`;
  const loadingTask = pdfjsLib.getDocument(url);
  renderedPdf = await loadingTask.promise;

  pdfContainer.innerHTML = "";

  const scale = 1.6;

  for (let pageNum = 1; pageNum <= renderedPdf.numPages; pageNum++) {
    const page = await renderedPdf.getPage(pageNum);
    const viewport = page.getViewport({ scale });

    const wrapper = document.createElement("div");
    wrapper.style.position = "relative";
    wrapper.style.marginBottom = "24px";
    wrapper.style.width = `${viewport.width}px`;
    wrapper.style.height = `${viewport.height}px`;
    wrapper.style.margin = "0 auto 24px auto";

    pageWrappers.set(pageNum, wrapper);

    const canvas = document.createElement("canvas");
    const context = canvas.getContext("2d");
    if (!context) continue;

    canvas.width = viewport.width;
    canvas.height = viewport.height;

    canvas.style.width = `${viewport.width}px`;
    canvas.style.height = `${viewport.height}px`;
    canvas.style.display = "block";

    await page.render({
      canvasContext: context,
      viewport
    }).promise;

    wrapper.appendChild(canvas);
    pdfContainer.appendChild(wrapper);
  }

  await renderClauseOverlays();
}

async function renderClauseOverlays() {
  if (!documentData || !renderedPdf) return;

  const scale = 1.6;

  for (const category of Object.values(documentData.clause_analysis || {})) {
    for (const clause of category) {
      if (!clause.page || !clause.bbox) continue;

      const wrapper = pageWrappers.get(clause.page);
      if (!wrapper) continue;

      const page = await renderedPdf.getPage(clause.page);
      const viewport = page.getViewport({ scale });

      const rect = viewport.convertToViewportRectangle([
        clause.bbox.x,
        clause.bbox.y,
        clause.bbox.x + clause.bbox.width,
        clause.bbox.y + clause.bbox.height
      ]);

      const overlay = document.createElement("div");
      overlay.className = "block-highlight";

      const uniqueId = `${clause.page}-${clause.bbox.x}-${clause.bbox.y}`;
      overlay.dataset.id = uniqueId;

      overlay.style.position = "absolute";
      overlay.style.left = `${Math.min(rect[0], rect[2])}px`;
      overlay.style.top = `${Math.min(rect[1], rect[3])}px`;
      overlay.style.width = `${Math.abs(rect[2] - rect[0])}px`;
      overlay.style.height = `${Math.abs(rect[3] - rect[1])}px`;

      wrapper.appendChild(overlay);
    }
  }
}

function scrollToClause(clause: ClauseItem) {
  if (!clause.page || !clause.bbox) return;

  const uniqueId = `${clause.page}-${clause.bbox.x}-${clause.bbox.y}`;
  selectedClauseId = uniqueId;

  document.querySelectorAll(".block-highlight")
    .forEach(el => el.classList.remove("selected-block-highlight"));

  const selected = document.querySelector(`[data-id="${uniqueId}"]`);

  if (selected) {
    selected.classList.add("selected-block-highlight");
    selected.scrollIntoView({
      behavior: "smooth",
      block: "center"
    });
  }
}

  function getTotalClauses(): number {
    if (!documentData?.clause_analysis) return 0;
    return Object.values(documentData.clause_analysis)
      .reduce((acc, arr) => acc + arr.length, 0);
  }

  function calculateRiskScore(analysis: ClauseAnalysis): number {
    let score = 0;
    for (const category in analysis) {
      const count = analysis[category].length;
      if (category === "Liability") score += count * 10;
      else if (category === "Liquidated Damages") score += count * 8;
      else if (category === "Non-Compete") score += count * 7;
      else score += count * 3;
    }
    return Math.min(score, 100);
  }

  function riskBandClass(score: number): string {
    if (score >= 70) return "critical";
    if (score >= 40) return "elevated";
    return "controlled";
  }

  function riskBandLabel(score: number): string {
    if (score >= 70) return "Critical Exposure";
    if (score >= 40) return "Elevated Exposure";
    return "Controlled Exposure";
  }

  function clausePreview(text: string): string {
    const cleaned = text.replace(/\s+/g, " ").trim();
    return cleaned.length > 84 ? `${cleaned.slice(0, 84)}...` : cleaned;
  }
</script>

{#if loading}
  <div class="panel-strong p-8 text-center">Loading document...</div>
{:else if error}
  <div class="panel-strong p-8 text-center text-red-700">{error}</div>
{:else if documentData}
<div class="risk-detail space-y-4">
  <section class="panel p-6 risk-detail-head">
    <div>
      <p class="kicker">Evidence Mode</p>
      <h1>Risk Analysis</h1>
      <p class="subtitle">{documentData?.filename ?? "No document selected"}</p>
    </div>

    <div class="header-actions">
      <button class="btn btn-ghost" on:click={() => goto('/risk')}>Back to Risk Analysis</button>
    </div>
  </section>

  <section class="risk-grid">
    <div class="panel-strong pdf-viewer">
      <div class="pdf-toolbar">
        <span class="legend"><i></i> Clause overlays</span>
        <span class="legend selected"><i></i> Selected clause</span>
      </div>
      <div bind:this={pdfContainer} class="pdf-scroll"></div>
    </div>

    <aside class="risk-panel">
      <div class="panel-strong card stat-card">
        <span class="score">{riskScore}</span>
        <div class={`risk-tone ${riskBandClass(riskScore)}`}>{riskBandLabel(riskScore)}</div>
        <div class="confidence">Analysis Confidence: {confidence}%</div>
        <div class="confidence-bar">
          <span style={`width: ${Math.min(100, Math.max(0, confidence))}%`}></span>
        </div>
      </div>

      <div class="panel-strong card clauses">
        <h3>Detected Clauses ({getTotalClauses()})</h3>

        {#if documentData?.clause_analysis}
          {#each Object.entries(documentData.clause_analysis) as [category, clauses]}
            <div class="accordion-item">
              <button class="accordion-header" on:click={() => toggleCategory(category)}>
                <span class="accordion-left">
                  <span class="chevron {openCategories.has(category) ? 'open' : ''}">▸</span>
                  <span class="category-name">{category}</span>
                </span>

                <span class="badge">{clauses.length}</span>
              </button>

              {#if openCategories.has(category)}
                <div class="accordion-body">
                  {#each clauses as clause, index}
                    <button
                      class="clause-link"
                      class:active={selectedClauseId === `${clause.page}-${clause.bbox?.x}-${clause.bbox?.y}`}
                      on:click={() => scrollToClause(clause)}
                    >
                      <strong>Clause {index + 1}</strong>
                      <span>{clausePreview(clause.clause_text)}</span>
                    </button>
                  {/each}
                </div>
              {/if}
            </div>
          {/each}
        {/if}
      </div>
    </aside>
  </section>
</div>
{/if}

<style>
.risk-detail-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 14px;
  background: linear-gradient(130deg, rgba(14, 164, 107, 0.14), rgba(32, 149, 232, 0.11));
}

.kicker {
  margin: 0;
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  font-weight: 700;
  color: #0d6f4a;
}

.risk-detail-head h1 {
  margin: 6px 0 2px;
}

.subtitle {
  margin: 0;
  color: #5f7279;
}

.risk-grid {
  display: grid;
  grid-template-columns: minmax(0, 2fr) minmax(320px, 1fr);
  gap: 16px;
  align-items: start;
}

.risk-panel {
  display: flex;
  flex-direction: column;
  gap: 12px;
  position: sticky;
  top: 14px;
}

.card {
  padding: 14px;
}

.stat-card {
  text-align: center;
}

.score {
  font-size: 2.6rem;
  font-weight: 800;
  color: #b52d41;
}

.confidence {
  margin-top: 6px;
  color: #607279;
}

.risk-tone {
  margin-top: 4px;
  font-size: 0.8rem;
  font-weight: 700;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

.risk-tone.critical { color: #a92a3d; }
.risk-tone.elevated { color: #995610; }
.risk-tone.controlled { color: #0d724b; }

.confidence-bar {
  margin-top: 9px;
  height: 8px;
  border-radius: 999px;
  background: rgba(17, 34, 40, 0.11);
  overflow: hidden;
}

.confidence-bar span {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: linear-gradient(90deg, #14b07c, #2f95f1);
}

.pdf-viewer {
  padding: 14px;
  height: 84vh;
  overflow: hidden;
}

.pdf-toolbar {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  font-size: 0.75rem;
  color: #4f656e;
  margin-bottom: 8px;
}

.legend {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.legend i {
  width: 10px;
  height: 10px;
  border-radius: 3px;
  background: rgba(14, 164, 107, 0.2);
}

.legend.selected i {
  background: rgba(223, 62, 85, 0.28);
}

.pdf-scroll {
  height: 100%;
  overflow-y: auto;
  overflow-x: auto;
  border: 1px solid rgba(17, 34, 40, 0.1);
  border-radius: 12px;
  background: #fff;
  padding: 12px;
}

:global(.pdf-scroll canvas) {
  display: block;
  margin: 0 auto 16px auto;
}

.clauses h3 {
  margin: 0 0 10px;
}

.accordion-item {
  border-top: 1px solid rgba(17, 34, 40, 0.1);
  padding: 8px 0;
}

.accordion-header {
  display: flex;
  width: 100%;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
  padding: 8px 0;
  border: none;
  background: transparent;
  text-align: left;
}

.accordion-left {
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.badge {
  border-radius: 999px;
  background: rgba(17, 34, 40, 0.07);
  color: #3d525b;
  padding: 2px 8px;
  font-size: 0.78rem;
}

.accordion-body {
  padding: 0 0 8px 22px;
  display: grid;
  gap: 4px;
}

.clause-link {
  border: 1px solid transparent;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.75);
  text-align: left;
  padding: 8px 9px;
  color: #29474f;
  cursor: pointer;
  display: grid;
  gap: 3px;
}

.clause-link:hover {
  border-color: rgba(17, 34, 40, 0.15);
  background: #fff;
}

.clause-link strong {
  color: #0f6f4b;
  font-size: 0.83rem;
}

.clause-link span {
  color: #5d747c;
  font-size: 0.79rem;
  line-height: 1.45;
}

.clause-link.active {
  border-color: rgba(223, 62, 85, 0.4);
  background: rgba(223, 62, 85, 0.08);
}

.chevron {
  display: inline-block;
  transition: transform 0.2s ease;
  color: #607179;
}

.chevron.open {
  transform: rotate(90deg);
}

:global(.block-highlight) {
  background: rgba(14, 164, 107, 0.2);
  border-radius: 6px;
  pointer-events: none;
  box-sizing: border-box;
}

:global(.selected-block-highlight) {
  background: rgba(223, 62, 85, 0.28);
  border-radius: 6px;
  box-shadow: 0 0 0 2px rgba(223, 62, 85, 0.35);
}

@media (max-width: 980px) {
  .risk-grid {
    grid-template-columns: 1fr;
  }

  .risk-panel {
    position: static;
  }

  .pdf-viewer {
    height: 70vh;
  }
}

@media (max-width: 720px) {
  .risk-detail-head {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
