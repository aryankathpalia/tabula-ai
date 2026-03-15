<script lang="ts">
  import { onMount } from 'svelte';

  type TourStep = {
    title: string;
    description: string;
    selector: string;
  };

  const STORAGE_KEY = 'tabula_onboarding_seen_v1';

  const steps: TourStep[] = [
    {
      title: 'Control Center',
      description: 'Use this navigation rail to move across analysis, risk review, and document chat.',
      selector: '[data-tour="nav"]'
    },
    {
      title: 'Workspace Search',
      description: 'Semantic search helps you jump to clauses, risks, and documents in seconds.',
      selector: '[data-tour="search"]'
    },
    {
      title: 'Live Activity Feed',
      description: 'Track the latest analyzed contracts and jump directly into detailed review from here.',
      selector: '[data-tour="activity"]'
    },
    {
      title: 'Risk Intelligence',
      description: 'This panel surfaces exposure trends and key legal risk signals from your portfolio.',
      selector: '[data-tour="insights"]'
    }
  ];

  let active = false;
  let stepIndex = 0;
  let targetRect: DOMRect | null = null;

  $: currentStep = steps[stepIndex];

  function isSeen(): boolean {
    if (typeof localStorage === 'undefined') return true;
    return localStorage.getItem(STORAGE_KEY) === 'true';
  }

  function markSeen() {
    if (typeof localStorage === 'undefined') return;
    localStorage.setItem(STORAGE_KEY, 'true');
  }

  function refreshTarget() {
    if (!active) return;

    const el = document.querySelector(currentStep.selector);
    if (!el) {
      targetRect = null;
      return;
    }

    targetRect = (el as HTMLElement).getBoundingClientRect();
  }

  function skip() {
    active = false;
    markSeen();
  }

  function next() {
    if (stepIndex >= steps.length - 1) {
      skip();
      return;
    }

    stepIndex += 1;
    setTimeout(refreshTarget, 20);
  }

  function close() {
    skip();
  }

  function previous() {
    if (stepIndex === 0) return;
    stepIndex -= 1;
    setTimeout(refreshTarget, 20);
  }

  function handleKeydown(e: KeyboardEvent) {
    if (!active) return;
    if (e.key === 'Escape') close();
    if (e.key === 'ArrowRight') next();
    if (e.key === 'ArrowLeft') previous();
  }

  function cardPosition() {
    if (!targetRect) {
      return {
        top: 90,
        left: 20
      };
    }

    const cardWidth = Math.min(360, window.innerWidth - 24);
    const bottomSpace = window.innerHeight - targetRect.bottom;
    const top = bottomSpace > 230
      ? targetRect.bottom + 14
      : Math.max(14, targetRect.top - 190);

    const preferredLeft = Math.min(
      window.innerWidth - cardWidth - 12,
      Math.max(12, targetRect.left)
    );

    return { top, left: preferredLeft };
  }

  $: pos = cardPosition();

  onMount(() => {
    if (isSeen()) return;

    active = true;
    setTimeout(refreshTarget, 120);

    const onScroll = () => refreshTarget();
    const onResize = () => refreshTarget();

    window.addEventListener('resize', onResize);
    window.addEventListener('scroll', onScroll, true);
    window.addEventListener('keydown', handleKeydown);

    return () => {
      window.removeEventListener('resize', onResize);
      window.removeEventListener('scroll', onScroll, true);
      window.removeEventListener('keydown', handleKeydown);
    };
  });

  $: if (active && !targetRect) {
    const fallbackIndex = steps.findIndex((step, idx) => {
      if (idx === stepIndex) return false;
      return !!document.querySelector(step.selector);
    });

    if (fallbackIndex > -1 && fallbackIndex !== stepIndex) {
      stepIndex = fallbackIndex;
      setTimeout(refreshTarget, 20);
    }
  }
</script>

{#if active}
  <div class="spotlight-overlay" role="presentation" on:click={close}></div>

  {#if targetRect}
    <div
      class="spotlight-hole"
      style="
        top: {Math.max(8, targetRect.top - 8)}px;
        left: {Math.max(8, targetRect.left - 8)}px;
        width: {Math.max(36, targetRect.width + 16)}px;
        height: {Math.max(36, targetRect.height + 16)}px;
      "
    ></div>
  {/if}

  <div class="tour-card fade-up" style="top: {pos.top}px; left: {pos.left}px;">
    <h3>{currentStep.title}</h3>
    <p>{currentStep.description}</p>

    <div class="tour-actions">
      <span class="text-xs text-slate-500">Step {stepIndex + 1} / {steps.length}</span>
      <div class="flex items-center gap-2">
        {#if stepIndex > 0}
          <button class="btn btn-ghost" on:click={previous}>Back</button>
        {/if}
        <button class="btn btn-ghost" on:click={skip}>Skip</button>
        <button class="btn btn-primary" on:click={next}>
          {stepIndex === steps.length - 1 ? 'Finish' : 'Next'}
        </button>
      </div>
    </div>
  </div>
{/if}
