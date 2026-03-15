<script lang="ts">
import { page } from "$app/stores";
import { goto } from "$app/navigation";
import { marked } from "marked";
import { onMount } from "svelte";

export let data;

let documentData = data.documentData;

let documentId: string | null = null;
$: documentId = $page.params.id ?? null;

let loading = false;
let error: string | null = null;

let pdfContainer: HTMLDivElement | null = null;
let previewRendered = false;
let isExpanded = false;

$: chatEnabled =
  documentData?.status === "processed" &&
  documentData?.summary_status === "completed";

function toggleExpand() {
  isExpanded = !isExpanded;
}

type DocumentResponse = {
  id: number;
  filename: string;
  status: string;
  summary_status?: string;
  embedding_status?: string;
  created_at: string;
  clause_analysis?: Record<string, any[]>;
  analysis_confidence?: number;
  summary?: string;
};

let overallScore = 0;
let exposureLevel = "";
let riskPosture = "";
let summaryText = "";

async function loadSummary(id: string) {
  const res = await fetch(
    `${import.meta.env.VITE_API_URL}/documents/${id}/local-summary`
  );

  const data = await res.json();

  if (data.status === "completed") {
    summaryText = data.summary;
    overallScore = data.overall_score;
    exposureLevel = data.exposure_level;
    riskPosture = data.risk_posture;
  }
}

async function renderPDFPreview(id: string) {
  if (!pdfContainer) return;

  pdfContainer.innerHTML = "";

  const pdfjs = await import("pdfjs-dist");
  const worker = await import("pdfjs-dist/build/pdf.worker?url");

  pdfjs.GlobalWorkerOptions.workerSrc = worker.default;

  const loadingTask = pdfjs.getDocument(
    `${import.meta.env.VITE_API_URL}/documents/${id}/file`
  );

  const pdf = await loadingTask.promise;

  const scale = 1.3;

  for (let pageNum = 1; pageNum <= pdf.numPages; pageNum++) {
    const page = await pdf.getPage(pageNum);
    const viewport = page.getViewport({ scale });

    const canvas = document.createElement("canvas");
    const context = canvas.getContext("2d");
    if (!context) continue;

    canvas.width = viewport.width;
    canvas.height = viewport.height;

    canvas.style.width = "100%";
    canvas.style.height = "auto";
    canvas.style.marginBottom = "20px";

    await page.render({
      canvas,
      viewport
    }).promise;

    pdfContainer.appendChild(canvas);
  }
}

function goToRisk() {
  if (documentId) {
    goto(`/risk/${documentId}`);
  }
}

function openChat() {
  if (documentId) {
    goto(`/team?documentId=${documentId}`);
  }
}

function getTotalClauses(): number {
  if (!documentData?.clause_analysis) return 0;

  const values = Object.values(documentData.clause_analysis) as any[][];
  return values.reduce((acc, arr) => acc + arr.length, 0);
}

function calculateRiskScore(): number {
  if (!documentData?.clause_analysis) return 0;

  let score = 0;

  for (const category in documentData.clause_analysis) {
    const count = documentData.clause_analysis[category].length;

    if (category === "Liability") score += count * 10;
    else if (category === "Liquidated Damages") score += count * 8;
    else if (category === "Non-Compete") score += count * 7;
    else score += count * 3;
  }

  return Math.min(score, 100);
}

function getExposureClass(level: string) {
  if (level.includes("High")) return "risk-high";
  if (level.includes("Moderate")) return "risk-moderate";
  return "risk-low";
}

