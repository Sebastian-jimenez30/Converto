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
const errorMessage = ref("");
const activeJob = ref<JobResponse | null>(null);
const downloadUrl = ref("");
let pollHandle: number | null = null;

const allFormats = computed(() =>
  Array.from(new Set(Object.values(formats.value).flat())).sort()
);

function clearPolling() {
  if (pollHandle !== null) {
    window.clearInterval(pollHandle);
    pollHandle = null;
  }
}

async function loadFormats() {
  try {
    const response = await fetch(`${apiUrl}/v1/capabilities/formats`);
    if (!response.ok) {
      throw new Error("Could not load formats");
    }
    const payload = (await response.json()) as FormatsResponse;
    formats.value = payload.formats;
    if (allFormats.value.length > 0) {
      selectedFormat.value = allFormats.value[0];
    }
  } catch {
    formats.value = {
      image: ["jpg", "png", "webp"],
      document: ["pdf", "docx", "txt"]
    };
    selectedFormat.value = "pdf";
  } finally {
    loadingFormats.value = false;
  }
}

function onFileChange(event: Event) {
  const target = event.target as HTMLInputElement;
  selectedFile.value = target.files && target.files.length > 0 ? target.files[0] : null;
}

async function fetchJob(jobId: string) {
  const response = await fetch(`${apiUrl}/v1/jobs/${jobId}`);
  if (!response.ok) {
    throw new Error("Could not read job status");
  }
  activeJob.value = (await response.json()) as JobResponse;
}

async function fetchDownloadUrl(jobId: string) {
  const response = await fetch(`${apiUrl}/v1/jobs/${jobId}/download`);
  if (!response.ok) {
    return;
  }
  const payload = (await response.json()) as DownloadUrlResponse;
  downloadUrl.value = payload.url;
}

async function pollJob(jobId: string) {
  try {
    await fetchJob(jobId);
    if (activeJob.value?.status === "done") {
      clearPolling();
      await fetchDownloadUrl(jobId);
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
    errorMessage.value = "Select a file first";
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
  <main class="container">
    <section class="card">
      <p class="eyebrow">Converto MVP</p>
      <h1>File conversion with hexagonal architecture</h1>
      <p class="lead">
        Upload a file, create a conversion job, track status, and download the
        result when ready.
      </p>

      <div class="upload-mock">
        <label for="file" class="label">Source file</label>
        <input id="file" type="file" @change="onFileChange" />

        <label for="format" class="label">Target format</label>
        <select id="format" v-model="selectedFormat" :disabled="loadingFormats">
          <option v-for="format in allFormats" :key="format" :value="format">
            {{ format.toUpperCase() }}
          </option>
        </select>

        <button type="button" :disabled="uploading || loadingFormats" @click="submitConversion">
          {{ uploading ? "Uploading..." : "Convert" }}
        </button>
      </div>

      <p v-if="errorMessage" class="error-text">{{ errorMessage }}</p>
    </section>

    <section class="card">
      <h2>Job status</h2>
      <ul>
        <li>Frontend: Vue 3 + Vite</li>
        <li>API URL: <code>{{ apiUrl }}</code></li>
        <li>
          Supported formats:
          <code v-if="!loadingFormats">{{ allFormats.join(", ") || "none" }}</code>
          <code v-else>loading...</code>
        </li>
        <li v-if="activeJob">Job ID: <code>{{ activeJob.id }}</code></li>
        <li v-if="activeJob">Current status: <strong>{{ activeJob.status }}</strong></li>
      </ul>

      <a
        v-if="downloadUrl"
        class="download-link"
        :href="downloadUrl"
        target="_blank"
        rel="noopener noreferrer"
      >
        Download result
      </a>
    </section>
  </main>
</template>

