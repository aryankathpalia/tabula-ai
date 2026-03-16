<script lang="ts">
  import { onMount } from 'svelte';
  import ChevronRight from 'lucide-svelte/icons/chevron-right';
  import ChevronLeft from 'lucide-svelte/icons/chevron-left';
  import FileText from 'lucide-svelte/icons/file-text';
  import ShieldCheck from 'lucide-svelte/icons/shield-check';
  import MessageSquare from 'lucide-svelte/icons/message-square';
  import Zap from 'lucide-svelte/icons/zap';
  import Lock from 'lucide-svelte/icons/lock';
  import Building from 'lucide-svelte/icons/building';
  import Linkedin from 'lucide-svelte/icons/linkedin';
  import Github from 'lucide-svelte/icons/github';
  import Mail from 'lucide-svelte/icons/mail';

  let stepIndex = 0;
  let activeAnimation = 0;
  let videoEls: HTMLVideoElement[] = [];

  const email = 'aryan.kathpalia2000@gmail.com';
  let copied = false;

  function copyEmail() {
    navigator.clipboard.writeText(email);
    copied = true;
    setTimeout(() => {
      copied = false;
    }, 2000);
  }

  const steps = [
    { title: 'Upload Your Document', text: 'Ingest PDF, DOCX, and TXT contracts directly into Tabula AI for automated review.' },
    { title: 'AI Extracts Clauses', text: 'Domain-aware models detect liability, termination, penalties, and critical legal terms.' },
    { title: 'Risk Scoring', text: 'The platform computes a structured exposure score and confidence profile for each contract.' },
    { title: 'Interactive Review', text: 'Investigate highlighted evidence and connect risk outputs to precise document context.' },
    { title: 'Chat With Documents', text: 'Ask natural-language questions and retrieve contextual answers grounded in source clauses.' }
  ];

  const features = [
    { icon: FileText, title: 'AI Clause Detection', text: 'Automatically identifies contractual structures and legal obligations at scale.' },
    { icon: ShieldCheck, title: 'Risk Intelligence', text: 'Transforms clause signals into an enterprise-ready exposure framework.' },
    { icon: MessageSquare, title: 'Document Chat', text: 'Interactive AI assistant grounded in document evidence and legal context.' },
    { icon: Zap, title: 'Fast Processing', text: 'Optimized ingestion and analysis pipelines for rapid contract understanding.' },
    { icon: Lock, title: 'Private & Secure', text: 'Designed for confidentiality and trusted operation across legal workflows.' },
    { icon: Building, title: 'Enterprise Ready', text: 'Structured for teams handling high-volume agreements and compliance demands.' }
  ];

  function next() {
    if (stepIndex < steps.length - 3) stepIndex++;
  }

  function prev() {
    if (stepIndex > 0) stepIndex--;
  }

  onMount(() => {
    function playAnimation(index: number) {
      videoEls.forEach((v, i) => {
        if (!v) return;
        if (i === index) {
          v.currentTime = 0;
          v.play();
        } else {
          v.pause();
          v.currentTime = 0;
        }
      });
    }

    playAnimation(0);
    const interval = setInterval(() => {
      activeAnimation = (activeAnimation + 1) % steps.length;
      playAnimation(activeAnimation);
    }, 3200);

    return () => clearInterval(interval);
  });
</script>

