/**
 * Estado real de la fuente de datos, como store reactivo.
 *
 * Problema que resuelve: antes `DATA_SOURCE_INFO.status` era un valor fijo
 * ('live' para la API), así que con el backend caído la barra lateral seguía
 * afirmando "datos del backend" mientras la pantalla mostraba el error de
 * conexión. Ahora el estado se deriva de la última consulta real, usando
 * `apiHealth` de ./sources/api.source.js (campos: contacted, ok, error, at, base).
 *
 * Contrato para la UI (App.vue) — mismos nombres de siempre:
 *
 *   DATA_SOURCE_INFO.mode          'mock' | 'api'
 *   DATA_SOURCE_INFO.status        'demo' | 'live' | 'pending' | 'error'
 *   DATA_SOURCE_INFO.label         nombre corto de la fuente
 *   DATA_SOURCE_INFO.illustrative  true (mock) | false (api)
 *
 * Campos extra, para mensajes más precisos:
 *   DATA_SOURCE_INFO.error         mensaje en español de la última falla (o null)
 *   DATA_SOURCE_INFO.contacted     ¿ya se consultó al backend alguna vez?
 *   DATA_SOURCE_INFO.updatedAt     ISO de la última consulta (o null)
 *   DATA_SOURCE_INFO.base          base URL del backend (o null en mock)
 *
 * Valores de `status` y qué debería mostrar la UI:
 *
 *   'demo'    → modo mock. "Catálogo de demostración" + "cifras ilustrativas".
 *   'live'    → la última consulta al backend salió bien. "Catálogo del backend".
 *   'pending' → todavía no se consultó (o la fuente no está conectada).
 *               "Catálogo sin conectar" + "todavía no se consultó el backend".
 *   'error'   → la última consulta falló (red caída, 404, no-JSON, etc.).
 *               "Catálogo no disponible" + el mensaje de `error`.
 *
 * Es un objeto `reactive` de Vue: si la vista lee `DATA_SOURCE_INFO.status`
 * dentro de un computed, se actualiza solo cuando la consulta termina.
 */

import { reactive } from 'vue';
import { apiHealth } from './sources/api.source.js';

export const ESTADOS_FUENTE = Object.freeze({
  DEMO: 'demo',
  LIVE: 'live',
  PENDING: 'pending',
  ERROR: 'error',
});

/** Store reactivo. Se exporta con el nombre histórico `DATA_SOURCE_INFO`. */
export const dataSourceInfo = reactive({
  mode: 'mock',
  status: ESTADOS_FUENTE.DEMO,
  label: 'Datos de demostración',
  illustrative: true,
  error: null,
  contacted: false,
  updatedAt: null,
  base: null,
});

/** Alias: mismo objeto, mismo contrato que consumía la vista. */
export const DATA_SOURCE_INFO = dataSourceInfo;

/** Estado que corresponde según lo que ya sabe el backend (apiHealth). */
export function estadoDesdeApiHealth(health = apiHealth) {
  if (!health?.contacted) return ESTADOS_FUENTE.PENDING;
  return health.ok ? ESTADOS_FUENTE.LIVE : ESTADOS_FUENTE.ERROR;
}

/** Vuelca apiHealth al store. Devuelve el status resultante. */
export function refrescarDesdeApiHealth() {
  if (dataSourceInfo.mode !== 'api') return dataSourceInfo.status;
  const health = apiHealth ?? {};
  dataSourceInfo.status = estadoDesdeApiHealth(health);
  dataSourceInfo.error = health.ok ? null : (health.error ?? null);
  dataSourceInfo.contacted = Boolean(health.contacted);
  dataSourceInfo.updatedAt = health.at ?? null;
  dataSourceInfo.base = health.base ?? null;
  return dataSourceInfo.status;
}

/**
 * Inicializa el store según la fuente activa.
 * La API arranca en 'pending' (todavía no se consultó nada); el mock es 'demo'.
 */
export function initSourceInfo(source) {
  dataSourceInfo.mode = source?.mode ?? 'mock';
  dataSourceInfo.label = source?.label ?? '';
  dataSourceInfo.illustrative = source?.illustrative ?? null;
  dataSourceInfo.error = null;
  dataSourceInfo.contacted = false;
  dataSourceInfo.updatedAt = null;
  dataSourceInfo.base = dataSourceInfo.mode === 'api' ? (apiHealth?.base ?? null) : null;
  dataSourceInfo.status = dataSourceInfo.mode === 'api' ? ESTADOS_FUENTE.PENDING : ESTADOS_FUENTE.DEMO;
  return dataSourceInfo;
}

/**
 * Envuelve una llamada a la fuente para que el store refleje su resultado.
 * No cambia lo que devuelve ni cómo falla: solo registra el estado.
 */
export function conEstado(fn) {
  return async (...args) => {
    try {
      const resultado = await fn(...args);
      // El mock no declara estados de red: sigue siendo 'demo'.
      if (dataSourceInfo.mode === 'api') refrescarDesdeApiHealth();
      return resultado;
    } catch (error) {
      if (dataSourceInfo.mode === 'api') {
        refrescarDesdeApiHealth();
        // apiHealth ya trae el mensaje; si la fuente falló antes de consultar
        // (por ejemplo, un slug inválido), se usa el del error.
        if (!dataSourceInfo.error) dataSourceInfo.error = error?.message ?? null;
      }
      throw error;
    }
  };
}
