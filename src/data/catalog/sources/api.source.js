/**
 * Fuente `api`: los datos reales del backend Django de Nawi.
 *
 * Endpoints (contrato en backend/api/urls.py):
 *   GET /api/objetos/              -> array plano de objetos
 *   GET /api/objetos/<slug>/       -> ficha con `cuadros[]` (y `estado`, `motivo`…)
 *
 * Funciona en cualquier origen porque el backend ya tiene CORS habilitado para
 * el frontend (http://localhost:5178 en desarrollo).
 *
 * Variables de entorno:
 *   VITE_API_BASE             base del backend, sin barra final
 *                             (default http://127.0.0.1:8010)
 *   VITE_NAWI_DATA_SOURCE=api activa esta fuente en src/data/catalog/index.js
 *
 * Honestidad: acá no hay datos de relleno. Si el backend no responde, estas
 * funciones rechazan con un mensaje en español y la interfaz muestra el error;
 * nunca se devuelve un objeto o un cuadro inventado. Los frames que salen de
 * acá llevan `illustrative: false` porque solo existen si vinieron de una
 * respuesta 200 del backend (ver ../adapters.js).
 */

import { toDetalleVista, toFramesVista } from '../adapters.js';

export const DEFAULT_API_BASE = 'http://127.0.0.1:8010';

/** Tiempo máximo de espera por respuesta del backend. */
const TIMEOUT_MS = 12000;

function readApiBase() {
  try {
    const configurado = import.meta.env?.VITE_API_BASE;
    const valor = typeof configurado === 'string' ? configurado.trim() : '';
    return (valor || DEFAULT_API_BASE).replace(/\/+$/, '');
  } catch {
    return DEFAULT_API_BASE;
  }
}

export const API_BASE = readApiBase();

/**
 * Última respuesta del backend. No se usa para decidir qué mostrar (eso lo hace
 * el manejo de errores), sino para diagnóstico: permite saber si la fuente ya
 * habló con el backend y con qué resultado.
 */
export const apiHealth = {
  contacted: false,
  ok: false,
  error: null,
  at: null,
  base: API_BASE,
};

function marcarContacto(ok, error = null) {
  apiHealth.contacted = true;
  apiHealth.ok = ok;
  apiHealth.error = error;
  apiHealth.at = new Date().toISOString();
}

function esJson(response) {
  return String(response.headers.get('content-type') ?? '').toLowerCase().includes('json');
}

function mensajeDelCuerpo(cuerpo) {
  if (!cuerpo || typeof cuerpo !== 'object') return '';
  for (const clave of ['mensaje', 'error', 'detail']) {
    const valor = cuerpo[clave];
    if (typeof valor === 'string' && valor.trim()) return valor.trim();
  }
  return '';
}

/**
 * GET + parseo con errores explícitos en español.
 * `descripcion` se usa para redactar el mensaje ("el catálogo", "el objeto «x»").
 */
async function requestJson(path, descripcion) {
  const url = `${API_BASE}${path}`;
  const control = new AbortController();
  const temporizador = setTimeout(() => control.abort(), TIMEOUT_MS);

  let response;
  try {
    response = await fetch(url, {
      headers: { Accept: 'application/json' },
      signal: control.signal,
    });
  } catch (error) {
    const abortado = error?.name === 'AbortError';
    const mensaje = abortado
      ? `El backend no respondió en ${TIMEOUT_MS / 1000} segundos al pedir ${descripcion} (${url}).`
      : `No se pudo conectar con el backend en ${API_BASE} al pedir ${descripcion}. ` +
        'Verificá que el servidor esté corriendo (cd backend && ./.venv/bin/python manage.py runserver 8010).';
    marcarContacto(false, mensaje);
    throw new Error(mensaje);
  } finally {
    clearTimeout(temporizador);
  }

  const texto = await response.text().catch(() => '');
  let cuerpo = null;
  let parseoOk = false;
  if (texto) {
    try {
      cuerpo = JSON.parse(texto);
      parseoOk = true;
    } catch {
      parseoOk = false;
    }
  } else {
    parseoOk = true; // cuerpo vacío: no es un error de formato, se evalúa por status
  }

  if (!response.ok) {
    const detalle = mensajeDelCuerpo(cuerpo);
    const mensaje = response.status === 404
      ? `El backend no encontró ${descripcion} (HTTP 404).${detalle ? ` ${detalle}` : ''}`
      : `El backend respondió HTTP ${response.status} al pedir ${descripcion}.${detalle ? ` ${detalle}` : ''}`;
    marcarContacto(false, mensaje);
    throw new Error(mensaje);
  }

  if (!parseoOk || (!esJson(response) && cuerpo === null)) {
    const mensaje =
      `El backend devolvió una respuesta que no es JSON al pedir ${descripcion} ` +
      `(content-type: ${response.headers.get('content-type') || 'desconocido'}).`;
    marcarContacto(false, mensaje);
    throw new Error(mensaje);
  }

  marcarContacto(true, null);
  return cuerpo;
}

