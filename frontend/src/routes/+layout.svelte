<script lang="ts">
  import Sidebar from '$lib/components/Sidebar.svelte';
  import OnboardingTour from '$lib/components/OnboardingTour.svelte';
  import '../app.css';

  let sidebarCollapsed = false;
</script>

<div class="app-shell">

  <Sidebar bind:collapsed={sidebarCollapsed} />

  <main class="app-main">
    <div class="page-wrap">
      <slot />
    </div>
  </main>

  <OnboardingTour />

</div>