<script lang="ts">
  let query = '';
  let results: any[] = [];
  let loading = false;

  async function runSearch() {
    loading = true;
    try {
      const res = await fetch(`${import.meta.env.VITE_API_URL}/search/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, top_k: 10 })
      });

      const data = await res.json();
      results = data.results;
    } catch (err) {
      console.error(err);
    } finally {
      loading = false;
    }
  }
</script>

<div class="search-page space-y-5">
  <section class="panel p-6 md:p-8 search-hero">
    <p class="hero-kicker">Discovery Layer</p>
    <h1>Advanced Semantic Search</h1>
    <p>Search across contracts, policies, and legal text using natural language prompts.</p>

    <div class="search-bar" data-tour="search">
      <input
        bind:value={query}
        type="text"
        placeholder="e.g. liability risk assessment AND contract termination"
        class="field"
      />
      <button on:click={runSearch} class="btn btn-primary">
        {loading ? 'Searching...' : 'Search'}
      </button>
    </div>
  </section>

  <section class="search-grid">
    <aside class="panel-strong filters">
      <h3>Filters</h3>

      <div>
        <p class="filter-label">Document Type</p>
        <div class="space-y-1 text-sm">
          <label><input type="checkbox" checked /> Contract</label>
          <label><input type="checkbox" /> Regulatory Policy</label>
          <label><input type="checkbox" /> Legal Memo</label>
        </div>
      </div>

      <div>
        <p class="filter-label">Risk Level</p>
        <div class="space-y-1 text-sm">
          <label><input type="checkbox" /> Critical</label>
          <label><input type="checkbox" /> Elevated</label>
          <label><input type="checkbox" /> Moderate</label>
        </div>
      </div>
    </aside>

    <section class="panel-strong results">
      <header>
        <h3>Search Results</h3>
        <span>{results.length} results</span>
      </header>

      {#if results.length === 0}
        <p class="placeholder">No results found.</p>
      {:else}
        <div class="result-list">
          {#each results as r}
            <article class="result-card">
              <h4>{r.filename}</h4>
              <p>{r.snippet}</p>
              <span>Relevance: {r.relevance}%</span>
            </article>
          {/each}
        </div>
      {/if}
    </section>
  </section>
</div>

<style>
.search-hero {
  background: linear-gradient(120deg, rgba(14, 164, 107, 0.14), rgba(32, 149, 232, 0.1));
}

.hero-kicker {
  margin: 0;
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: #0d6f4a;
  font-weight: 700;
}

.search-hero h1 {
  margin: 8px 0 4px;
}

.search-hero p {
  margin: 0;
  color: #5d7077;
}

.search-bar {
  margin-top: 14px;
  display: flex;
  gap: 10px;
}

.search-grid {
  display: grid;
  grid-template-columns: minmax(250px, 0.9fr) minmax(0, 2.1fr);
  gap: 16px;
}

.filters {
  padding: 16px;
  display: grid;
  gap: 16px;
  height: fit-content;
}

.filters h3 {
  margin: 0;
}

.filter-label {
  margin: 0 0 6px;
  font-size: 0.74rem;
  text-transform: uppercase;
  letter-spacing: 0.07em;
  color: #667a81;
}

.filters label {
  display: flex;
  gap: 8px;
  align-items: center;
  color: #344a53;
}

.results {
  padding: 16px;
}

.results header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.results h3 {
  margin: 0;
}

.results header span {
  color: #62757b;
  font-size: 0.82rem;
}

.result-list {
  display: grid;
  gap: 10px;
}

.result-card {
  padding: 12px;
  border: 1px solid rgba(17, 34, 40, 0.09);
  border-radius: 12px;
  background: #fff;
}

.result-card h4 {
  margin: 0;
  color: #0f5d9a;
}

.result-card p {
  margin: 8px 0;
  color: #30454e;
  font-size: 0.92rem;
}

.result-card span {
  color: #607279;
  font-size: 0.79rem;
}

.placeholder {
  color: #607279;
}

@media (max-width: 900px) {
  .search-grid {
    grid-template-columns: 1fr;
  }

  .search-bar {
    flex-direction: column;
  }
}
</style>