export const apiSource = Object.freeze({
  mode: 'api',
  // La fuente es el backend real: lo que devuelve son sus datos. Si el backend
  // falla, la promesa rechaza y la interfaz muestra el error; no hay relleno.
  status: 'live',
  label: 'API del backend',
  illustrative: false,
  apiBase: API_BASE,

  /** Catálogo crudo del backend (lo traduce ../adapters.js a modelo de vista). */
  async listObjects() {
    const datos = await requestJson('/api/objetos/', 'el catálogo de objetos');
    if (!Array.isArray(datos)) {
      const mensaje = 'El backend devolvió el catálogo con un formato inesperado: se esperaba un array de objetos.';
      marcarContacto(false, mensaje);
      throw new Error(mensaje);
    }
    return datos;
  },

  /**
   * Serie temporal de un objeto, ya traducida a frames de la vista.
   * Si el objeto existe pero no tiene datos precalculados, devuelve [] (la ficha
   * del backend viene con `estado: "sin_datos"` y `cuadros: []`).
   */
  async listFrames(slug) {
    if (typeof slug !== 'string' || !slug.trim()) {
      throw new Error('Falta el identificador del objeto para pedir los cuadros.');
    }
    const datos = await requestJson(
      `/api/objetos/${encodeURIComponent(slug.trim())}/`,
      `el objeto «${slug.trim()}»`,
    );
    if (!datos || typeof datos !== 'object' || Array.isArray(datos)) {
      const mensaje = `El backend devolvió la ficha de «${slug.trim()}» con un formato inesperado.`;
      marcarContacto(false, mensaje);
      throw new Error(mensaje);
    }
    const cuadros = Array.isArray(datos.cuadros) ? datos.cuadros : [];
    return toFramesVista(cuadros, { apiBase: API_BASE });
  },

  /**
   * Ficha completa del objeto: estado, motivo, latido (curva de brillo),
   * cuadros, rastro, revelar y conocido.
   *
   * Devuelve el detalle normalizado (../adapters.js -> toDetalleVista):
   *   { slug, estado, motivo, latido, cuadros, rastro, revelar, conocido }
   *
   * Hoy el backend expone `latido: []` (exportar_cuadros.py lo deja vacío a
   * propósito), así que sin datos reales la respuesta es estado 'sin_datos' y
   * latido []; no se inventan puntos. Cuando Cecilia llene el campo, esta
   * función lo entrega sin cambios de código.
   */
  async getDetalleObjeto(slug) {
    if (typeof slug !== 'string' || !slug.trim()) {
      throw new Error('Falta el identificador del objeto para pedir el detalle.');
    }
    const datos = await requestJson(
      `/api/objetos/${encodeURIComponent(slug.trim())}/`,
      `el objeto «${slug.trim()}»`,
    );
    const detalle = toDetalleVista(datos, { apiBase: API_BASE });
    if (!detalle) {
      const mensaje = `El backend devolvió la ficha de «${slug.trim()}» con un formato inesperado.`;
      marcarContacto(false, mensaje);
      throw new Error(mensaje);
    }
    return detalle;
  },
});
