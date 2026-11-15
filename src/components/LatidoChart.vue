<script setup>
/**
 * Latido: curva de brillo en SVG puro, sin librerías.
 *
 * Recibe las mediciones tal como las entrega el backend
 * ({ fecha, flujo, error, longitud_onda_um }) y no recalcula ni corrige nada:
 * solo dibuja. Si no hay mediciones válidas muestra un estado vacío, sin ejes
 * inventados.
 */
import { computed } from 'vue';

const props = defineProps({
  puntos: { type: Array, default: () => [] },
  nombre: { type: String, default: '' },
  motivo: { type: String, default: '' },
  cargando: { type: Boolean, default: false },
});

const MESES = ['ene', 'feb', 'mar', 'abr', 'may', 'jun', 'jul', 'ago', 'sep', 'oct', 'nov', 'dic'];

// Geometría del lienzo (viewBox): el SVG escala solo, sin deformarse.
const ANCHO = 660;
const ALTO = 300;
const M = { top: 24, right: 20, bottom: 52, left: 68 };
const anchoUtil = ANCHO - M.left - M.right;
const altoUtil = ALTO - M.top - M.bottom;

/** 'YYYY-MM-DD' -> ms UTC (mediodía no hace falta: nunca se muestra hora). */
function aFecha(texto) {
  const partes = /^(\d{4})-(\d{2})-(\d{2})$/.exec(String(texto ?? '').trim());
  if (!partes) return null;
  const t = Date.UTC(Number(partes[1]), Number(partes[2]) - 1, Number(partes[3]));
  return Number.isFinite(t) ? t : null;
}

function fechaCorta(t) {
  const d = new Date(t);
  return `${String(d.getUTCDate()).padStart(2, '0')} ${MESES[d.getUTCMonth()]}`;
}

function numero(valor) {
  const n = Number(valor);
  return Number.isFinite(n) ? n : null;
}

function formatear(valor) {
  const abs = Math.abs(valor);
  const decimales = abs >= 100 ? 1 : abs >= 1 ? 2 : abs >= 0.01 ? 3 : 4;
  return valor.toFixed(decimales);
}

// Un paso "lindo" para el eje: 1, 2 o 5 por potencia de diez.
function pasoLindo(rango) {
  if (!(rango > 0)) return 1;
  const bruto = rango / 4;
  const base = 10 ** Math.floor(Math.log10(bruto));
  const factor = bruto / base;
  const multiplo = factor <= 1 ? 1 : factor <= 2 ? 2 : factor <= 5 ? 5 : 10;
  return multiplo * base;
}

const puntosValidos = computed(() => {
  const limpios = (props.puntos ?? [])
    .map((punto, orden) => {
      const t = aFecha(punto?.fecha ?? punto?.date);
      const flujo = numero(punto?.flujo ?? punto?.brillo);
      if (t === null || flujo === null) return null;
      const error = numero(punto?.error);
      const lambda = numero(punto?.longitud_onda_um ?? punto?.longitudOndaUm);
      return { orden, t, flujo, error, lambda, fechaTexto: String(punto?.fecha ?? punto?.date).slice(0, 10) };
    })
    .filter(Boolean)
    .sort((a, b) => a.t - b.t);

  if (!limpios.length) return [];

  const flujos = limpios.map((p) => p.flujo);
  const min = Math.min(...flujos);
  const max = Math.max(...flujos);
  // Serie plana: se abre un margen para que la línea no quede pegada al borde.
  const margen = min === max ? Math.max(Math.abs(min) * 0.05, 0.5) : (max - min) * 0.12;
  const yMin = min - margen;
  const yMax = max + margen;

  const tMin = limpios[0].t;
  const tMax = limpios[limpios.length - 1].t;
  const rangoT = tMax - tMin || 1;

  const x = (t) => (limpios.length === 1 ? M.left + anchoUtil / 2 : M.left + ((t - tMin) / rangoT) * anchoUtil);
  const y = (v) => M.top + altoUtil - ((v - yMin) / (yMax - yMin)) * altoUtil;

  // La etiqueta de longitud de onda se anota solo si hay pocas mediciones:
  // con muchas, el gráfico se vuelve ilegible y el dato queda en el tooltip.
  const anotarLambda = limpios.length <= 10;

  return limpios.map((p) => {
    const detalle = [`${p.fechaTexto} · flujo ${formatear(p.flujo)}`];
    if (p.error !== null) detalle.push(`± ${formatear(p.error)}`);
    if (p.lambda !== null) detalle.push(`${p.lambda} μm`);
    // La etiqueta de la longitud de onda se corre hacia adentro del gráfico
    // cuando el punto cae sobre un borde, para no chocar con el eje.
    const cercaDelBorde = p.x < M.left + 34 || p.x > ANCHO - M.right - 34;
    const anclaje = p.x < M.left + 34 ? 'start' : p.x > ANCHO - M.right - 34 ? 'end' : 'middle';
    const desplazamiento = anclaje === 'start' ? 8 : anclaje === 'end' ? -8 : 0;
    const arriba = y(p.flujo) - 12 < M.top + 6;

    return {
      ...p,
      x: x(p.t),
      y: y(p.flujo),
      etiqueta: anotarLambda && p.lambda !== null ? `${p.lambda} μm` : '',
      etiquetaX: x(p.t) + desplazamiento,
      etiquetaY: arriba ? y(p.flujo) + 17 : y(p.flujo) - 12,
      etiquetaAnclaje: anclaje,
      cercaDelBorde,
      tooltip: detalle.join(' · '),
    };
  });
});

