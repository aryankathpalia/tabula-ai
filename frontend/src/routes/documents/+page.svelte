<script lang="ts">
  import { goto } from "$app/navigation";
  import { onMount } from "svelte";
  import Trash2 from "lucide-svelte/icons/trash-2";
  import { browser } from "$app/environment";

type DocumentItem = {
  id: number;
  filename: string;
  status: string;
  summary_status?: string;
  analysis_confidence?: number;
  created_at: string;
};

  let documents: DocumentItem[] = [];
  let loadingDocs = false;

  async function loadDocs() {
      try {
        loadingDocs = true;
        const res = await fetch(`${import.meta.env.VITE_API_URL}/documents/`);

        if (!res.ok) {
          console.error("Failed to fetch documents");
          return;
        }

        documents = await res.json();
      } catch (err) {
        console.error("Fetch error:", err);
      } finally {
        loadingDocs = false;
      }
    }

    onMount(() => {
      if (!browser) return;
      loadDocs();
    });

  let selectedFile: File | null = null;
  let uploading = false;
  let error: string | null = null;

  async function uploadDocument() {
    if (!selectedFile) {
      error = "Please select a file first.";
      return;
    }

    uploading = true;
    error = null;

    const formData = new FormData();
    formData.append("file", selectedFile);

    try {
      const res = await fetch(`${import.meta.env.VITE_API_URL}/documents/`, {
        method: "POST",
        body: formData
      });

      if (!res.ok) throw new Error("Upload failed");

      const data = await res.json();

      documents = [
        {
          id: data.id,
          filename: selectedFile!.name,
          status: "processing",
          created_at: new Date().toISOString()
        },
        ...documents
      ];

      selectedFile = null;
      waitForProcessing(data.id);
    } catch (err: any) {
      error = err.message || "Upload failed.";
    } finally {
      uploading = false;
    }
  }

  function handleFileChange(event: Event) {
    const input = event.target as HTMLInputElement;
    selectedFile = input.files?.[0] || null;
  }

  async function deleteDocument(id: number) {
    try {
      const res = await fetch(`${import.meta.env.VITE_API_URL}/documents/${id}`, {
        method: "DELETE"
      });

      if (!res.ok) throw new Error("Delete failed");
      documents = documents.filter(doc => doc.id !== id);
    } catch (err) {
      console.error("Delete failed", err);
      alert("Failed to delete document");
    }
  }

  async function waitForProcessing(documentId: number) {
    const interval = setInterval(async () => {
      const res = await fetch(`${import.meta.env.VITE_API_URL}/documents/${documentId}`);
      if (!res.ok) return;

      const doc = await res.json();

      documents = documents.map(d =>
        d.id === doc.id ? doc : d
      );

      if (doc.summary_status === "completed") {
        clearInterval(interval);
        goto(`/documents/${documentId}`);
      }
    }, 3000);
  }
</script>

