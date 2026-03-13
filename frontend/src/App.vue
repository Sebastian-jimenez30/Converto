<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from "vue";

const apiUrl = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

type FormatsResponse = {
  formats: Record<string, string[]>;
};

type JobResponse = {
  id: string;
  source_filename: string;
  source_format: string;
  target_format: string;
  status: string;
  source_key: string;
  result_key: string | null;
  error_message: string | null;
  created_at: string;
  updated_at: string;
};

type DownloadUrlResponse = {
  url: string;
};

const formats = ref<Record<string, string[]>>({});
const selectedFormat = ref("pdf");
const selectedFile = ref<File | null>(null);
const loadingFormats = ref(true);
const uploading = ref(false);
const isDragOver = ref(false);
const errorMessage = ref("");
const activeJob = ref<JobResponse | null>(null);
const downloadUrl = ref("");
const fileInputRef = ref<HTMLInputElement | null>(null);
let pollHandle: number | null = null;

const allFormats = computed(() =>
  Array.from(new Set(Object.values(formats.value).flat())).sort()
);

const formatGroups = computed(() => Object.entries(formats.value));

const canConvert = computed(
  () => !!selectedFile.value && !uploading.value && !loadingFormats.value
);

const statusText = computed(() => {
  if (!activeJob.value) return "Ready";
  if (activeJob.value.status === "queued") return "Queued";
  if (activeJob.value.status === "processing") return "Processing";
  if (activeJob.value.status === "done") return "Done";
  if (activeJob.value.status === "failed") return "Failed";
  return activeJob.value.status;
});

const statusClass = computed(() => {
  if (!activeJob.value) return "idle";
  if (activeJob.value.status === "queued") return "queued";
  if (activeJob.value.status === "processing") return "processing";
  if (activeJob.value.status === "done") return "done";
  if (activeJob.value.status === "failed") return "failed";
  return "idle";
});

const statusProgress = computed(() => {
  if (!activeJob.value) return 6;
  if (activeJob.value.status === "queued") return 34;
  if (activeJob.value.status === "processing") return 72;
  if (activeJob.value.status === "done") return 100;
  if (activeJob.value.status === "failed") return 100;
  return 6;
});

const shortJobId = computed(() => {
  if (!activeJob.value) return "-";
  return `${activeJob.value.id.slice(0, 8)}...${activeJob.value.id.slice(-6)}`;
});

const fileLabel = computed(() => {
  if (!selectedFile.value) return "Drop a file here or choose one";
  return `${selectedFile.value.name} (${prettySize(selectedFile.value.size)})`;
});

function prettySize(bytes: number): string {
  const units = ["B", "KB", "MB", "GB"];
  let value = bytes;
  let index = 0;
  while (value >= 1024 && index < units.length - 1) {
    value /= 1024;
    index += 1;
  }
  return `${value.toFixed(value < 10 && index > 0 ? 1 : 0)} ${units[index]}`;
}

function clearPolling() {
  if (pollHandle !== null) {
    window.clearInterval(pollHandle);
    pollHandle = null;
  }
}

function setSelectedFile(file: File | null) {
  selectedFile.value = file;
  if (file) {
    errorMessage.value = "";
  }
}

function triggerPicker() {
  fileInputRef.value?.click();
}

function onFileChange(event: Event) {
  const target = event.target as HTMLInputElement;
  const file = target.files && target.files.length > 0 ? target.files[0] : null;
  setSelectedFile(file);
}

function onDragOver(event: DragEvent) {
  event.preventDefault();
  isDragOver.value = true;
}

function onDragLeave(event: DragEvent) {
  event.preventDefault();
  isDragOver.value = false;
}

function onDrop(event: DragEvent) {
  event.preventDefault();
  isDragOver.value = false;
  const file =
    event.dataTransfer?.files && event.dataTransfer.files.length > 0
      ? event.dataTransfer.files[0]
      : null;
  setSelectedFile(file);
}

async function loadFormats() {
  try {
    const response = await fetch(`${apiUrl}/v1/capabilities/formats`);
    if (!response.ok) throw new Error("Could not load formats");
    const payload = (await response.json()) as FormatsResponse;
    formats.value = payload.formats;
    if (allFormats.value.length > 0) {
      selectedFormat.value = allFormats.value[0];
    }
  } catch {
    formats.value = {
      image: ["jpg", "png", "webp"],
      document: ["pdf", "docx", "txt"],
      audio: ["mp3", "wav"]
    };
    selectedFormat.value = "pdf";
  } finally {
    loadingFormats.value = false;
  }
}

async function fetchJob(jobId: string) {
  const response = await fetch(`${apiUrl}/v1/jobs/${jobId}`);
  if (!response.ok) throw new Error("Could not read job status");
  activeJob.value = (await response.json()) as JobResponse;
}

async function fetchDownloadUrl(jobId: string) {
  const response = await fetch(`${apiUrl}/v1/jobs/${jobId}/download`);
  if (!response.ok) return;
  const payload = (await response.json()) as DownloadUrlResponse;
  downloadUrl.value = payload.url;
}

