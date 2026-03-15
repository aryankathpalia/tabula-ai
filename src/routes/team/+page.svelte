<script lang="ts">
import { tick } from 'svelte';
import FileText from 'lucide-svelte/icons/file-text';
import { marked } from 'marked';
import { onMount } from 'svelte';

let fileName: string | null = null;
let documentId: number | null = null;

type Message = {
  role: 'user' | 'assistant';
  content: string;
  sources?: { snippet: string }[];
};

let messages: Message[] = [];
let question = '';

let loading = false;
let uploading = false;

async function uploadFile(event: Event) {
  const target = event.target as HTMLInputElement;
  const selectedFile = target.files?.[0];
  if (!selectedFile) return;

  fileName = selectedFile.name;

  const formData = new FormData();
  formData.append('file', selectedFile);

  uploading = true;

  try {
    const res = await fetch(`${import.meta.env.VITE_API_URL}/documents/chat-upload`, {
      method: 'POST',
      body: formData
    });

    if (!res.ok) {
      alert('Upload failed');
      uploading = false;
      return;
    }

    const data = await res.json();
    documentId = data.document_id;
  } catch (err) {
    console.error(err);
    alert('Upload error');
  }

  uploading = false;
}

async function sendMessage(): Promise<void> {
  if (!question.trim() || !documentId) return;

  const q = question;

  const userMessage: Message = {
    role: 'user',
    content: q
  };

  messages = [...messages, userMessage];
  question = '';
  loading = true;

  try {
    const res = await fetch(
      `${import.meta.env.VITE_API_URL}/documents/${documentId}/chat`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          question: q,
          history: messages.slice(-6)
        })
      }
    );

    if (!res.ok) {
      alert('Chat request failed');
      loading = false;
      return;
    }

    const data = await res.json();

    const aiMessage: Message = {
      role: 'assistant',
      content: data.answer,
      sources: data.sources
    };

    messages = [...messages, aiMessage];
  } catch (err) {
    console.error(err);
    alert('Chat error');
  }

  loading = false;
  await tick();

  document.querySelector('.chat')?.scrollTo({
    top: 999999,
    behavior: 'smooth'
  });
}

function removeFile() {
  fileName = null;
  documentId = null;
  messages = [];
}

onMount(async () => {
  const params = new URLSearchParams(window.location.search);
  const docId = params.get('documentId');
  if (!docId) return;

  documentId = Number(docId);

  try {
    const res = await fetch(`${import.meta.env.VITE_API_URL}/documents/${docId}`);
    const doc = await res.json();
    fileName = doc.filename;
  } catch (err) {
    console.error('Failed to load document info');
  }

  loading = true;

  try {
    const res = await fetch(
      `${import.meta.env.VITE_API_URL}/documents/${documentId}/chat`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          question: 'Summarize this contract and highlight key obligations, liabilities, termination terms, and risks.',
          history: []
        })
      }
    );

    const data = await res.json();

    messages = [{
      role: 'assistant',
      content: data.answer
    }];
  } catch (err) {
    console.error(err);
  }

  loading = false;
});
</script>

<div class="team-page space-y-5">
  <section class="panel p-6 md:p-8 team-hero">
    <p class="hero-kicker">Conversational Layer</p>
    <h1>Chat with your Document</h1>
    <p>Upload a contract and ask direct legal questions with context-aware AI assistance.</p>

    <div class="prompt" data-tour="upload">
      <label class="upload-btn">
        +
        <input type="file" on:change={uploadFile} hidden />
      </label>

      {#if fileName}
        <div class="file-chip">
          <div class="file-icon">
            <FileText size={20} stroke-width={2} />
          </div>
          <span class="file-name">{fileName}</span>
          <button class="remove-file" on:click={removeFile}>x</button>
        </div>
      {/if}

      <textarea
        bind:value={question}
        rows="1"
        placeholder="Upload a document or ask about it..."
        on:keydown={(e) => {
          if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
          }
        }}
      ></textarea>

      <button
        class="btn btn-primary"
        on:click={sendMessage}
        disabled={!documentId || loading || uploading}
      >
        {uploading ? 'Uploading...' : loading ? 'Thinking...' : 'Ask'}
      </button>
    </div>
  </section>

  {#if messages.length > 0}
    <section class="panel-strong chat">
      {#each messages as msg}
        <div class="message {msg.role}">
          <div class="bubble">{@html marked(msg.content)}</div>
        </div>
      {/each}

      {#if loading}
        <div class="message assistant">
          <div class="bubble">Thinking...</div>
        </div>
      {/if}
    </section>
  {/if}
</div>

<style>
.team-hero {
  background: linear-gradient(120deg, rgba(14, 164, 107, 0.15), rgba(32, 149, 232, 0.1));
}

.hero-kicker {
  margin: 0;
  font-size: 0.74rem;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  font-weight: 700;
  color: #0d6f4a;
}

.team-hero h1 {
  margin: 8px 0 4px;
}

.team-hero p {
  margin: 0;
  color: #5f7279;
}

.prompt {
  margin-top: 14px;
  display: flex;
  align-items: center;
  gap: 10px;
  border: 1px solid rgba(17, 34, 40, 0.15);
  border-radius: 14px;
  padding: 10px;
  background: rgba(255, 255, 255, 0.84);
}

.upload-btn {
  display: grid;
  place-items: center;
  width: 34px;
  height: 34px;
  border-radius: 10px;
  background: rgba(17, 34, 40, 0.08);
  cursor: pointer;
  font-weight: 700;
}

.file-chip {
  position: relative;
  display: flex;
  align-items: center;
  gap: 6px;
  background: rgba(17, 34, 40, 0.08);
  border-radius: 10px;
  padding: 6px;
}

.file-name {
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 0.85rem;
}

.remove-file {
  border: none;
  background: #c53a4f;
  color: white;
  width: 18px;
  height: 18px;
  border-radius: 999px;
  font-size: 0.72rem;
}

.prompt textarea {
  flex: 1;
  border: none;
  background: transparent;
  resize: none;
  outline: none;
  min-height: 34px;
  max-height: 120px;
  padding: 6px;
}

.chat {
  max-height: calc(100vh - 290px);
  overflow-y: auto;
  padding: 14px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.message {
  display: flex;
}

.message.user {
  justify-content: flex-end;
}

.message.assistant {
  justify-content: flex-start;
}

.bubble {
  max-width: min(760px, 92%);
  border-radius: 14px;
  border: 1px solid rgba(17, 34, 40, 0.1);
  background: #fff;
  padding: 12px 14px;
  line-height: 1.62;
}

.message.user .bubble {
  background: linear-gradient(130deg, #0ea46b, #0b8556);
  color: white;
  border: none;
}

:global(.bubble p) {
  margin: 0 0 8px;
}

:global(.bubble ul) {
  margin: 0 0 8px 18px;
}

:global(.bubble h1),
:global(.bubble h2),
:global(.bubble h3) {
  margin: 0 0 8px;
}

@media (max-width: 820px) {
  .prompt {
    flex-wrap: wrap;
  }

  .prompt textarea {
    order: 3;
    width: 100%;
  }
}
</style>
