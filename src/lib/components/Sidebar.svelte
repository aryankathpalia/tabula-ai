<script lang="ts">
  import { page } from '$app/stores';

  import LayoutDashboard from 'lucide-svelte/icons/layout-dashboard';
  import FileText from 'lucide-svelte/icons/file-text';
  import Shield from 'lucide-svelte/icons/shield';
  import MessageSquare from 'lucide-svelte/icons/message-square';
  import Settings from 'lucide-svelte/icons/settings';

  export let collapsed = false;

  const navItems = [
    { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
    { name: 'Documents', href: '/documents', icon: FileText },
    { name: 'Risk Analysis', href: '/risk', icon: Shield },
    { name: 'Chat', href: '/team', icon: MessageSquare },
    { name: 'About', href: '/about', icon: Settings }
  ];
</script>

<aside
  class="sidebar"
  data-tour="nav"
  class:collapsed={collapsed}
>
  <div class="sidebar-header">
    <div class="brand">
      <div class="logo-mark" aria-hidden="true">
        <svg viewBox="0 0 64 64" role="img" aria-label="Tabula AI logo">
          <defs>
            <linearGradient id="brandBg" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stop-color="#07131a" />
              <stop offset="100%" stop-color="#0f2731" />
            </linearGradient>
            <linearGradient id="orbitA" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stop-color="#2df9c5" />
              <stop offset="100%" stop-color="#36b9ff" />
            </linearGradient>
            <linearGradient id="orbitB" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stop-color="#83f9ff" />
              <stop offset="100%" stop-color="#67ffd6" />
            </linearGradient>
          </defs>
          <rect x="4" y="4" width="56" height="56" rx="18" fill="url(#brandBg)" />
          <circle cx="32" cy="32" r="18" stroke="url(#orbitA)" stroke-width="4" fill="none" opacity="0.95" />
          <path d="M15 32c0-9.4 7.6-17 17-17" stroke="url(#orbitB)" stroke-width="4" stroke-linecap="round" fill="none" />
          <path d="M24 22h20" stroke="#eaffff" stroke-width="3.6" stroke-linecap="round" />
          <path d="M32 22v20" stroke="#eaffff" stroke-width="4.1" stroke-linecap="round" />
          <path d="M25 42h14" stroke="#eaffff" stroke-width="2.6" stroke-linecap="round" opacity="0.9" />
          <circle cx="47" cy="20" r="3" fill="#9dfcff" />
          <circle cx="17" cy="41" r="2.1" fill="#5ec6ff" opacity="0.9" />
        </svg>
      </div>
      {#if !collapsed}
        <div class="brand-text-wrap">
          <span class="brand-title">Tabula AI</span>
          <span class="brand-subtitle">Signal Over Noise</span>
        </div>
      {/if}
    </div>

    <button
      class="collapse-btn"
      on:click={() => (collapsed = !collapsed)}
    >
      {#if collapsed}→{:else}←{/if}
    </button>
  </div>

  <nav class="sidebar-nav">
    {#each navItems as item}
      <a
        href={item.href}
        class="nav-item"
        class:active={$page.url.pathname.startsWith(item.href)}
      >
        <span class="icon-wrap"><svelte:component this={item.icon} size={18} stroke-width={1.8} /></span>

        {#if !collapsed}
          <span>{item.name}</span>
        {/if}
      </a>
    {/each}
  </nav>

  <div class="sidebar-footer">
    {#if !collapsed}
      <span>Contract risk cockpit</span>
      <span class="live-dot"><span></span>Live</span>
    {/if}
  </div>
</aside>

<style>
.sidebar {
  margin: 16px;
  height: calc(100vh - 32px);
  background: rgba(255, 255, 255, 0.76);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(17, 34, 40, 0.12);
  border-radius: 20px;
  display: flex;
  flex-direction: column;
  width: 260px;
  transition: width 0.25s ease, transform 0.25s ease;
  box-shadow: 0 18px 42px rgba(10, 30, 38, 0.16);
}

.sidebar.collapsed {
  width: 64px;
}

.sidebar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px;
  border-bottom: 1px solid rgba(17, 34, 40, 0.1);
}

.brand {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo-mark {
  width: 42px;
  height: 42px;
  border-radius: 15px;
  display: grid;
  place-items: center;
  flex: 0 0 auto;
  box-shadow: 0 10px 25px rgba(5, 25, 31, 0.32), 0 0 18px rgba(45, 249, 197, 0.24);
  background: radial-gradient(circle at 15% 12%, rgba(121, 255, 240, 0.25), rgba(8, 24, 31, 0));
}

.logo-mark svg {
  width: 100%;
  height: 100%;
  display: block;
}

.brand-text-wrap {
  display: flex;
  flex-direction: column;
  line-height: 1.2;
}

.brand-title {
  font-family: 'Space Grotesk', sans-serif;
  font-weight: 700;
  font-size: 0.96rem;
  letter-spacing: 0.02em;
  color: #14303a;
}

.brand-subtitle {
  font-size: 0.64rem;
  color: #3e5e69;
  letter-spacing: 0.09em;
  text-transform: uppercase;
}

.collapse-btn {
  padding: 5px 8px;
  border-radius: 10px;
  border: 1px solid rgba(17, 34, 40, 0.13);
  color: #29444f;
  background: rgba(255, 255, 255, 0.72);
  transition: all 0.2s ease;
}

.collapse-btn:hover {
  background: rgba(14, 164, 107, 0.12);
}

.sidebar-nav {
  flex: 1;
  padding: 12px 10px;
  overflow-y: auto;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  border-radius: 12px;
  font-size: 0.89rem;
  color: #41545d;
  text-decoration: none;
  transition: all 0.2s ease;
}

.icon-wrap {
  display: inline-grid;
  place-items: center;
  color: #5f7178;
}

.nav-item:hover {
  background: rgba(17, 34, 40, 0.05);
  color: #112228;
  transform: translateX(2px);
}

.nav-item:hover .icon-wrap {
  color: #112228;
}

.nav-item.active {
  background: linear-gradient(130deg, rgba(14, 164, 107, 0.2), rgba(32, 149, 232, 0.2));
  color: #0d6f4a;
  font-weight: 700;
  border: 1px solid rgba(14, 164, 107, 0.25);
}

.nav-item.active .icon-wrap {
  color: #0d6f4a;
}

.sidebar-footer {
  padding: 12px 14px;
  border-top: 1px solid rgba(17, 34, 40, 0.1);
  font-size: 0.74rem;
  color: #607179;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.live-dot {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.live-dot span {
  width: 7px;
  height: 7px;
  border-radius: 999px;
  background: #0ea46b;
  box-shadow: 0 0 0 5px rgba(14, 164, 107, 0.14);
}

@media (max-width: 800px) {
  .sidebar {
    margin: 0;
    border-radius: 0;
    width: 100%;
    height: 72px;
    flex-direction: row;
    align-items: center;
    padding: 8px;
  }

  .sidebar.collapsed {
    width: 100%;
  }

  .sidebar-header {
    border: none;
    width: auto;
    padding: 6px;
  }

  .sidebar-nav {
    display: flex;
    gap: 4px;
    flex: 1;
    padding: 0 8px;
    overflow-x: auto;
    overflow-y: hidden;
  }

  .nav-item {
    white-space: nowrap;
    padding: 8px 10px;
  }

  .sidebar-footer {
    display: none;
  }
}
</style>
