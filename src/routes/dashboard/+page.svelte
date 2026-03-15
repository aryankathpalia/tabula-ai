<script lang="ts">
import { onMount } from "svelte";

let loading = true;

let totalDocuments = 0;
let averageRiskScore = 0;
let exposureDistribution = {
  high: 0,
  moderate: 0,
  low: 0
};
let highestRiskDoc: HighRiskDoc | null = null;

let topRiskDriver = "";
let topRiskCount = 0;

type ExposureLevel = "High Exposure" | "Moderate Exposure" | "Low Exposure";

type HighRiskDoc = {
  id: number;
  filename: string;
  score: number;
  exposure: ExposureLevel;
};

let recentHighRiskDocs: HighRiskDoc[] = [];

onMount(async () => {
  try {
    const res = await fetch(`${import.meta.env.VITE_API_URL}/analytics/dashboard`);
    const data = await res.json();

    totalDocuments = data.total_documents;
    averageRiskScore = data.average_risk_score;
    exposureDistribution = data.exposure_distribution;
    recentHighRiskDocs = data.recent_high_risk_documents;

    if (recentHighRiskDocs.length > 0) {
      highestRiskDoc = [...recentHighRiskDocs].sort((a, b) => b.score - a.score)[0];
    }

    topRiskDriver = "Moderate Exposure";
    topRiskCount = exposureDistribution.moderate;

    if (exposureDistribution.high > topRiskCount) {
      topRiskDriver = "High Exposure";
      topRiskCount = exposureDistribution.high;
    }

    if (exposureDistribution.low > topRiskCount) {
      topRiskDriver = "Low Exposure";
      topRiskCount = exposureDistribution.low;
    }
  } catch (err) {
    console.error("Dashboard load failed", err);
  } finally {
    loading = false;
  }
});
</script>

