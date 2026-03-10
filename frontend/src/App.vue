<script setup lang="ts">
const apiUrl = import.meta.env.VITE_API_URL ?? "http://localhost:8000";
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
        <select id="format">
          <option value="pdf">PDF</option>
          <option value="docx">DOCX</option>
          <option value="png">PNG</option>
          <option value="jpg">JPG</option>
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
      </ul>
    </section>
  </main>
</template>

