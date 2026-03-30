<script lang="ts">
  type ComparisonResult = {
    documents: string[];
    comparison: Record<string, Record<string, string>>;
    grouped: any;
  };

  type EntityItem = {
    type?: string;
    value?: string;
  };

  type InsightsResult = {
    doc_scores: Record<string, number>;
    entities: Record<string, EntityItem[]>;
    verdict: string;
  };

  type EntityGroupKey = "financial" | "percentage" | "duration" | "other";

  let fileA: File | null = null;
  let fileB: File | null = null;
  let files: File[] = [];

  let result: ComparisonResult | null = null;
  let insights: InsightsResult | null = null;

  let loading = false;
  let loadingInsights = false;
  let error: string | null = null;

  let dragA = false;
  let dragB = false;
  let loadingStep = 0;
  let loadingTimer: ReturnType<typeof setInterval> | null = null;

  const loadingSteps = [
    "Extracting text",
    "Identifying clauses",
    "Analyzing risk posture",
    "Generating AI insights"
  ];

  const featureCards = [
    {
      title: "Risk Detection",
      description: "Surface asymmetric liability, indemnity, and termination exposure before signing."
    },
    {
      title: "Clause Comparison",
      description: "View side-by-side legal language deltas by clause category and context."
    },
    {
      title: "Financial Insights",
      description: "Extract values, percentages, and duration terms for instant commercial review."
    },
    {
      title: "AI Verdict",
      description: "Get an executive-grade recommendation with document-level risk scoring."
    }
  ];

  function syncFiles() {
    files = [fileA, fileB].filter(Boolean) as File[];
  }

  function shortName(name: string) {
    return name.length > 36 ? `${name.slice(0, 32)}...` : name;
  }

  function setFile(slot: "a" | "b", file: File | null) {
    if (slot === "a") {
      fileA = file;
    } else {
      fileB = file;
    }
    error = null;
    syncFiles();
  }

  function handleFilePick(slot: "a" | "b", event: Event) {
    const input = event.target as HTMLInputElement;
    setFile(slot, input.files?.[0] ?? null);
  }

  function handleDrop(slot: "a" | "b", event: DragEvent) {
    event.preventDefault();
    if (slot === "a") dragA = false;
    if (slot === "b") dragB = false;
    setFile(slot, event.dataTransfer?.files?.[0] ?? null);
  }

  function startLoadingProgress() {
    stopLoadingProgress();
    loadingStep = 0;
    loadingTimer = setInterval(() => {
      loadingStep = Math.min(loadingStep + 1, loadingSteps.length - 1);
    }, 900);
  }

  function stopLoadingProgress() {
    if (!loadingTimer) return;
    clearInterval(loadingTimer);
    loadingTimer = null;
  }

  function safeText(value: string | undefined) {
    return value?.trim() || "-";
  }

  function hasClauseDifference(values: string[]) {
    const normalized = values.map((v) => v.trim().toLowerCase()).filter(Boolean);
    if (normalized.length <= 1) return false;
    return new Set(normalized).size > 1;
  }

  function maxRiskScore() {
    if (!insights) return 0;
    const scores = Object.values(insights.doc_scores ?? {});
    return scores.length ? Math.max(...scores) : 0;
  }

  function verdictTone(score: number) {
    if (score >= 75) {
      return {
        badge: "High Risk",
        card: "from-rose-600 to-red-700",
        ring: "ring-rose-200",
        text: "text-rose-50"
      };
    }
    if (score >= 45) {
      return {
        badge: "Moderate Risk",
        card: "from-amber-500 to-orange-600",
        ring: "ring-amber-200",
        text: "text-amber-50"
      };
    }
    return {
      badge: "Low Risk",
      card: "from-emerald-600 to-green-700",
      ring: "ring-emerald-200",
      text: "text-emerald-50"
    };
  }

  function scoreBarClass(score: number) {
    if (score >= 75) return "bg-rose-500";
    if (score >= 45) return "bg-amber-500";
    return "bg-emerald-500";
  }

  function groupFromEntity(entity: EntityItem): EntityGroupKey {
    const type = (entity.type || "").toLowerCase();
    const value = entity.value || "";

    const isFinancial =
      /money|amount|payment|price|fee|cost|currency|financial|total|budget|liability/.test(type) ||
      /[$€£]|\b(?:usd|eur|gbp|inr|million|billion|m|k)\b/i.test(value);
    if (isFinancial) return "financial";

    const isPercentage = /percent|percentage|rate|interest/.test(type) || /\d+(?:\.\d+)?\s?%/.test(value);
    if (isPercentage) return "percentage";

    const isDuration =
      /duration|term|notice|period|renewal|deadline|date/.test(type) ||
      /\b\d+\s?(?:day|days|month|months|year|years|week|weeks)\b/i.test(value);
    if (isDuration) return "duration";

    return "other";
  }

  function groupedEntities(doc: string) {
    const labels: Record<EntityGroupKey, string> = {
      financial: "Financial",
      percentage: "Percentage",
      duration: "Duration",
      other: "Other"
    };

    const source = (insights?.entities?.[doc] ?? []).slice(0, 14);
    const grouped: Record<EntityGroupKey, EntityItem[]> = {
      financial: [],
      percentage: [],
      duration: [],
      other: []
    };

    source.forEach((entity) => {
      grouped[groupFromEntity(entity)].push(entity);
    });

    return (Object.keys(grouped) as EntityGroupKey[])
      .map((key) => ({
        key,
        label: labels[key],
        items: grouped[key].slice(0, 4)
      }))
      .filter((section) => section.items.length > 0);
  }

  async function upload() {
    if (files.length < 2) {
      error = "Upload both documents to continue";
      return;
    }

    loading = true;
    error = null;
    result = null;
    insights = null;
    startLoadingProgress();

    const formData = new FormData();
    files.forEach((f) => formData.append("files", f));

    try {
      const res = await fetch("http://localhost:8000/compare/", {
        method: "POST",
        body: formData
      });

      if (!res.ok) throw new Error("Comparison request failed");

      const data = await res.json();
      result = data;

      if (!data) return;

      loadingInsights = true;

      const insightsRes = await fetch("http://localhost:8000/compare/insights/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          grouped: data.grouped,
          documents: data.documents
        })
      });

      if (!insightsRes.ok) throw new Error("Insights request failed");

      insights = await insightsRes.json();
    } catch (e) {
      error = "Failed to compare documents. Please try again.";
    } finally {
      loading = false;
      loadingInsights = false;
      stopLoadingProgress();
    }
  }
