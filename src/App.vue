<script setup>
import { computed, onMounted, onUnmounted, ref, watch } from 'vue';
import { DATA_SOURCE_INFO, catalog } from './data/catalog/index.js';

// Tema claro/oscuro: arranca según la preferencia del sistema y se recuerda en localStorage.
const THEME_KEY = 'nawi-theme';
const THEME_COLORS = { dark: '#1d2021', light: '#ebdbb2' };

function readStoredTheme() {
  try {
    const saved = window.localStorage.getItem(THEME_KEY);
    return saved === 'light' || saved === 'dark' ? saved : null;
  } catch {
    return null;
  }
}

// Oscuro por defecto (regla de la guía); el claro es una elección explícita y se recuerda.
const theme = ref(readStoredTheme() ?? 'dark');
const isLight = computed(() => theme.value === 'light');

watch(theme, (value) => {
  document.documentElement.dataset.theme = value;
  document.documentElement.style.colorScheme = value;
  document.querySelector('meta[name="theme-color"]')?.setAttribute('content', THEME_COLORS[value]);
  try {
    window.localStorage.setItem(THEME_KEY, value);
  } catch {
    /* modo privado: el tema vale solo para esta sesión */
  }
}, { immediate: true });

function toggleTheme() {
  theme.value = isLight.value ? 'dark' : 'light';
}

// Catálogo y cuadros vienen de la capa de datos intercambiable (src/data/catalog).
// Hoy la respalda el mock; cuando existan los endpoints pasa a la API sin tocar la vista.
const objects = ref([]);
const frames = ref([]);
const loading = ref(true);
const loadError = ref('');

const objectId = ref('');
const frameIndex = ref(0);
const playing = ref(false);
const compare = ref(false);
const query = ref('');
const notice = ref('');

const selectedObject = computed(() => objects.value.find((item) => item.id === objectId.value) ?? objects.value[0] ?? null);
const frame = computed(() => frames.value[frameIndex.value] ?? null);
const previousFrame = computed(() => frames.value[Math.max(0, frameIndex.value - 1)] ?? null);
const filteredObjects = computed(() => objects.value.filter((item) => `${item.name} ${item.kind}`.toLowerCase().includes(query.value.toLowerCase())));
const ready = computed(() => !loading.value && !loadError.value && Boolean(selectedObject.value) && Boolean(frame.value));
const progressPercent = computed(() => (frames.value.length > 1 ? (frameIndex.value / (frames.value.length - 1)) * 100 : 0));

// Lo que se puede afirmar según el estado de la fuente. 'pending' no se disfraza
// de datos del backend: se avisa que no hay nada conectado.
const SOURCE_COPY = {
  demo: {
    title: 'Catálogo de demostración',
    note: `${DATA_SOURCE_INFO.label} · cifras ilustrativas, no validadas.`,
  },
  live: {
    title: 'Catálogo del backend',
    note: `${DATA_SOURCE_INFO.label} · datos del backend.`,
  },
  pending: {
    title: 'Catálogo sin conectar',
    note: `${DATA_SOURCE_INFO.label} no está conectada: no hay datos que mostrar.`,
  },
};

const sourceCopy = SOURCE_COPY[DATA_SOURCE_INFO.status] ?? SOURCE_COPY.pending;
const dataSourceNote = sourceCopy.note;

async function loadFrames() {
  frames.value = objectId.value ? await catalog.listFrames(objectId.value) : [];
  if (frameIndex.value >= frames.value.length) frameIndex.value = 0;
}

// Único punto de carga: si mañana la fuente es la API, el resto de la vista no cambia.
async function loadCatalog() {
  loading.value = true;
  loadError.value = '';
  try {
    // Se leen los parámetros acá para respetar un enlace compartido (?obj=&frame=).
    const params = new URLSearchParams(window.location.search);
    objects.value = await catalog.listObjects();

    const requestedObject = params.get('obj');
    objectId.value = objects.value.some((item) => item.id === requestedObject)
      ? requestedObject
      : (objects.value[0]?.id ?? '');

    await loadFrames();

    const requestedFrame = Number(params.get('frame'));
    frameIndex.value = Number.isInteger(requestedFrame) && requestedFrame >= 0 && requestedFrame < frames.value.length
      ? requestedFrame
      : 0;
  } catch (error) {
    objects.value = [];
    frames.value = [];
    loadError.value = error?.message || 'No se pudo cargar el catálogo.';
  } finally {
    loading.value = false;
  }
}

watch([objectId, frameIndex], () => {
  if (loading.value || loadError.value) return;
  const nextParams = new URLSearchParams(window.location.search);
  nextParams.set('obj', objectId.value);
  nextParams.set('frame', String(frameIndex.value));
  window.history.replaceState({}, '', `${window.location.pathname}?${nextParams.toString()}`);
});

