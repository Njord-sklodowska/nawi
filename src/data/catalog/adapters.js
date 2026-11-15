/**
 * Adaptador entre el catálogo del backend y lo que necesita la vista.
 *
 * Entrada: un objeto con la forma de backend/pipeline/objetos.json
 *          (slug, nombre, tipo, ra_deg, dec_deg, pm_*, fov_arcmin…).
 * Salida:  el modelo de vista que consume App.vue.
 *
 * Toda la traducción vive acá: cuando la fuente sea la API, devuelve el mismo
 * JSON y este adaptador hace el resto. La vista no cambia.
 */

import { PRESENTACION } from './objects.mock.js';

const TIPO_LABEL = {
  estrella_movimiento_propio: 'Estrella de alto movimiento propio',
  enana_marron_Y: 'Enana marrón clase Y',
  enana_marron: 'Enana marrón',
  estrella_variable: 'Estrella variable',
};

const pad = (value, size = 2) => String(value).padStart(size, '0');

/** 269.45207696° -> "17h 57m 48.50s" */
export function formatRa(raDeg) {
  if (!Number.isFinite(raDeg)) return null;
  const totalHoras = (((raDeg % 360) + 360) % 360) / 15;
  const horas = Math.floor(totalHoras);
  const minutos = Math.floor((totalHoras - horas) * 60);
  const segundos = (totalHoras - horas - minutos / 60) * 3600;
  return `${pad(horas)}h ${pad(minutos)}m ${segundos.toFixed(2)}s`;
}

/** 4.69336497° -> "+04° 41′ 36.1″" */
export function formatDec(decDeg) {
  if (!Number.isFinite(decDeg)) return null;
  const signo = decDeg < 0 ? '−' : '+';
  const abs = Math.abs(decDeg);
  const grados = Math.floor(abs);
  const minutos = Math.floor((abs - grados) * 60);
  const segundos = (abs - grados - minutos / 60) * 3600;
  return `${signo}${pad(grados)}° ${pad(minutos)}′ ${segundos.toFixed(1)}″`;
}

/**
 * Las cifras vienen del catálogo del backend, pero el frontend no las verifica
 * ni las usa para calcular: la interfaz las muestra siempre rotuladas.
 */
function coordenadas(raw) {
  const ra = formatRa(raw.ra_deg);
  const dec = formatDec(raw.dec_deg);
  if (!ra || !dec) return null;
  return Object.freeze({
    ra,
    dec,
    raDeg: raw.ra_deg,
    decDeg: raw.dec_deg,
    epoca: raw.epoca ?? null,
    status: 'catalogo',
    statusLabel: 'CATÁLOGO',
    note:
      'Valores de backend/pipeline/objetos.json (SIMBAD/Gaia DR3). ' +
      'El frontend los muestra sin verificarlos ni recalcularlos.',
  });
}

export function toObjetoVista(raw) {
  const extra = PRESENTACION[raw.slug] ?? {};
  const pm = Number.isFinite(raw.pm_ra_cosdec_mas_yr) && Number.isFinite(raw.pm_dec_mas_yr)
    ? Object.freeze({ ra: raw.pm_ra_cosdec_mas_yr, dec: raw.pm_dec_mas_yr })
    : null;

  return Object.freeze({
    // contrato del backend
    slug: raw.slug,
    nombre: raw.nombre,
    tipo: raw.tipo,
    rol: raw.rol,
    fovArcmin: raw.fov_arcmin ?? null,
    pm,
    coordinates: coordenadas(raw),
    // alias que usa la vista
    id: raw.slug,
    name: raw.nombre,
    kind: TIPO_LABEL[raw.tipo] ?? raw.tipo,
    tag: extra.tag ?? 'OBJETO',
    demoRole: extra.papel ?? '',
    demoUse: extra.uso ?? '',
  });
}