async function pollJob(jobId: string) {
  try {
    await fetchJob(jobId);
    if (activeJob.value?.status === "done") {
      clearPolling();
      await fetchDownloadUrl(jobId);
      return;
    }
    if (activeJob.value?.status === "failed") {
      clearPolling();
      errorMessage.value = activeJob.value.error_message ?? "Conversion failed";
    }
  } catch (error) {
    clearPolling();
    errorMessage.value = error instanceof Error ? error.message : "Polling failed";
  }
}

function startPolling(jobId: string) {
  clearPolling();
  pollJob(jobId);
  pollHandle = window.setInterval(() => {
    pollJob(jobId);
  }, 2000);
}

async function submitConversion() {
  if (!selectedFile.value) {
    errorMessage.value = "Please select a file before converting";
    return;
  }

  uploading.value = true;
  errorMessage.value = "";
  activeJob.value = null;
  downloadUrl.value = "";
  clearPolling();

  try {
    const formData = new FormData();
    formData.append("file", selectedFile.value);
    formData.append("target_format", selectedFormat.value);

    const response = await fetch(`${apiUrl}/v1/jobs/upload`, {
      method: "POST",
      body: formData
    });

    if (!response.ok) {
      const errorBody = await response.json().catch(() => ({}));
      throw new Error(errorBody.detail ?? "Upload failed");
    }

    activeJob.value = (await response.json()) as JobResponse;
    startPolling(activeJob.value.id);
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : "Upload failed";
  } finally {
    uploading.value = false;
  }
}

onMounted(loadFormats);
onBeforeUnmount(clearPolling);
</script>

<template>
  <main class="app-shell">
    <div class="noise-layer"></div>
    <div class="aurora orb-a"></div>
    <div class="aurora orb-b"></div>
    <div class="aurora orb-c"></div>

    <header class="app-header reveal">
      <div class="brand">
        <div class="brand-mark">C</div>
        <div>
          <p class="brand-name">Converto</p>
          <p class="brand-sub">File Conversion Studio</p>
        </div>
      </div>
      <span class="pill-live">Live API</span>
    </header>

    <section class="hero reveal delay-1">
      <p class="eyebrow">Fast • Reliable • Modern</p>
      <h1>Convert files with a premium web experience.</h1>
      <p>
        Drag, drop, convert, and download with a clean workflow. Built for speed
        and designed to feel like a modern SaaS product from day one.
      </p>
    </section>

    <section class="workbench reveal delay-2">
      <article class="panel upload-panel">
        <h2>Start a conversion</h2>
        <p class="muted">
          Upload one file, choose target format, and launch processing.
        </p>
        <p class="beta-note">
          Current beta: only same-format processing is enabled (e.g., PDF to PDF).
        </p>

        <div
          class="dropzone"
          :class="{ drag: isDragOver, selected: !!selectedFile }"
          @dragover="onDragOver"
          @dragleave="onDragLeave"
          @drop="onDrop"
        >
          <input
            ref="fileInputRef"
            class="hidden-file"
            type="file"
            @change="onFileChange"
          />
          <p class="drop-title">{{ fileLabel }}</p>
          <button class="ghost-button" type="button" @click="triggerPicker">
            Choose file
          </button>
        </div>

        <div class="controls">
          <label for="format">Target format</label>
          <select id="format" v-model="selectedFormat" :disabled="loadingFormats">
            <option v-for="format in allFormats" :key="format" :value="format">
              {{ format.toUpperCase() }}
            </option>
          </select>
        </div>

        <button class="primary-action" :disabled="!canConvert" @click="submitConversion">
          {{ uploading ? "Uploading..." : "Convert now" }}
        </button>

        <p v-if="errorMessage" class="error-text">{{ errorMessage }}</p>
      </article>

      <article class="panel status-panel">
        <h2>Job monitor</h2>
        <div class="status-chip" :class="statusClass">{{ statusText }}</div>

        <div class="progress-track">
          <span class="progress-fill" :style="{ width: `${statusProgress}%` }"></span>
        </div>

        <dl class="meta-grid">
          <div>
            <dt>Job ID</dt>
            <dd>{{ shortJobId }}</dd>
          </div>
          <div>
            <dt>Source</dt>
            <dd>{{ activeJob?.source_format?.toUpperCase() || "-" }}</dd>
          </div>
          <div>
            <dt>Target</dt>
            <dd>{{ activeJob?.target_format?.toUpperCase() || selectedFormat.toUpperCase() }}</dd>
          </div>
          <div>
            <dt>API</dt>
            <dd>{{ apiUrl.replace("http://", "") }}</dd>
          </div>
        </dl>

        <a
          v-if="downloadUrl"
          class="download-action"
          :href="downloadUrl"
          target="_blank"
          rel="noopener noreferrer"
        >
          Download converted file
        </a>
      </article>
    </section>

    <section class="format-catalog reveal delay-3">
      <h3>Supported format families</h3>
      <div class="format-grid">
        <article v-for="[family, values] in formatGroups" :key="family" class="format-card">
          <p class="family-name">{{ family }}</p>
          <p class="family-values">{{ values.join(" • ") }}</p>
        </article>
      </div>
    </section>
  </main>
</template>