function formatStatus(value?: string): string {
  if (!value) return "Pending";
  return value.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

onMount(async () => {
  if (!documentId) return;

  const interval = setInterval(async () => {
    const res = await fetch(`${import.meta.env.VITE_API_URL}/documents/${documentId}`);
    documentData = await res.json();

    await loadSummary(documentId);

    if (summaryText) {
      clearInterval(interval);
    }
  }, 3000);
});

$: if (documentData && documentId && pdfContainer && !previewRendered) {
  previewRendered = true;
  renderPDFPreview(documentId);
}
</script>

{#if loading}
  <div class="panel-strong p-8">Loading document...</div>
{:else if error}
  <div class="panel-strong p-8 text-red-700">{error}</div>
{:else if documentData}
  <div class="doc-page space-y-5">
    <section class="panel doc-top p-6">
      <div>
        <p class="kicker">Contract Profile</p>
        <h1>Document Overview</h1>
        <p class="subtitle">{documentData.filename}</p>
        <div class="doc-meta">
          <span class="meta-pill">Doc: {formatStatus(documentData.status)}</span>
          <span class="meta-pill">Summary: {formatStatus(documentData.summary_status)}</span>
          <span class="meta-pill">Embeddings: {formatStatus(documentData.embedding_status)}</span>
        </div>
      </div>
      <button class="btn btn-ghost" on:click={() => goto('/documents')}>Back to Documents</button>
    </section>

    <section class="doc-grid">
      <article class="panel-strong p-5 space-y-4">
        <header class="summary-head">
          <h3>AI Summary</h3>
          {#if summaryText}
            <div class="risk-chip-wrap">
              <div class="risk-score">{overallScore}</div>
              <div>
                <div class={`risk-level ${getExposureClass(exposureLevel)}`}>{exposureLevel}</div>
                <div class="risk-posture">{riskPosture}</div>
              </div>
            </div>
          {/if}
        </header>

        <div class="summary-box">
          {#if summaryText}
            <div class="summary-content">{@html marked(summaryText)}</div>
          {:else}
            <div class="summary-loading">
              <p>Generating AI summary...</p>
              <div class="skeleton" style="height: 10px; width: 84%; margin-top: 10px;"></div>
              <div class="skeleton" style="height: 10px; width: 92%; margin-top: 8px;"></div>
              <div class="skeleton" style="height: 10px; width: 76%; margin-top: 8px;"></div>
            </div>
          {/if}
        </div>
      </article>

      <aside class="side-stack">
        <article class="panel-strong pdf-card {isExpanded ? 'expanded' : ''}">
          <div class="pdf-header">
            <h3>PDF Preview</h3>
            <button class="btn btn-ghost" on:click={toggleExpand}>
              {isExpanded ? "Exit Focus" : "Focus Mode"}
            </button>
          </div>
          <div class="pdf-preview-container">
            <div bind:this={pdfContainer}></div>
          </div>
        </article>

        <article class="panel-strong p-5">
          <h3 class="mb-4">Key Risk Snapshot</h3>
          <div class="risk-metrics">
            <div>
              <span>Risk Score</span>
              <strong>{calculateRiskScore()}</strong>
            </div>
            <div>
              <span>Confidence</span>
              <strong>{documentData.analysis_confidence ?? 0}%</strong>
            </div>
            <div>
              <span>Clauses</span>
              <strong>{getTotalClauses()}</strong>
            </div>
          </div>

          <div class="risk-meter-wrap">
            <div class="risk-meter-label">
              <span>Portfolio Exposure Index</span>
              <strong>{calculateRiskScore()}%</strong>
            </div>
            <div class="risk-meter">
              <div class="risk-meter-fill" style={`width: ${calculateRiskScore()}%`}></div>
            </div>
          </div>

          <div class="button-row">
            <button class="btn btn-primary" on:click={goToRisk}>View Risk Analysis</button>
            <button class="btn btn-ghost" on:click={openChat} disabled={!chatEnabled}>Chat With Document</button>
          </div>
        </article>
      </aside>
    </section>
  </div>
{/if}

<style>
.doc-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  background: linear-gradient(130deg, rgba(14, 164, 107, 0.13), rgba(32, 149, 232, 0.11));
}

.kicker {
  margin: 0;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  font-size: 0.74rem;
  font-weight: 700;
  color: #0c6e49;
}

.doc-top h1 {
  margin: 8px 0 4px;
  font-size: clamp(1.5rem, 2vw, 2.2rem);
}

.subtitle {
  margin: 0;
  color: #4f6269;
}

.doc-meta {
  margin-top: 10px;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.meta-pill {
  border-radius: 999px;
  border: 1px solid rgba(17, 34, 40, 0.12);
  background: rgba(255, 255, 255, 0.76);
  color: #35505a;
  font-size: 0.73rem;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  padding: 4px 9px;
}

.doc-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.6fr) minmax(320px, 1fr);
  gap: 16px;
  align-items: start;
}

.summary-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.summary-head h3 {
  margin: 0;
}

.risk-chip-wrap {
  display: flex;
  align-items: center;
  gap: 10px;
}

.risk-score {
  min-width: 60px;
  text-align: center;
  font-weight: 800;
  font-size: 1.35rem;
  padding: 10px;
  border-radius: 12px;
  background: rgba(17, 34, 40, 0.08);
}

.summary-box {
  border: 1px solid rgba(17, 34, 40, 0.08);
  border-radius: 14px;
  background: linear-gradient(180deg, rgba(255, 255, 255, 1), rgba(247, 250, 251, 1));
  min-height: 240px;
  padding: 14px;
}

.summary-loading {
  color: #647880;
}

.side-stack {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.pdf-card {
  padding: 14px;
  background: linear-gradient(160deg, rgba(255, 255, 255, 0.96), rgba(242, 250, 251, 0.9));
}

.pdf-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.pdf-header h3 {
  margin: 0;
}

:global(.pdf-preview-container) {
  height: 70vh;
  overflow-y: auto;
  overflow-x: hidden;
  border-radius: 12px;
  border: 1px solid rgba(17, 34, 40, 0.12);
  background: rgba(255, 255, 255, 0.92);
  padding: 16px;
}

:global(.pdf-preview-container canvas) {
  max-width: 900px;
  width: 100%;
}

.pdf-card.expanded {
  position: fixed;
  inset: 20px;
  z-index: 999;
  box-shadow: 0 28px 60px rgba(9, 24, 32, 0.32);
}

.pdf-card.expanded .pdf-preview-container {
  height: calc(100vh - 140px);
}

.risk-metrics {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
  margin-bottom: 12px;
}

.risk-metrics div {
  border: 1px solid rgba(17, 34, 40, 0.08);
  border-radius: 12px;
  background: #fff;
  padding: 10px;
}

.risk-metrics span {
  display: block;
  color: #6a7d83;
  font-size: 0.77rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.risk-metrics strong {
  font-size: 1.15rem;
}

.risk-meter-wrap {
  border: 1px solid rgba(17, 34, 40, 0.09);
  border-radius: 12px;
  background: #fff;
  padding: 10px;
  margin-bottom: 12px;
}

.risk-meter-label {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  font-size: 0.84rem;
  color: #4e656e;
}

.risk-meter-label strong {
  color: #153642;
  font-size: 0.92rem;
}

.risk-meter {
  height: 10px;
  border-radius: 999px;
  background: rgba(17, 34, 40, 0.1);
  overflow: hidden;
}

.risk-meter-fill {
  height: 100%;
  border-radius: inherit;
  background: linear-gradient(90deg, #13b47f, #2d95f2, #d14b5f);
}

.button-row {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

:global(.summary-content) {
  font-size: 0.96rem;
  line-height: 1.72;
  color: #1b313a;
}

:global(.summary-content h2) {
  font-size: 1.1rem;
  margin-top: 18px;
  margin-bottom: 8px;
}

:global(.summary-content p) {
  margin: 0 0 10px;
}

:global(.summary-content ul) {
  margin: 0 0 10px 18px;
}

.risk-level {
  font-size: 0.9rem;
  font-weight: 700;
}

.risk-posture {
  color: #63767d;
  font-size: 0.82rem;
}

:global(.risk-high) { color: #a92a3d; }
:global(.risk-moderate) { color: #9a5a0f; }
:global(.risk-low) { color: #0d724b; }

@media (max-width: 1100px) {
  .doc-grid {
    grid-template-columns: 1fr;
  }

  .pdf-card {
    order: 1;
  }
}

@media (max-width: 680px) {
  .doc-top {
    flex-direction: column;
    align-items: flex-start;
  }

  .risk-metrics {
    grid-template-columns: 1fr;
  }
}
</style>