<div class="dashboard-page space-y-6">
  <section class="panel hero-panel p-6 md:p-8">
    <div class="max-w-2xl space-y-4">
      <p class="hero-kicker">Tabula AI Command Deck</p>
      <h1 class="hero-title">Executive Risk Intelligence</h1>
      <p class="hero-copy">
        Monitor exposure trends, detect problematic clauses, and prioritize legal action with an AI-native workflow.
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

  <section class="stat-grid">
    <article class="panel-strong stat-card">
      <span>Total Documents</span>
      {#if loading}
        <div class="skeleton stat-skeleton"></div>
      {:else}
        <h2>{totalDocuments}</h2>
      {/if}
      <p>Contracts currently indexed for analysis.</p>
    </article>

    <article class="panel-strong stat-card">
      <span>Average Risk Score</span>
      {#if loading}
        <div class="skeleton stat-skeleton"></div>
      {:else}
        <h2>{averageRiskScore}</h2>
      {/if}
      <p>Weighted across processed agreements.</p>
    </article>

    <article class="panel-strong stat-card">
      <span>High Exposure</span>
      {#if loading}
        <div class="skeleton stat-skeleton"></div>
      {:else}
        <h2 class="text-[#b52d41]">{exposureDistribution.high}</h2>
      {/if}
      <p>Immediate legal review recommended.</p>
    </article>

    <article class="panel-strong stat-card">
      <span>Moderate Exposure</span>
      {#if loading}
        <div class="skeleton stat-skeleton"></div>
      {:else}
        <h2 class="text-[#9a5a0f]">{exposureDistribution.moderate}</h2>
      {/if}
      <p>Watchlist contracts with notable risk.</p>
    </article>
  </section>

  <section class="dashboard-grid">
    <article class="panel-strong activity-panel" data-tour="activity">
      <header>
        <h3>Recent Document Activity</h3>
        <button class="btn btn-ghost" on:click={() => (window.location.href = '/documents')}>View All</button>
      </header>

      {#if loading}
        <p class="placeholder">Loading activity feed...</p>
      {:else if recentHighRiskDocs.length === 0}
        <p class="placeholder">No recent risk documents available.</p>
      {:else}
        <div class="activity-list">
          {#each recentHighRiskDocs as d}
            <button class="activity-row" on:click={() => (window.location.href = `/documents/${d.id}`)}>
              <div>
                <p class="doc-name">{d.filename}</p>
                <p class="doc-meta">Score {d.score}</p>
              </div>
              <span
                class="pill"
                class:high={d.exposure === 'High Exposure'}
                class:moderate={d.exposure === 'Moderate Exposure'}
                class:low={d.exposure === 'Low Exposure'}
              >
                {d.exposure}
              </span>
            </button>
          {/each}
        </div>
      {/if}
    </article>

    <aside class="space-y-5" data-tour="insights">
      <article class="panel-strong insights-card">
        <h3>Risk Distribution</h3>
        <div class="space-y-3">
          {#each Object.entries(exposureDistribution) as [key, value]}
            <div class="space-y-1">
              <div class="metric-row">
                <span class="capitalize">{key}</span>
                <span>{value}</span>
              </div>
              <div class="bar-track">
                <div
                  class="bar-fill"
                  style="width: {totalDocuments ? (value / totalDocuments) * 100 : 0}%"
                ></div>
              </div>
            </div>
          {/each}
        </div>
      </article>

      <article class="panel-strong insights-card">
        <h3>AI Risk Insights</h3>
        <div class="space-y-4 text-sm">
          <div>
            <p class="label">Top Risk Pattern</p>
            <p class="value">{topRiskDriver} detected in {topRiskCount} contracts.</p>
          </div>

          {#if highestRiskDoc}
            <div>
              <p class="label">Highest Risk Document</p>
              <p class="value">{highestRiskDoc.filename} - Score {highestRiskDoc.score}</p>
            </div>
          {/if}

          <div>
            <p class="label">Portfolio Status</p>
            <p class="value">
              {exposureDistribution.high === 0
                ? "No high-exposure contracts detected in the current portfolio."
                : `${exposureDistribution.high} high-exposure contracts require review.`}
            </p>
          </div>
        </div>
      </article>
    </aside>
  </section>
</div>

<style>
.dashboard-page {
  animation: fade-up 380ms ease;
}

.hero-panel {
  position: relative;
  overflow: hidden;
  background:
    linear-gradient(120deg, rgba(14, 164, 107, 0.16), rgba(32, 149, 232, 0.1)),
    rgba(255, 255, 255, 0.66);
}

.hero-panel::after {
  content: '';
  position: absolute;
  right: -80px;
  top: -70px;
  width: 260px;
  height: 260px;
  border-radius: 999px;
  background: radial-gradient(circle, rgba(32, 149, 232, 0.27), transparent 66%);
}

.hero-kicker {
  font-size: 0.76rem;
  text-transform: uppercase;
  letter-spacing: 0.11em;
  font-weight: 700;
  color: #0b6f49;
}

.hero-title {
  margin: 0;
  font-size: clamp(1.8rem, 2.4vw, 2.8rem);
}

.hero-copy {
  margin: 0;
  max-width: 60ch;
  color: #465a62;
}

.stat-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 14px;
}

.stat-card {
  padding: 18px;
}

.stat-card span {
  font-size: 0.72rem;
  text-transform: uppercase;
  letter-spacing: 0.07em;
  color: #5f7178;
}

.stat-card h2 {
  margin: 10px 0 6px;
  font-size: 2rem;
}

.stat-skeleton {
  width: 56%;
  height: 36px;
  margin: 10px 0 6px;
}

.stat-card p {
  margin: 0;
  color: #607179;
  font-size: 0.84rem;
}

.dashboard-grid {
  display: grid;
  grid-template-columns: minmax(0, 2fr) minmax(300px, 1fr);
  gap: 16px;
}

.activity-panel {
  padding: 18px;
}

.activity-panel header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.activity-panel h3,
.insights-card h3 {
  margin: 0;
  font-size: 1.04rem;
}

.activity-list {
  display: grid;
  gap: 10px;
}

.activity-row {
  border: 1px solid rgba(17, 34, 40, 0.08);
  background: #fff;
  border-radius: 14px;
  padding: 12px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  text-align: left;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.activity-row:hover {
  transform: translateY(-1px);
  box-shadow: 0 10px 22px rgba(12, 29, 39, 0.12);
}

.doc-name {
  margin: 0;
  font-weight: 700;
}

.doc-meta {
  margin: 2px 0 0;
  color: #61737a;
  font-size: 0.83rem;
}

.placeholder {
  padding: 16px;
  color: #66797f;
}

.insights-card {
  padding: 16px;
}

.metric-row {
  display: flex;
  justify-content: space-between;
  font-size: 0.85rem;
  color: #52656d;
}

.bar-track {
  width: 100%;
  height: 8px;
  background: rgba(17, 34, 40, 0.11);
  border-radius: 999px;
}

.bar-fill {
  height: 100%;
  border-radius: 999px;
  background: linear-gradient(120deg, #0ea46b, #2095e8);
  transition: width 0.4s ease;
}

.label {
  margin: 0;
  color: #6a7d83;
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

.value {
  margin: 4px 0 0;
  color: #1c333c;
}

@media (max-width: 1100px) {
  .stat-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .dashboard-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .stat-grid {
    grid-template-columns: 1fr;
  }
}
</style>
