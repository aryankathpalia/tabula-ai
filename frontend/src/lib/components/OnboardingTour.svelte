<script lang="ts">
  import { fade, fly } from 'svelte/transition';
  import { cubicOut } from 'svelte/easing';
  import { onMount } from 'svelte';

  type TourStep = {
    title: string;
    description: string;
    label: string;
    icon: 'analyze' | 'risk' | 'compare' | 'chat';
  };

  const STORAGE_KEY = 'tabula_onboarding_seen_v1';

  const steps: TourStep[] = [
    {
      label: 'Document Analysis',
      title: 'Analyze Contracts Instantly',
      description:
        'Upload and analyze legal documents in seconds. Our AI extracts key clauses, obligations, and structure - giving you a clear understanding without manual review.',
      icon: 'analyze'
    },
    {
      label: 'Risk Analysis',
      title: 'Visual Risk Detection',
      description:
        'Automatically detect and highlight risky clauses directly inside your contract. Identify liabilities, penalties, and exposure areas with precision.',
      icon: 'risk'
    },
    {
      label: 'Contract Comparison',
      title: 'Compare Contracts Side-by-Side',
      description:
        'Instantly compare multiple contracts to identify differences in clauses, obligations, and risk. Make faster decisions with structured insights.',
      icon: 'compare'
    },
    {
      label: 'AI Assistant',
      title: 'Ask Your Contracts Anything',
      description:
        'Use AI chat to query your documents - summarize clauses, explain terms, or extract key information instantly.',
      icon: 'chat'
    }
  ];

  let active = false;
  let stepIndex = 0;

  $: currentStep = steps[stepIndex];
  $: progress = ((stepIndex + 1) / steps.length) * 100;

  function isSeen(): boolean {
    if (typeof localStorage === 'undefined') return true;
    return localStorage.getItem(STORAGE_KEY) === 'true';
  }

  function markSeen() {
    if (typeof localStorage === 'undefined') return;
    localStorage.setItem(STORAGE_KEY, 'true');
  }

  function skip() {
    active = false;
    markSeen();
  }

  function close() {
    skip();
  }

  function next() {
    if (stepIndex >= steps.length - 1) {
      skip();
      return;
    }

    stepIndex += 1;
  }

  function previous() {
    if (stepIndex === 0) return;
    stepIndex -= 1;
  }

  function handleKeydown(e: KeyboardEvent) {
    if (!active) return;
    if (e.key === 'Escape') close();
    if (e.key === 'ArrowRight') next();
    if (e.key === 'ArrowLeft') previous();
  }

  onMount(() => {
    if (isSeen()) return;

    active = true;
    window.addEventListener('keydown', handleKeydown);

    return () => {
      window.removeEventListener('keydown', handleKeydown);
    };
  });
</script>