watch([playing, frames], ([isPlaying], _previous, onCleanup) => {
  if (!isPlaying || frames.value.length < 2) return;
  const timer = window.setInterval(() => {
    frameIndex.value = (frameIndex.value + 1) % frames.value.length;
  }, 1800);
  onCleanup(() => window.clearInterval(timer));
});

async function chooseObject(id) {
  playing.value = false;
  objectId.value = id;
  await loadFrames();
  frameIndex.value = 0;
}

function handleKeyDown(event) {
  if (event.target instanceof HTMLInputElement) return;
  if (!frames.value.length) return;
  if (event.key === 'ArrowRight') frameIndex.value = (frameIndex.value + 1) % frames.value.length;
  if (event.key === 'ArrowLeft') frameIndex.value = (frameIndex.value - 1 + frames.value.length) % frames.value.length;
}

async function shareView() {
  try {
    await navigator.clipboard.writeText(window.location.href);
    notice.value = 'Enlace copiado';
  } catch {
    notice.value = 'Copiá el enlace desde la barra del navegador';
  }
  window.setTimeout(() => { notice.value = ''; }, 2400);
}

onMounted(() => {
  loadCatalog();
  window.addEventListener('keydown', handleKeyDown);
});
onUnmounted(() => window.removeEventListener('keydown', handleKeyDown));
</script>