const dominio = computed(() => {
  if (!puntosValidos.value.length) return null;
  const flujos = puntosValidos.value.map((p) => p.flujo);
  const min = Math.min(...flujos);
  const max = Math.max(...flujos);
  const margen = min === max ? Math.max(Math.abs(min) * 0.05, 0.5) : (max - min) * 0.12;
  return { yMin: min - margen, yMax: max + margen, tMin: puntosValidos.value[0].t, tMax: puntosValidos.value[puntosValidos.value.length - 1].t };
});

const escalaY = computed(() => {
  if (!dominio.value) return { min: 0, max: 1 };
  return { min: dominio.value.yMin, max: dominio.value.yMax };
});

const y = (valor) => {
  const { min, max } = escalaY.value;
  const rango = max - min || 1;
  return M.top + altoUtil - ((valor - min) / rango) * altoUtil;
};

const ticksY = computed(() => {
  const { min, max } = escalaY.value;
  const paso = pasoLindo(max - min);
  const primero = Math.ceil(min / paso) * paso;
  const ticks = [];
  for (let v = primero; v <= max + paso * 0.001 && ticks.length < 6; v += paso) {
    ticks.push({ valor: v, y: y(v), label: formatear(v) });
  }
  return ticks;
});

const ticksX = computed(() => {
  const puntos = puntosValidos.value;
  if (!puntos.length) return [];
  if (puntos.length === 1) return [{ x: puntos[0].x, label: fechaCorta(puntos[0].t) }];
  const candidatos = [puntos[0], puntos[Math.floor((puntos.length - 1) / 2)], puntos[puntos.length - 1]];
  // Evita repetir la misma fecha si hay dos mediciones el mismo día.
  const vistos = new Set();
  return candidatos
    .filter((p) => {
      const clave = p.t;
      if (vistos.has(clave)) return false;
      vistos.add(clave);
      return true;
    })
    .map((p) => ({ x: p.x, label: fechaCorta(p.t) }));
});

const linea = computed(() => puntosValidos.value.map((p) => `${p.x.toFixed(1)},${p.y.toFixed(1)}`).join(' '));

const descripcion = computed(() => {
  const puntos = puntosValidos.value;
  const quien = props.nombre ? ` de ${props.nombre}` : '';
  if (!puntos.length) return `Curva de brillo${quien}: sin datos de brillo todavía.`;
  const desde = fechaCorta(puntos[0].t);
  const hasta = fechaCorta(puntos[puntos.length - 1].t);
  const rango = `${desde} y ${hasta}`;
  const medida = puntos.length === 1 ? `${puntos.length} medición (${rango})` : `${puntos.length} mediciones entre ${rango}`;
  return `Curva de brillo${quien}: ${medida}. Valores tal como los entrega el backend, sin recálculo.`;
});

const hayLambda = computed(() => puntosValidos.value.some((p) => p.lambda !== null));
</script>

<template>
  <div class="latido-chart">
    <div v-if="cargando" class="latido-estado" role="status">
      <i class="bi bi-hourglass-split" />
      <p>Cargando el latido…</p>
    </div>

    <div v-else-if="!puntosValidos.length" class="latido-estado latido-vacio">
      <i class="bi bi-activity" />
      <div>
        <strong>Sin datos de brillo todavía</strong>
        <p v-if="motivo">El backend informó: {{ motivo }}</p>
        <p v-else>Cuando el backend publique las mediciones, la curva aparece acá. No se dibujan ejes ni puntos inventados.</p>
      </div>
    </div>

    <template v-else>
      <svg class="latido-svg" :viewBox="`0 0 ${ANCHO} ${ALTO}`" role="img" :aria-label="descripcion" preserveAspectRatio="xMidYMid meet">
        <title>{{ descripcion }}</title>

        <g class="latido-ejes" aria-hidden="true">
          <line v-for="tick in ticksY" :key="`grid-${tick.valor}`" class="latido-grid" :x1="M.left" :x2="ANCHO - M.right" :y1="tick.y" :y2="tick.y" />
          <text v-for="tick in ticksY" :key="`label-${tick.valor}`" class="latido-tick" :x="M.left - 10" :y="tick.y + 4" text-anchor="end">{{ tick.label }}</text>
          <line class="latido-axis" :x1="M.left" :x2="ANCHO - M.right" :y1="M.top + altoUtil" :y2="M.top + altoUtil" />
          <line class="latido-axis" :x1="M.left" :x2="M.left" :y1="M.top" :y2="M.top + altoUtil" />
          <text v-for="tick in ticksX" :key="`x-${tick.x}`" class="latido-tick" :x="tick.x" :y="M.top + altoUtil + 22" text-anchor="middle">{{ tick.label }}</text>
          <text class="latido-eje-titulo" :x="M.left" :y="M.top - 10">flujo (unidades del backend)</text>
          <text class="latido-eje-titulo" :x="ANCHO - M.right" :y="ALTO - 8" text-anchor="end">fecha</text>
        </g>

        <polyline v-if="puntosValidos.length > 1" class="latido-linea" :points="linea" />

        <g v-for="punto in puntosValidos" :key="punto.fechaTexto + punto.flujo" class="latido-punto">
          <circle class="latido-hit" :cx="punto.x" :cy="punto.y" r="22" />
          <circle class="latido-dot" :cx="punto.x" :cy="punto.y" r="4" />
          <text v-if="punto.etiqueta" class="latido-lambda" :x="punto.etiquetaX" :y="punto.etiquetaY" :text-anchor="punto.etiquetaAnclaje">{{ punto.etiqueta }}</text>
          <title>{{ punto.tooltip }}</title>
        </g>
      </svg>

      <p class="latido-pie">
        {{
          hayLambda
            ? 'Cada punto es una medición del backend; la etiqueta indica la longitud de onda cuando está informada.'
            : 'Cada punto es una medición del backend; esta serie no informa longitud de onda.'
        }}
      </p>
    </template>
  </div>
</template>