<div class="about-page space-y-6">
  <section class="panel hero p-7 md:p-10">
    <p class="hero-kicker">Product Story</p>
    <h1>Contract Intelligence For High-Stakes Legal Teams</h1>
    <p class="hero-copy">
      Tabula AI transforms dense contracts into clear, explainable risk intelligence. It combines clause extraction,
      exposure scoring, and conversational analysis in one focused legal workspace.
    </p>

    <div class="hero-metrics">
      <article class="metric panel-strong floating-soft">
        <span>End-to-End Flow</span>
        <strong>Upload -> Analyze -> Act</strong>
      </article>
      <article class="metric panel-strong floating-soft">
        <span>Core Promise</span>
        <strong>Faster, clearer legal decisions</strong>
      </article>
      <article class="metric panel-strong floating-soft">
        <span>Built For</span>
        <strong>Enterprise contract operations</strong>
      </article>
    </div>
  </section>

  <section class="panel-strong p-6 md:p-8 journey">
    <header class="journey-head">
      <div>
        <p class="section-kicker">Workflow</p>
        <h2>How Tabula AI Works</h2>
      </div>
      <div class="nav-actions">
        <button class="btn btn-ghost" on:click={prev}><ChevronLeft size={18} /></button>
        <button class="btn btn-ghost" on:click={next}><ChevronRight size={18} /></button>
      </div>
    </header>

    <div class="journey-grid">
      {#each steps.slice(stepIndex, stepIndex + 3) as step, i (stepIndex + i)}
        <article class="step-card">
          <div class="step-video">
<video
  autoplay
  muted
  loop
  playsinline
  preload="auto"
  bind:this={videoEls[stepIndex + i]}
  class:active={activeAnimation === stepIndex + i}
>
  <source src={`/webm${stepIndex + i + 1}.webm`} type="video/webm" />
</video>
          </div>
          <p class="step-label">Step {stepIndex + i + 1}</p>
          <h3>{step.title}</h3>
          <p>{step.text}</p>
        </article>
      {/each}
    </div>
  </section>

  <section class="panel-strong p-6 md:p-8 capabilities">
    <p class="section-kicker">Capabilities</p>
    <h2>Platform Highlights</h2>
    <div class="feature-grid">
      {#each features as f}
        <article class="feature-card">
          <svelte:component this={f.icon} size={26} stroke-width={1.8} />
          <h3>{f.title}</h3>
          <p>{f.text}</p>
        </article>
      {/each}
    </div>
  </section>

  <section class="panel-strong p-6 md:p-8 developer">
    <div class="dev-copy">
      <p class="section-kicker">Builder</p>
      <h2>About the Developer</h2>
      <p>
        Hi, I am Aryan Kathpalia, focused on building practical AI systems that make complex information usable.
        Tabula AI is built to help legal and compliance teams detect obligations, liabilities, and contractual risk
        quickly with transparent evidence.
      </p>
      <p>
        The platform combines document parsing, clause classification, structured scoring, and AI-generated guidance
        so teams can move from document review to risk action with clarity.
      </p>

      <div class="tags">
        <span>Machine Learning</span>
        <span>AI Systems</span>
        <span>Document Intelligence</span>
      </div>

      <div class="socials">
        <a href="https://www.linkedin.com/in/aryan-kathpalia/" target="_blank" rel="noreferrer"><Linkedin size={20} /></a>
        <a href="https://github.com/aryankathpalia/" target="_blank" rel="noreferrer"><Github size={20} /></a>
        <button class="mail-btn" on:click|preventDefault={copyEmail}><Mail size={20} /></button>
        <span class="email-text">{email}</span>
        {#if copied}
          <span class="copied">Copied</span>
        {/if}
      </div>
    </div>

    <div class="dev-photo-wrap">
      <div class="photo panel">
        <img src="/aryankathpalia.jpg" alt="Aryan - Developer" />
      </div>
    </div>
  </section>
</div>

<style>
.about-page { animation: fade-up 420ms ease; }
.hero { background: linear-gradient(130deg, rgba(14, 164, 107, 0.16), rgba(32, 149, 232, 0.14)), rgba(255, 255, 255, 0.72); }
.hero-kicker, .section-kicker { margin: 0; font-size: 0.73rem; letter-spacing: 0.1em; text-transform: uppercase; font-weight: 700; color: #0d6f4a; }
.hero h1 { margin: 10px 0 8px; font-size: clamp(1.8rem, 2.8vw, 3.1rem); max-width: 18ch; }
.hero-copy { margin: 0; max-width: 62ch; color: #4f6269; line-height: 1.65; }
.hero-metrics { margin-top: 18px; display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 12px; }
.metric { padding: 14px; }
.metric span { display: block; color: #678087; font-size: 0.76rem; text-transform: uppercase; letter-spacing: 0.06em; }
.metric strong { font-size: 1rem; }
.journey-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px; gap: 10px; }
.journey-head h2, .capabilities h2, .developer h2 { margin: 6px 0 0; }
.nav-actions { display: flex; gap: 8px; }
.journey-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 14px; }
.step-card { border: 1px solid rgba(17, 34, 40, 0.1); border-radius: 14px; background: #fff; padding: 14px; }
.step-video {
  border-radius: 12px;
  background: rgba(17, 34, 40, 0.07);
  height: 160px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 12px;
  overflow: hidden;
}
.step-video video {
  width: 100%;
  height: 160px;
  object-fit: contain;
}
.step-label { margin: 0; color: #667a81; font-size: 0.74rem; text-transform: uppercase; letter-spacing: 0.08em; }
.step-card h3 { margin: 6px 0 4px; font-size: 1.04rem; }
.step-card p { margin: 0; color: #5b7078; line-height: 1.55; }
.feature-grid { margin-top: 12px; display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 12px; }
.feature-card { border: 1px solid rgba(17, 34, 40, 0.1); border-radius: 14px; background: #fff; padding: 14px; transition: transform 0.2s ease, box-shadow 0.2s ease; }
.feature-card:hover { transform: translateY(-2px); box-shadow: 0 10px 22px rgba(12, 29, 39, 0.12); }
.feature-card h3 { margin: 8px 0 4px; }
.feature-card p { margin: 0; color: #5f737b; }
.developer { display: grid; grid-template-columns: minmax(0, 1.4fr) minmax(260px, 0.8fr); gap: 18px; align-items: center; }
.dev-copy p { color: #5a6d75; line-height: 1.68; }
.tags { display: flex; flex-wrap: wrap; gap: 8px; margin: 12px 0; }
.tags span { border-radius: 999px; background: rgba(17, 34, 40, 0.08); color: #233942; font-size: 0.78rem; padding: 5px 10px; }
.socials { display: flex; align-items: center; flex-wrap: wrap; gap: 10px; }
.socials a, .mail-btn { display: inline-grid; place-items: center; width: 34px; height: 34px; border-radius: 10px; border: 1px solid rgba(17, 34, 40, 0.13); color: #2e4750; background: #fff; }
.mail-btn { cursor: pointer; }
.email-text { font-size: 0.86rem; color: #52666e; }
.copied { font-size: 0.75rem; color: #0d6f4a; font-weight: 700; }
.dev-photo-wrap { display: grid; place-items: center; }
.photo { padding: 8px; border-radius: 20px; }
.photo img { display: block; width: 100%; max-width: 270px; border-radius: 14px; object-fit: cover; }
@media (max-width: 1080px) {
  .hero-metrics, .journey-grid, .feature-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .developer { grid-template-columns: 1fr; }
}
@media (max-width: 700px) {
  .hero-metrics, .journey-grid, .feature-grid { grid-template-columns: 1fr; }
  .journey-head { flex-direction: column; align-items: flex-start; }
}
</style>