</script>

<div class="compare-page page-wrap px-1 pb-10 pt-1">
  <section class="panel compare-hero p-6 md:p-8 lg:p-10">
    <div class="mx-auto max-w-4xl space-y-4 text-center">
      <p class="kicker">Contract Intelligence</p>
      <h1 class="hero-title">Contract Comparison</h1>
      <p class="hero-copy">
        Compare legal agreements side-by-side to uncover hidden risk, commercial deltas, and negotiation leverage in minutes.
      </p>
    </div>
  </section>

  <section class="panel-strong mt-6 p-5 md:p-6 lg:p-7">
    <div class="grid gap-4 md:grid-cols-2">
      <div
        class="upload-card"
        class:dragging={dragA}
        role="group"
        aria-label="Upload Document A"
        on:dragover|preventDefault={() => (dragA = true)}
        on:dragleave={() => (dragA = false)}
        on:drop={(event) => handleDrop("a", event)}
      >
        <div class="space-y-2">
          <p class="upload-title">Upload Document A</p>
          <p class="upload-hint">PDF, DOCX up to 50MB</p>
        </div>

        <label class="upload-action" for="docAInput">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true">
            <path d="M12 16V4"></path>
            <path d="m7 9 5-5 5 5"></path>
            <path d="M20 16.6A4.6 4.6 0 0 1 15.4 21H8.2A5.2 5.2 0 0 1 8 10.6"></path>
          </svg>
          <span>{fileA ? "Replace file" : "Choose file"}</span>
        </label>

        <input id="docAInput" class="hidden" type="file" accept=".pdf,.doc,.docx,.txt" on:change={(event) => handleFilePick("a", event)} />

        <p class="file-name">{fileA ? shortName(fileA.name) : "No file selected"}</p>
      </div>

      <div
        class="upload-card"
        class:dragging={dragB}
        role="group"
        aria-label="Upload Document B"
        on:dragover|preventDefault={() => (dragB = true)}
        on:dragleave={() => (dragB = false)}
        on:drop={(event) => handleDrop("b", event)}
      >
        <div class="space-y-2">
          <p class="upload-title">Upload Document B</p>
          <p class="upload-hint">PDF, DOCX up to 50MB</p>
        </div>

        <label class="upload-action" for="docBInput">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true">
            <path d="M12 16V4"></path>
            <path d="m7 9 5-5 5 5"></path>
            <path d="M20 16.6A4.6 4.6 0 0 1 15.4 21H8.2A5.2 5.2 0 0 1 8 10.6"></path>
          </svg>
          <span>{fileB ? "Replace file" : "Choose file"}</span>
        </label>

        <input id="docBInput" class="hidden" type="file" accept=".pdf,.doc,.docx,.txt" on:change={(event) => handleFilePick("b", event)} />

        <p class="file-name">{fileB ? shortName(fileB.name) : "No file selected"}</p>
      </div>
    </div>

    <div class="mt-5 flex flex-col items-center gap-3">
      <button class="btn btn-primary compare-cta" on:click={upload} disabled={loading || files.length < 2}>
        {loading ? "Analyzing Contracts..." : "Compare Contracts"}
      </button>

      {#if error}
        <p class="text-sm font-semibold text-[#b52d41]">{error}</p>
      {/if}
    </div>
  </section>

  {#if loading}
    <section class="panel-strong mt-6 p-6 md:p-7 fade-soft">
      <div class="grid gap-6 lg:grid-cols-[1.2fr_1fr]">
        <div class="space-y-4">
          <p class="loading-label">Processing comparison pipeline</p>
          <div class="space-y-3">
            {#each loadingSteps as step, index}
              <div class="loading-step" class:active={index <= loadingStep}>
                <span class="step-dot"></span>
                <span>{step}</span>
              </div>
            {/each}
          </div>
        </div>

        <div class="grid grid-cols-2 gap-3">
          <div class="skeleton h-16"></div>
          <div class="skeleton h-16"></div>
          <div class="skeleton col-span-2 h-32"></div>
          <div class="skeleton col-span-2 h-20"></div>
        </div>
      </div>
    </section>
  {/if}

  {#if !result && !loading}
    <section class="mt-6 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
      {#each featureCards as feature}
        <article class="panel-strong feature-card p-5">
          <h3>{feature.title}</h3>
          <p>{feature.description}</p>
        </article>
      {/each}
    </section>

    <section class="panel-strong mt-6 p-5 md:p-6 lg:p-7">
      <div class="mb-5 flex flex-wrap items-center justify-between gap-3">
        <div>
          <p class="kicker mb-1">Example Preview</p>
          <h2 class="preview-title">What your comparison will look like</h2>
        </div>
        <div class="preview-verdict">
          <p>AI Verdict</p>
          <strong>Document B carries higher negotiation risk</strong>
        </div>
      </div>

      <div class="grid gap-4 lg:grid-cols-[1.4fr_1fr]">
        <div class="table-shell">
          <table class="w-full text-left">
            <thead>
              <tr>
                <th>Clause</th>
                <th>Document A</th>
                <th>Document B</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>Liability Cap</td>
                <td>Limited to annual contract value</td>
                <td class="mock-diff">Limited to 3x annual contract value</td>
              </tr>
              <tr>
                <td>Payment Terms</td>
                <td>Net 30 days</td>
                <td class="mock-diff">Net 45 days with late fees</td>
              </tr>
              <tr>
                <td>Termination Notice</td>
                <td>30 days</td>
                <td class="mock-diff">60 days</td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="space-y-4">
          <article class="preview-card">
            <h4>Sample Risk Scores</h4>
            <div class="space-y-2 text-sm">
              <p class="score-row"><span>Document A</span><strong>38.2</strong></p>
              <p class="score-row"><span>Document B</span><strong>71.4</strong></p>
            </div>
          </article>

          <article class="preview-card">
            <h4>Sample Key Data</h4>
            <ul>
              <li><span>Financial</span><strong>$1,250,000 cap</strong></li>
              <li><span>Percentage</span><strong>8% late penalty</strong></li>
              <li><span>Duration</span><strong>36-month term</strong></li>
            </ul>
          </article>
        </div>
      </div>
    </section>
  {/if}

  {#if result}
    {@const score = maxRiskScore()}
    {@const tone = verdictTone(score)}

    <section class={`mt-6 rounded-2xl bg-gradient-to-r ${tone.card} p-6 text-white shadow-lg ring-1 ${tone.ring}`}>
      <div class="flex flex-wrap items-start justify-between gap-4">
        <div class="max-w-3xl space-y-2">
          <p class="text-[0.76rem] font-bold uppercase tracking-[0.12em] opacity-90">AI Verdict</p>
          <h2 class="text-2xl font-semibold md:text-3xl">
            {#if loadingInsights}
              Finalizing insights...
            {:else if insights}
              {insights.verdict}
            {:else}
              Verdict unavailable
            {/if}
          </h2>
          <p class="text-sm opacity-90">Risk classification: {tone.badge}</p>
        </div>

        <div class={`rounded-xl border border-white/30 bg-white/10 px-4 py-3 text-right ${tone.text}`}>
          <p class="text-xs font-semibold uppercase tracking-[0.08em] opacity-90">Risk Score</p>
          <p class="text-3xl font-bold leading-tight">{score.toFixed(1)}</p>
        </div>
      </div>
    </section>

    <section class="mt-4 grid gap-4 md:grid-cols-2">
      {#each result.documents as doc, idx}
        <article class="panel-strong p-5">
          <p class="kicker mb-2">Document {idx === 0 ? "A" : idx === 1 ? "B" : idx + 1}</p>
          <h3 class="doc-title">{shortName(doc)}</h3>
          <p class="text-sm text-[#556870]">Ready for clause-level review and risk benchmarking.</p>
        </article>
      {/each}
    </section>

    {#if insights}
      <section class="panel-strong mt-4 p-5 md:p-6">
        <div class="mb-4 flex items-center justify-between gap-3">
          <h3 class="section-title">Risk Scores by Document</h3>
          <span class="text-sm text-[#5a6a71]">Higher score indicates higher risk</span>
        </div>

        <div class="grid gap-3 md:grid-cols-2">
          {#each result.documents as doc}
            {@const docScore = insights.doc_scores?.[doc] ?? 0}
            <article class="score-card">
              <div class="mb-2 flex items-center justify-between gap-2">
                <p class="truncate font-semibold text-[#17343f]">{shortName(doc)}</p>
                <p class="text-sm font-bold text-[#17343f]">{docScore.toFixed(1)}</p>
              </div>
              <div class="h-2.5 rounded-full bg-[#e6edef]">
                <div class={`h-full rounded-full ${scoreBarClass(docScore)}`} style={`width: ${Math.max(3, Math.min(100, docScore))}%`}></div>
              </div>
            </article>
          {/each}
        </div>
      </section>
    {/if}

    <section class="panel-strong mt-4 overflow-hidden">
      <div class="border-b border-[rgba(17,34,40,0.08)] px-5 py-4 md:px-6">
        <h3 class="section-title">Clause Comparison Matrix</h3>
      </div>

      <div class="compare-table-wrap">
        <table class="compare-table">
          <thead>
            <tr>
              <th class="sticky-col">Clause</th>
              {#each result.documents as doc}
                <th>{shortName(doc)}</th>
              {/each}
            </tr>
          </thead>
          <tbody>
            {#each Object.entries(result.comparison) as [key, val], rowIndex}
              {@const values = result.documents.map((doc) => safeText(val[doc]))}
              {@const clauseDiff = hasClauseDifference(values)}
              <tr class:striped={rowIndex % 2 === 1}>
                <td class="sticky-col clause-name">{key}</td>
                {#each result.documents as doc}
                  <td class:diff-cell={clauseDiff}>{safeText(val[doc])}</td>
                {/each}
              </tr>
            {/each}
          </tbody>
        </table>
      </div>
    </section>

    {#if insights}
      <section class="mt-4 grid gap-4 lg:grid-cols-2">
        {#each result.documents as doc}
          <article class="panel-strong p-5 md:p-6">
            <div class="mb-4 flex items-center justify-between gap-3">
              <h3 class="section-title">Key Data: {shortName(doc)}</h3>
              <span class="text-xs font-semibold uppercase tracking-[0.08em] text-[#5a6a71]">Top entities</span>
            </div>

            {#if (insights.entities?.[doc] ?? []).length}
              <div class="divide-y divide-[rgba(17,34,40,0.08)] rounded-xl border border-[rgba(17,34,40,0.08)] bg-white/80">
                {#each (insights.entities?.[doc] ?? []).slice(0, 8) as ent}
                  {@const entity = ent as any}
                  <div class="p-3">
                    <div class="flex items-start justify-between gap-4">
                      <div class="min-w-0">
                        <p class="truncate font-medium text-[#163640]">{entity.type || "Entity"}</p>
                        <p class="text-xs text-gray-500">{entity.label || "Unlabeled"}</p>
                      </div>
                      <p class="max-w-[55%] break-words text-right font-semibold text-gray-900">{entity.value || "-"}</p>
                    </div>

                    {#if entity.parties?.length}
                      <p class="mt-1 text-xs text-gray-400">Parties: {entity.parties.join(", ")}</p>
                    {/if}
                  </div>
                {/each}
              </div>
            {:else}
              <p class="text-sm text-[#72858d]">No key data extracted</p>
            {/if}
          </article>
        {/each}
      </section>
    {/if}
  {/if}
</div>

<style>
  .compare-page {
    animation: fade-up 380ms ease;
  }

  .compare-hero {
    background:
      linear-gradient(125deg, rgba(14, 164, 107, 0.16), rgba(32, 149, 232, 0.12)),
      rgba(255, 255, 255, 0.7);
    position: relative;
    overflow: hidden;
  }

  .compare-hero::after {
    content: '';
    position: absolute;
    right: -84px;
    top: -88px;
    width: 280px;
    height: 280px;
    border-radius: 999px;
    background: radial-gradient(circle, rgba(32, 149, 232, 0.24), transparent 68%);
  }

  .kicker {
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.11em;
    font-weight: 700;
    color: #0b6f49;
  }

  .hero-title {
    margin: 0;
    font-size: clamp(2rem, 2.5vw, 2.85rem);
  }

  .hero-copy {
    margin: 0 auto;
    max-width: 62ch;
    color: #4b5f67;
    line-height: 1.6;
  }

  .upload-card {
    border: 1.5px dashed rgba(17, 34, 40, 0.2);
    border-radius: 16px;
    background: linear-gradient(180deg, rgba(255, 255, 255, 0.85), rgba(245, 251, 249, 0.8));
    padding: 16px;
    display: flex;
    min-height: 176px;
    flex-direction: column;
    justify-content: space-between;
    transition: border-color 0.2s ease, box-shadow 0.2s ease, transform 0.2s ease;
  }

  .upload-card:hover,
  .upload-card.dragging {
    transform: translateY(-1px);
    border-color: rgba(14, 164, 107, 0.56);
    box-shadow: 0 12px 26px rgba(10, 42, 31, 0.08);
  }

  .upload-title {
    margin: 0;
    font-weight: 700;
    color: #12343f;
  }

  .upload-hint {
    margin: 0;
    font-size: 0.84rem;
    color: #617279;
  }

  .upload-action {
    width: fit-content;
    display: inline-flex;
    align-items: center;
    gap: 8px;
    border-radius: 12px;
    border: 1px solid rgba(17, 34, 40, 0.12);
    background: rgba(255, 255, 255, 0.92);
    padding: 8px 12px;
    font-size: 0.88rem;
    font-weight: 700;
    color: #1f3b45;
    cursor: pointer;
  }

  .upload-action svg {
    width: 15px;
    height: 15px;
  }

  .file-name {
    margin: 0;
    font-size: 0.86rem;
    color: #5f7179;
    font-weight: 600;
  }

  .compare-cta {
    min-width: 230px;
  }

  .feature-card h3 {
    margin: 0;
    font-size: 1rem;
    color: #163640;
  }

  .feature-card p {
    margin: 10px 0 0;
    color: #5d7078;
    line-height: 1.5;
    font-size: 0.92rem;
  }

  .preview-title {
    margin: 0;
    font-size: 1.35rem;
    color: #163640;
  }

  .preview-verdict {
    border: 1px solid rgba(14, 164, 107, 0.25);
    border-radius: 12px;
    background: rgba(14, 164, 107, 0.08);
    padding: 10px 12px;
  }

  .preview-verdict p {
    margin: 0;
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 0.09em;
    font-weight: 700;
    color: #0d6f49;
  }

  .preview-verdict strong {
    color: #12343f;
    font-size: 0.9rem;
  }

  .table-shell {
    border: 1px solid rgba(17, 34, 40, 0.1);
    border-radius: 14px;
    overflow: hidden;
  }

  .table-shell table {
    border-collapse: collapse;
  }

  .table-shell th {
    background: rgba(244, 250, 248, 0.95);
    color: #17343f;
    font-size: 0.78rem;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    padding: 12px;
  }

  .table-shell td {
    padding: 12px;
    border-top: 1px solid rgba(17, 34, 40, 0.08);
    color: #42575f;
    font-size: 0.9rem;
  }

  .mock-diff {
    background: rgba(245, 158, 11, 0.1);
    color: #9a5a0f;
    font-weight: 600;
  }

  .preview-card {
    border: 1px solid rgba(17, 34, 40, 0.12);
    border-radius: 12px;
    background: rgba(255, 255, 255, 0.88);
    padding: 12px;
  }

  .preview-card h4 {
    margin: 0 0 8px;
    color: #153540;
  }

  .score-row {
    margin: 0;
    display: flex;
    justify-content: space-between;
    color: #4d626a;
  }

  .preview-card ul {
    margin: 0;
    padding: 0;
    list-style: none;
    display: grid;
    gap: 8px;
    font-size: 0.9rem;
  }

  .preview-card li {
    display: flex;
    justify-content: space-between;
    gap: 10px;
    border-top: 1px solid rgba(17, 34, 40, 0.09);
    padding-top: 8px;
  }

  .preview-card li:first-child {
    border-top: none;
    padding-top: 0;
  }

  .preview-card span {
    color: #5f7179;
  }

  .preview-card strong {
    color: #14343e;
  }

  .loading-label {
    margin: 0;
    font-size: 0.78rem;
    text-transform: uppercase;
    letter-spacing: 0.11em;
    color: #60737b;
    font-weight: 700;
  }

  .loading-step {
    display: flex;
    align-items: center;
    gap: 10px;
    color: #6d8087;
    font-weight: 600;
  }

  .loading-step.active {
    color: #18414d;
  }

  .step-dot {
    width: 10px;
    height: 10px;
    border-radius: 999px;
    border: 2px solid rgba(17, 34, 40, 0.28);
    transition: background-color 0.2s ease, border-color 0.2s ease;
  }

  .loading-step.active .step-dot {
    border-color: rgba(14, 164, 107, 0.8);
    background: rgba(14, 164, 107, 0.8);
  }

  .doc-title {
    margin: 0 0 8px;
    color: #143540;
    font-size: 1.08rem;
  }

  .section-title {
    margin: 0;
    font-size: 1.1rem;
    color: #153540;
  }

  .score-card {
    border: 1px solid rgba(17, 34, 40, 0.12);
    border-radius: 12px;
    background: rgba(255, 255, 255, 0.92);
    padding: 12px;
  }

  .compare-table-wrap {
    overflow-x: auto;
  }

  .compare-table {
    width: 100%;
    min-width: 720px;
    border-collapse: separate;
    border-spacing: 0;
  }

  .compare-table thead th {
    position: sticky;
    top: 0;
    z-index: 1;
    background: #f2f8f6;
    color: #163640;
    font-size: 0.78rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    text-align: left;
    padding: 12px;
    border-bottom: 1px solid rgba(17, 34, 40, 0.1);
  }

  .compare-table tbody td {
    padding: 12px;
    border-bottom: 1px solid rgba(17, 34, 40, 0.08);
    vertical-align: top;
    color: #45616a;
    font-size: 0.92rem;
  }

  .compare-table .striped td {
    background: rgba(246, 250, 251, 0.72);
  }

  .compare-table .sticky-col {
    position: sticky;
    left: 0;
    z-index: 2;
    background: #f8fcfb;
  }

  .compare-table .clause-name {
    color: #163640;
    font-weight: 700;
    min-width: 200px;
  }

  .compare-table .diff-cell {
    background: rgba(245, 158, 11, 0.09);
  }

  .group-title {
    margin: 0;
    font-size: 0.76rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #60737a;
    font-weight: 700;
  }

  .entity-row {
    border: 1px solid rgba(17, 34, 40, 0.09);
    border-radius: 10px;
    background: rgba(255, 255, 255, 0.82);
    padding: 9px 10px;
    display: flex;
    justify-content: space-between;
    gap: 8px;
    font-size: 0.88rem;
  }

  .entity-type {
    color: #67808a;
    text-transform: capitalize;
    flex: 0 0 36%;
  }

  .entity-value {
    color: #143540;
    font-weight: 600;
    text-align: right;
    flex: 1;
    overflow-wrap: anywhere;
  }

  @media (max-width: 768px) {
    .compare-page {
      padding-bottom: 24px;
    }

    .compare-cta {
      width: 100%;
    }

    .entity-row {
      flex-direction: column;
      align-items: flex-start;
    }

    .entity-value {
      text-align: left;
    }
  }
</style>