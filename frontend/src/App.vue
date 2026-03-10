<script setup lang="ts">
import { computed, onMounted, ref } from "vue";

const apiUrl = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

type FormatsResponse = {
  formats: Record<string, string[]>;
};

const formats = ref<Record<string, string[]>>({});
const selected = ref("pdf");
const loading = ref(true);

const allFormats = computed(() =>
  Array.from(new Set(Object.values(formats.value).flat())).sort()
);

onMounted(async () => {
  try {
    const response = await fetch(`${apiUrl}/v1/capabilities/formats`);
    if (!response.ok) {
      throw new Error("Failed to fetch formats");
    }
    const payload = (await response.json()) as FormatsResponse;
    formats.value = payload.formats;
    if (allFormats.value.length > 0) {
      selected.value = allFormats.value[0];
    }
  } catch {
    formats.value = {
      image: ["jpg", "png", "webp"],
      document: ["pdf", "docx", "txt"]
    };
  } finally {
    loading.value = false;
  }
});
</script>

<template>
  <main class="container">
    <section class="card">
      <p class="eyebrow">Converto MVP</p>
      <h1>Conversión de archivos con arquitectura hexagonal</h1>
      <p class="lead">
        Base inicial lista con Vue + Vite en frontend y backend orientado a
        puertos y adaptadores.
      </p>

      <div class="upload-mock">
        <label for="file" class="label">Archivo origen</label>
        <input id="file" type="file" />

        <label for="format" class="label">Formato destino</label>
        <select id="format" v-model="selected" :disabled="loading">
          <option v-for="format in allFormats" :key="format" :value="format">
            {{ format.toUpperCase() }}
          </option>
        </select>

        <button type="button" disabled>Convertir (pendiente integración)</button>
      </div>
    </section>

    <section class="card">
      <h2>Estado técnico</h2>
      <ul>
        <li>Frontend: Vue 3 + Vite</li>
        <li>API URL: <code>{{ apiUrl }}</code></li>
        <li>Backend: Hexagonal (domain / application / adapters)</li>
        <li>
          Formatos soportados:
          <code v-if="!loading">{{ allFormats.join(", ") || "sin datos" }}</code>
          <code v-else>cargando...</code>
        </li>
      </ul>
    </section>
  </main>
</template>