{#if active}
  <div class="onboarding-shell" in:fade={{ duration: 180 }} out:fade={{ duration: 160 }}>
    <div class="onboarding-backdrop" role="presentation" on:click={close}></div>

    <div class="onboarding-modal" role="dialog" aria-modal="true" aria-label="Product walkthrough">
      <header class="onboarding-header">
        <div class="eyebrow">Product Walkthrough</div>
        <button class="btn-close" aria-label="Close onboarding" on:click={close}>Close</button>
      </header>

      <div class="progress-wrap" aria-hidden="true">
        <div class="progress-track">
          <div class="progress-fill" style="width: {progress}%;"></div>
        </div>
        <div class="progress-dots">
          {#each steps as _, idx}
            <span class:active-dot={idx <= stepIndex}></span>
          {/each}
        </div>
      </div>

      <article class="step-panel">
        {#key stepIndex}
          <div class="step-content" in:fly={{ y: 12, duration: 220, opacity: 0.15, easing: cubicOut }} out:fade={{ duration: 150 }}>
          <div class="icon-chip" aria-hidden="true">
            {#if currentStep.icon === 'analyze'}
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">
                <rect x="4" y="3.5" width="13" height="17" rx="2"></rect>
                <line x1="8" y1="8" x2="13" y2="8"></line>
                <line x1="8" y1="12" x2="13" y2="12"></line>
                <line x1="8" y1="16" x2="11" y2="16"></line>
                <circle cx="18.5" cy="17.5" r="2.6"></circle>
                <line x1="20.3" y1="19.3" x2="22" y2="21"></line>
              </svg>
            {:else if currentStep.icon === 'risk'}
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">
                <path d="M12 3.5 4.8 6.8v5.5c0 4.6 3 8.2 7.2 9.7 4.2-1.5 7.2-5.1 7.2-9.7V6.8z"></path>
                <path d="M12 8.2v5"></path>
                <circle cx="12" cy="16.5" r="0.8" fill="currentColor" stroke="none"></circle>
              </svg>
            {:else if currentStep.icon === 'compare'}
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">
                <rect x="3" y="4" width="7" height="16" rx="1.5"></rect>
                <rect x="14" y="4" width="7" height="16" rx="1.5"></rect>
                <line x1="6" y1="8" x2="7.8" y2="8"></line>
                <line x1="6" y1="12" x2="8.2" y2="12"></line>
                <line x1="17" y1="8" x2="19" y2="8"></line>
                <line x1="16" y1="12" x2="19" y2="12"></line>
              </svg>
            {:else}
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">
                <path d="M4 6.5A2.5 2.5 0 0 1 6.5 4h11A2.5 2.5 0 0 1 20 6.5v7A2.5 2.5 0 0 1 17.5 16H9l-4.5 4v-4.5z"></path>
                <circle cx="10" cy="10" r="0.8" fill="currentColor" stroke="none"></circle>
                <circle cx="13" cy="10" r="0.8" fill="currentColor" stroke="none"></circle>
                <circle cx="16" cy="10" r="0.8" fill="currentColor" stroke="none"></circle>
              </svg>
            {/if}
          </div>

          <div class="step-meta">{currentStep.label}</div>
          <h2>{currentStep.title}</h2>
          <p>{currentStep.description}</p>
          </div>
        {/key}
      </article>

      <footer class="onboarding-actions">
        <span class="step-count">Step {stepIndex + 1} of {steps.length}</span>
        <div class="button-row">
          <button class="btn ghost" on:click={skip}>Skip</button>
          <button class="btn ghost" on:click={previous} disabled={stepIndex === 0}>Back</button>
          <button class="btn primary" on:click={next}>
            {stepIndex === steps.length - 1 ? 'Finish' : 'Next'}
          </button>
        </div>
      </footer>
    </div>
  </div>
{/if}

<style>
  .onboarding-shell {
    position: fixed;
    inset: 0;
    z-index: 70;
    display: grid;
    place-items: center;
    padding: 1.25rem;
  }

  .onboarding-backdrop {
    position: absolute;
    inset: 0;
    background:
      radial-gradient(85rem 35rem at 20% -10%, rgba(40, 92, 255, 0.2), transparent 55%),
      radial-gradient(65rem 30rem at 85% 120%, rgba(16, 185, 129, 0.18), transparent 60%),
      rgba(2, 6, 23, 0.6);
    backdrop-filter: blur(8px);
  }

  .onboarding-modal {
    position: relative;
    width: min(100%, 720px);
    border-radius: 20px;
    border: 1px solid rgba(148, 163, 184, 0.2);
    background: linear-gradient(180deg, rgba(255, 255, 255, 0.98) 0%, rgba(248, 250, 252, 0.98) 100%);
    box-shadow: 0 30px 80px rgba(15, 23, 42, 0.28);
    padding: 1.5rem;
    overflow: hidden;
  }

  .onboarding-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 1rem;
  }

  .eyebrow {
    font-size: 0.78rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #475569;
    font-weight: 650;
  }

  .btn-close {
    border: none;
    background: transparent;
    font-size: 0.9rem;
    color: #64748b;
    cursor: pointer;
    padding: 0.25rem 0.35rem;
  }

  .btn-close:hover {
    color: #0f172a;
  }

  .progress-wrap {
    margin-bottom: 1.2rem;
  }

  .progress-track {
    height: 6px;
    border-radius: 999px;
    background: rgba(148, 163, 184, 0.22);
    overflow: hidden;
  }

  .progress-fill {
    height: 100%;
    background: linear-gradient(90deg, #2563eb 0%, #14b8a6 100%);
    transition: width 220ms ease;
  }

  .progress-dots {
    display: flex;
    gap: 0.45rem;
    margin-top: 0.65rem;
  }

  .progress-dots span {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: #cbd5e1;
    transition: transform 180ms ease, background-color 180ms ease;
  }

  .progress-dots span.active-dot {
    background: #2563eb;
    transform: scale(1.12);
  }

  .step-panel {
    min-height: 250px;
    position: relative;
    overflow: hidden;
    margin-bottom: 1.3rem;
  }

  .step-content {
    position: absolute;
    inset: 0;
    display: flex;
    flex-direction: column;
    justify-content: center;
    gap: 0.75rem;
  }

  .icon-chip {
    width: 48px;
    height: 48px;
    border-radius: 14px;
    display: grid;
    place-items: center;
    background: linear-gradient(145deg, rgba(37, 99, 235, 0.14), rgba(20, 184, 166, 0.14));
    color: #0f172a;
  }

  .icon-chip svg {
    width: 24px;
    height: 24px;
  }

  .step-meta {
    font-size: 0.8rem;
    font-weight: 600;
    color: #0f766e;
    letter-spacing: 0.04em;
    text-transform: uppercase;
  }

  h2 {
    font-size: clamp(1.45rem, 1.2rem + 0.7vw, 1.95rem);
    line-height: 1.25;
    margin: 0;
    color: #0f172a;
    letter-spacing: -0.02em;
  }

  p {
    margin: 0;
    font-size: 1rem;
    line-height: 1.7;
    color: #334155;
    max-width: 62ch;
  }

  .onboarding-actions {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 0.8rem;
    border-top: 1px solid rgba(148, 163, 184, 0.25);
    padding-top: 1rem;
  }

  .step-count {
    font-size: 0.84rem;
    color: #64748b;
  }

  .button-row {
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
    justify-content: flex-end;
  }

  .btn {
    border-radius: 10px;
    padding: 0.58rem 0.95rem;
    font-weight: 600;
    font-size: 0.9rem;
    border: 1px solid transparent;
    cursor: pointer;
    transition: all 180ms ease;
  }

  .btn.ghost {
    background: #f8fafc;
    color: #0f172a;
    border-color: rgba(148, 163, 184, 0.35);
  }

  .btn.ghost:hover:not(:disabled) {
    background: #f1f5f9;
  }

  .btn.primary {
    background: linear-gradient(90deg, #1d4ed8 0%, #0f766e 100%);
    color: #ffffff;
    box-shadow: 0 10px 24px rgba(29, 78, 216, 0.24);
  }

  .btn.primary:hover {
    filter: brightness(1.05);
  }

  .btn:disabled {
    opacity: 0.45;
    cursor: not-allowed;
  }

  @media (max-width: 640px) {
    .onboarding-modal {
      padding: 1.1rem;
      border-radius: 16px;
    }

    .step-panel {
      min-height: 230px;
    }

    .onboarding-actions {
      flex-direction: column;
      align-items: flex-start;
    }

    .button-row {
      width: 100%;
    }

    .button-row .btn {
      flex: 1;
      min-width: 6rem;
    }
  }
</style>
