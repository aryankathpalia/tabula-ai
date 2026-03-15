<script lang="ts">
  import { goto } from '$app/navigation';
  import { onMount } from 'svelte';

  onMount(() => {
    const timer = setTimeout(() => goto('/dashboard'), 900);
    return () => clearTimeout(timer);
  });
</script>

<section class="landing-handoff panel p-8 md:p-10 fade-soft">
  <p class="kicker">Tabula AI</p>
  <h1>Preparing Your Legal Intelligence Workspace</h1>
  <p>
    Loading portfolio signals, contract insights, and document context.
  </p>

  <div class="loader-row">
    <span class="dot"></span>
    <span class="dot"></span>
    <span class="dot"></span>
  </div>
</section>

<style>
.landing-handoff {
  min-height: 52vh;
  display: grid;
  place-content: center;
  text-align: center;
  gap: 10px;
  background:
    linear-gradient(125deg, rgba(14, 164, 107, 0.16), rgba(32, 149, 232, 0.12)),
    rgba(255, 255, 255, 0.7);
}

.kicker {
  margin: 0;
  text-transform: uppercase;
  font-size: 0.74rem;
  letter-spacing: 0.1em;
  font-weight: 700;
  color: #0d6f4a;
}

h1 {
  margin: 0;
  font-size: clamp(1.6rem, 2.4vw, 2.7rem);
}

p {
  margin: 0;
  color: #5a6d75;
}

.loader-row {
  margin-top: 4px;
  display: flex;
  justify-content: center;
  gap: 8px;
}

.dot {
  width: 9px;
  height: 9px;
  border-radius: 999px;
  background: linear-gradient(140deg, #0ea46b, #2095e8);
  animation: pop 1.1s infinite ease-in-out;
}

.dot:nth-child(2) {
  animation-delay: 0.12s;
}

.dot:nth-child(3) {
  animation-delay: 0.24s;
}

@keyframes pop {
  0%,
  80%,
  100% {
    transform: scale(0.8);
    opacity: 0.45;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}
</style>
