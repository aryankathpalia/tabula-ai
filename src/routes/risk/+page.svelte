<script lang="ts">
  import { onMount } from "svelte";
  import { goto } from "$app/navigation";

  type DocumentItem = {
    id: number;
    filename: string;
    status: string;
    analysis_confidence?: number;
    clause_analysis?: Record<string, any[]>;
    created_at: string;
  };

  let documents: DocumentItem[] = [];
  let loading = true;
  let error: string | null = null;

  function calculateRiskScore(analysis?: Record<string, any[]>) {
    if (!analysis) return 0;

    let score = 0;

    for (const category in analysis) {
      const count = analysis[category]?.length || 0;

      if (category === "Liability") score += count * 10;
      else if (category === "Liquidated Damages") score += count * 8;
      else if (category === "Non-Compete") score += count * 7;
      else score += count * 3;
    }

    return Math.min(score, 100);
  }

  onMount(async () => {
    try {
      const res = await fetch(`${import.meta.env.VITE_API_URL}/documents/`);
      if (!res.ok) throw new Error("Failed to fetch documents");

      documents = await res.json();
    } catch (err: any) {
      error = err?.message || "Unknown error";
    } finally {
      loading = false;
    }
  });

  function openRisk(id: number) {
    goto(`/risk/${id}`);
  }

  async function handleQuickUpload(event: Event) {
    const input = event.target as HTMLInputElement;
    const file = input.files?.[0];
    if (!file) return;

    const tempId = Date.now();

    const tempDoc: DocumentItem = {
      id: tempId,
      filename: file.name,
      status: "processing",
      created_at: new Date().toISOString(),
      clause_analysis: {},
      analysis_confidence: 0
    };

    documents = [tempDoc, ...documents];

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch(`${import.meta.env.VITE_API_URL}/documents/`, {
        method: "POST",
        body: formData
      });

      if (!res.ok) throw new Error("Upload failed");

      const data = await res.json();

      documents = documents.map(doc =>
        doc.id === tempId ? data : doc
      );

      setTimeout(() => {
        goto(`/risk/${data.id}`);
      }, 800);
    } catch (err) {
      console.error("Quick upload failed", err);
    }
  }
</script>

<div class="risk-page space-y-5">
  <section class="panel risk-hero p-6 md:p-8">
    <div class="space-y-3 max-w-3xl">
      <p class="hero-kicker">Exposure Monitoring</p>
      <h1>Risk Analysis Overview</h1>
      <p>Monitor processed contracts, detect concentration of risk, and inspect evidence in one continuous workspace.</p>
      <div class="max-w-2xl" data-tour="search">
        <input
          type="text"
          placeholder="Search documents, risks, clauses..."
          class="field"
          on:keydown={(e) => e.key === 'Enter' && (window.location.href = '/search')}
        />
      </div>
    </div>

    <label class="btn btn-primary upload">
      Quick Upload
      <input
        type="file"
        accept=".pdf,.docx,.txt"
        class="hidden"
        on:change={handleQuickUpload}
      />
    </label>
  </section>

  {#if loading}
    <div class="panel-strong p-8">
      <div class="skeleton load-head"></div>
      <div class="skeleton load-row"></div>
      <div class="skeleton load-row"></div>
      <div class="skeleton load-row"></div>
    </div>
  {:else if error}
    <div class="panel-strong p-8 text-center text-red-700">{error}</div>
  {:else}
    <section class="panel-strong table-shell">
      <header>
        <h3>Risk Queue</h3>
        <span>{documents.length} documents</span>
      </header>

      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Document</th>
              <th>Status</th>
              <th>Risk Score</th>
              <th>Confidence</th>
              <th>Created</th>
            </tr>
          </thead>

          <tbody>
            {#each documents as doc}
              <tr on:click={() => openRisk(doc.id)}>
                <td class="filename">{doc.filename}</td>
                <td>
                  <span class="pill" class:low={doc.status === 'processed'} class:moderate={doc.status === 'processing'}>
                    {doc.status}
                    {#if doc.status === "processing"}
                      <span class="spinner"></span>
                    {/if}
                  </span>
                </td>
                <td>{calculateRiskScore(doc.clause_analysis)}</td>
                <td>{doc.analysis_confidence ?? 0}%</td>
                <td>{new Date(doc.created_at).toLocaleDateString()}</td>
              </tr>
            {/each}
          </tbody>
        </table>
      </div>
    </section>
  {/if}
</div>

<style>
.risk-hero {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: flex-end;
  background: linear-gradient(120deg, rgba(14, 164, 107, 0.14), rgba(32, 149, 232, 0.1));
}

.hero-kicker {
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.11em;
  color: #0b6f49;
  font-weight: 700;
}

.risk-hero h1 {
  margin: 0;
  font-size: clamp(1.8rem, 2.4vw, 2.6rem);
}

.risk-hero p {
  margin: 0;
  color: #556870;
}

.upload {
  white-space: nowrap;
}

.table-shell {
  padding: 16px;
}

.table-shell header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.table-shell h3 {
  margin: 0;
}

.table-shell header span {
  color: #607279;
  font-size: 0.82rem;
}

.table-wrap {
  overflow: auto;
  max-height: 70vh;
  border-radius: 14px;
  border: 1px solid rgba(17, 34, 40, 0.1);
}

table {
  width: 100%;
  border-collapse: collapse;
  background: #fff;
}

th {
  text-align: left;
  font-size: 0.74rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: #65787f;
  padding: 12px;
  position: sticky;
  top: 0;
  background: #f8fbfc;
}

td {
  padding: 12px;
  border-top: 1px solid rgba(17, 34, 40, 0.07);
  font-size: 0.91rem;
}

.filename {
  font-weight: 700;
}

tbody tr {
  cursor: pointer;
  transition: background 0.2s ease;
}

tbody tr:hover {
  background: #f5fbf9;
}

.spinner {
  margin-left: 7px;
  width: 11px;
  height: 11px;
  border: 2px solid #d7b165;
  border-top: 2px solid transparent;
  border-radius: 50%;
  display: inline-block;
  animation: spin 0.85s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@media (max-width: 780px) {
  .risk-hero {
    flex-direction: column;
    align-items: flex-start;
  }
}

.load-head {
  width: 30%;
  height: 22px;
  margin-bottom: 12px;
}

.load-row {
  width: 100%;
  height: 58px;
  margin-bottom: 10px;
}
</style>