<template>
  <main class="app-shell">
    <header class="topbar">
      <a class="brand" href="#inicio" aria-label="Nawi, inicio"><span class="brand-mark"><i class="bi bi-eye-fill" /></span><span>nawi<span class="brand-dot">.</span></span></a>
      <div class="mission-label"><span class="live-dot" /> EXPLORADOR INFRARROJO <span class="label-divider">/</span> SPHEREx</div>
      <div class="topbar-actions">
        <button class="icon-button theme-button" :title="isLight ? 'Cambiar a modo oscuro' : 'Cambiar a modo claro'" :aria-label="isLight ? 'Cambiar a modo oscuro' : 'Cambiar a modo claro'" :aria-pressed="isLight" @click="toggleTheme"><i class="bi" :class="isLight ? 'bi-moon-stars' : 'bi-brightness-high'" /></button>
        <button class="icon-button help-button" title="Acerca de Nawi" aria-label="Acerca de Nawi"><i class="bi bi-question-lg" /></button>
      </div>
    </header>

    <section id="inicio" class="intro-row">
      <div><div class="eyebrow"><span>01</span> OBSERVATORIO DIGITAL</div><h1>El cielo cambia.<br /><span>Ahora podés verlo.</span></h1><p class="intro-copy">Viajá a través de observaciones infrarrojas reales y seguí las huellas que dejan los objetos celestes.</p></div>
      <div class="mission-stat"><span class="stat-icon"><i class="bi bi-stars" /></span><div><strong>102</strong><span>bandas infrarrojas</span></div><div class="stat-rule" /><div><strong>6 <small>meses</small></strong><span>entre mapeos del cielo</span></div></div>
    </section>

    <div class="workspace container-fluid px-0">
      <div class="row g-3 align-items-start">
        <aside class="col-12 col-lg-3">
          <div class="sidebar panel">
            <div class="panel-heading"><div><span class="eyebrow">EXPLORAR</span><h2>Elegí un objeto</h2></div><span class="count-pill">{{ objects.length }}</span></div>
            <label class="search-box"><i class="bi bi-search" /><input v-model="query" placeholder="Buscar objeto..." aria-label="Buscar objeto" /><kbd>/</kbd></label>
            <div class="object-list" role="listbox" aria-label="Objetos astronómicos">
              <button v-for="(object, index) in filteredObjects" :key="object.id" class="object-option" :class="{ selected: object.id === objectId }" role="option" :aria-selected="object.id === objectId" @click="chooseObject(object.id)">
                <span class="object-index" :class="{ active: object.id === objectId }">{{ String(index + 1).padStart(2, '0') }}</span><span class="object-copy"><strong>{{ object.name }}</strong><small>{{ object.kind }}</small></span><span class="object-chevron"><i class="bi bi-arrow-up-right" /></span>
              </button>
              <div v-if="loading" class="empty-search">Cargando catálogo…</div>
              <div v-else-if="loadError" class="empty-search">{{ loadError }}</div>
              <div v-else-if="!filteredObjects.length" class="empty-search">No hay objetos con ese nombre.</div>
            </div>
            <div class="sidebar-bottom"><span class="status-check"><i class="bi bi-check2" /></span><span>{{ sourceCopy.title }}<br /><small>{{ dataSourceNote }}</small></span></div>
          </div>
        </aside>

        <section class="col-12 col-lg-9 viewer-column">
          <div v-if="ready" class="viewer panel">
            <div class="viewer-toolbar"><div><span class="eyebrow">CAMPO CELESTE <span class="toolbar-slash">/</span> {{ selectedObject.tag }}</span><h2>{{ selectedObject.name }}</h2></div><button class="share-button" @click="shareView"><i class="bi bi-share" /><span>Compartir vista</span></button></div>
            <div class="sky-stage" :class="{ comparison: compare }">
              <div class="image-layer" :style="{ backgroundImage: `url(${frame.url})` }" />
              <div class="sky-vignette" />
              <div class="sky-grid" />
              <div class="image-caption"><span class="caption-dot" /> {{ frame.illustrative ? 'IMAGEN ILUSTRATIVA · DATOS REALES PENDIENTES' : 'DATOS DEL BACKEND' }}</div>
              <div v-if="selectedObject.coordinates" class="coordinate-label" :title="selectedObject.coordinates.note"><i class="bi bi-exclamation-triangle" /> {{ selectedObject.coordinates.ra }} <span>/</span> {{ selectedObject.coordinates.dec }} · {{ selectedObject.coordinates.statusLabel }}</div>
              <div v-else class="coordinate-label"><i class="bi bi-hourglass-split" /> COORDENADAS PENDIENTES <span>/</span> NO VALIDADAS</div>
              <div class="target-marker"><span /><i /></div>
              <div class="target-label">OBJETO SELECCIONADO</div>
              <div v-if="compare" class="compare-wipe" :style="{ backgroundImage: `url(${previousFrame.url})` }"><span class="wipe-label">ANTERIOR · {{ previousFrame.date }}{{ previousFrame.illustrative ? ' · ILUSTRATIVO' : '' }}</span><span class="wipe-line" /></div>
              <div class="image-date"><span>{{ frame.date }}</span><small>{{ frame.band }}</small></div>
            </div>
            <div class="timeline">
              <div class="timeline-top"><span class="timeline-title"><i class="bi bi-clock-history" /> LÍNEA DE TIEMPO ILUSTRATIVA</span><span class="frame-counter">CUADRO <b>{{ String(frameIndex + 1).padStart(2, '0') }}</b> <span>/ {{ String(frames.length).padStart(2, '0') }}</span></span></div>
              <input v-model.number="frameIndex" class="time-range" :style="{ '--progress': `${progressPercent}%` }" type="range" min="0" :max="frames.length - 1" step="1" aria-label="Elegir cuadro ilustrativo" />
              <div class="timeline-dates"><button v-for="(item, index) in frames" :key="item.date" class="date-tick" :class="{ current: index === frameIndex }" @click="frameIndex = index">{{ item.date.slice(5) }}</button></div>
            </div>
            <div class="player-controls"><div class="transport"><button class="control-button" aria-label="Cuadro anterior" @click="frameIndex = (frameIndex - 1 + frames.length) % frames.length"><i class="bi bi-skip-backward-fill" /></button><button class="play-button" :aria-label="playing ? 'Pausar' : 'Reproducir'" @click="playing = !playing"><i class="bi" :class="playing ? 'bi-pause-fill' : 'bi-play-fill'" /></button><button class="control-button" aria-label="Cuadro siguiente" @click="frameIndex = (frameIndex + 1) % frames.length"><i class="bi bi-skip-forward-fill" /></button><span class="play-caption">{{ playing ? 'REPRODUCIENDO' : 'RECORRER CUADROS' }}</span></div><button class="compare-button" :class="{ 'is-on': compare }" @click="compare = !compare"><i class="bi bi-layout-split" /> <span>{{ compare ? 'Cerrar comparación' : 'Antes y después' }}</span></button></div>
          </div>
          <div v-else class="viewer panel">
            <div class="viewer-toolbar"><div><span class="eyebrow">CAMPO CELESTE</span><h2>{{ loading ? 'Cargando catálogo…' : 'Catálogo no disponible' }}</h2></div></div>
            <div class="sky-stage" style="display: flex; align-items: center; justify-content: center; padding: 24px; text-align: center"><p style="max-width: 46ch; margin: 0; color: var(--text-secondary); font-size: 13px">{{ loadError || 'Preparando los objetos de demostración.' }}</p></div>
          </div>
          <div class="below-viewer"><span><i class="bi bi-info-circle" /> {{ ready ? selectedObject.demoUse : 'Esta experiencia está en desarrollo.' }} <span class="caption-divider">·</span> {{ dataSourceNote }}</span><span class="keyboard-hint">NAVEGÁ CON <kbd>←</kbd> <kbd>→</kbd></span></div>
        </section>
      </div>
    </div>

    <footer class="footer"><span>NAWI <span class="footer-dot">·</span> UN OJO INFRARROJO PARA TODOS</span><span>DATOS DE MISIÓN SPHEREx <i class="bi bi-arrow-up-right" /></span></footer>
    <div v-if="notice" class="toast-note" role="status"><i class="bi bi-check-circle-fill" /> {{ notice }}</div>
  </main>
</template>