<div class="space-y-6 docs-page">
  <section class="panel docs-hero p-6 md:p-8">
    <div class="space-y-4 max-w-3xl">
      <p class="hero-kicker">Legal Ingestion Pipeline</p>
      <h1 class="hero-title">Document Intelligence Workspace</h1>
      <p class="hero-copy">
        Upload agreements and let Tabula AI classify clauses, compute exposure, and prepare legal summaries.
      </p>
      <div class="max-w-2xl" data-tour="search">
        <input
          type="text"
          placeholder="Search documents, risks, clauses..."
          class="field"
          on:keydown={(e) => e.key === 'Enter' && (window.location.href = '/search')}
        />
      </div>
    </div>
  </section>

  <section class="panel-strong upload-panel" data-tour="upload">
    <div class="upload-grid">
      <div>
        <h2>Drop files to initiate risk assessment</h2>
        <p>Supports PDF, DOCX, and TXT files up to 50MB.</p>
      </div>

      <div class="upload-actions">
        <input
          type="file"
          accept=".pdf,.docx,.txt"
          class="hidden"
          id="fileInput"
          on:change={handleFileChange}
        />

        <label for="fileInput" class="btn btn-ghost">Browse Files</label>

        <button
          on:click={uploadDocument}
          disabled={uploading}
          class="btn btn-primary"
        >
          {uploading ? "Processing..." : "Upload & Analyze"}
        </button>
      </div>
    </div>

    {#if selectedFile}
      <p class="file-picked">Selected: <strong>{selectedFile.name}</strong></p>
    {/if}

    {#if error}
      <p class="file-error">{error}</p>
    {/if}
  </section>

  <section class="panel-strong docs-table">
    <header>
      <h3>Previously Uploaded Documents</h3>
      <span>{documents.length} total</span>
    </header>

    {#if loadingDocs}
      <div class="placeholder skeleton-list">
        <div class="skeleton row-skeleton"></div>
        <div class="skeleton row-skeleton"></div>
        <div class="skeleton row-skeleton"></div>
      </div>
    {:else if documents.length === 0}
      <div class="placeholder">No documents uploaded yet.</div>
    {:else}
      <div class="rows">
        {#each documents as doc}
          <div
            class="row"
            role="button"
            tabindex="0"
            on:click={() => goto(`/documents/${doc.id}`)}
            on:keydown={(e) => e.key === "Enter" && goto(`/documents/${doc.id}`)}
          >
            <div>
              <p class="filename">{doc.filename}</p>
              <p class="date">{new Date(doc.created_at).toLocaleDateString()}</p>
            </div>

            <div class="row-actions">
              <span class="pill" class:low={doc.status === 'processed'} class:moderate={doc.status !== 'processed'}>
                {doc.status === "processing" ? "Processing..." : "Processed"}
              </span>

              {#if doc.analysis_confidence}
                <span class="confidence">{doc.analysis_confidence.toFixed(2)}%</span>
              {/if}

              <button
                class="trash"
                on:click|stopPropagation={() => deleteDocument(doc.id)}
              >
                <Trash2 size={16} stroke-width={1.8} />
              </button>
            </div>
          </div>
        {/each}
      </div>
    {/if}
  </section>
</div>

<style>
.docs-hero {
  background:
    linear-gradient(120deg, rgba(14, 164, 107, 0.14), rgba(32, 149, 232, 0.12)),
    rgba(255, 255, 255, 0.7);
}

.hero-kicker {
  font-size: 0.74rem;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  color: #0d6f4a;
  font-weight: 700;
}

.hero-title {
  margin: 0;
  font-size: clamp(1.8rem, 2.4vw, 2.7rem);
}

.hero-copy {
  margin: 0;
  color: #4f6269;
  max-width: 58ch;
}

.upload-panel {
  padding: 18px;
  border: 1px dashed rgba(14, 164, 107, 0.42);
}

.upload-grid {
  display: flex;
  justify-content: space-between;
  gap: 20px;
  align-items: center;
  flex-wrap: wrap;
}

.upload-grid h2 {
  margin: 0;
  font-size: 1.2rem;
}

.upload-grid p {
  margin: 4px 0 0;
  color: #607179;
}

.upload-actions {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.file-picked {
  margin: 10px 0 0;
  color: #1d333c;
}

.file-error {
  margin: 10px 0 0;
  color: #b52d41;
  font-weight: 700;
}

.docs-table {
  padding: 16px;
}

.docs-table header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.docs-table h3 {
  margin: 0;
  font-size: 1.02rem;
}

.docs-table header span {
  color: #66797f;
  font-size: 0.82rem;
}

.rows {
  max-height: 500px;
  overflow-y: auto;
  display: grid;
  gap: 8px;
  padding-right: 4px;
}

.row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  padding: 12px;
  border-radius: 14px;
  border: 1px solid rgba(17, 34, 40, 0.08);
  background: #fff;
  transition: all 0.2s ease;
}

.row:hover {
  transform: translateY(-1px);
  box-shadow: 0 10px 24px rgba(11, 30, 40, 0.12);
}

.filename {
  margin: 0;
  font-weight: 700;
}

.date {
  margin: 2px 0 0;
  color: #607179;
  font-size: 0.82rem;
}

.row-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.confidence {
  color: #61737a;
  font-size: 0.82rem;
}

.trash {
  display: grid;
  place-items: center;
  width: 33px;
  height: 33px;
  border: 1px solid rgba(17, 34, 40, 0.15);
  border-radius: 10px;
  background: #fff;
  color: #5d7178;
}

.placeholder {
  padding: 18px;
  color: #66797f;
}

.skeleton-list {
  display: grid;
  gap: 10px;
}

.row-skeleton {
  height: 62px;
}

@media (max-width: 740px) {
  .row {
    flex-direction: column;
    align-items: flex-start;
  }

  .row-actions {
    width: 100%;
    justify-content: flex-end;
  }
}
</style>
