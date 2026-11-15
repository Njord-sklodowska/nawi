/**
 * Catálogo de demostración de Nawi (fuente `mock`).
 *
 * FORMATO: cada objeto tiene EXACTAMENTE la forma del `objetos.json` real del
 * backend (rama cecilia/backend, repo Njord-sklodowska/nawi):
 *
 *   slug, nombre, tipo, rol, ra_deg, dec_deg, epoca,
 *   pm_ra_cosdec_mas_yr, pm_dec_mas_yr, fov_arcmin
 *
 * Los valores son los publicados por el backend (astrometría de SIMBAD/Gaia
 * DR3). El frontend los copia sin recalcular ni verificar nada.
 *
 * Copiar el shape —y no reinventarlo— hace que el día que exista el endpoint,
 * la fuente `api` devuelva esto mismo y la vista no se toque.
 */

export const MOCK_OBJETOS = Object.freeze([
  Object.freeze({
    slug: 'barnard',
    nombre: 'Estrella de Barnard',
    tipo: 'estrella_movimiento_propio',
    rol: 'principal',
    ra_deg: 269.45207696,
    dec_deg: 4.69336497,
    epoca: 'J2000',
    pm_ra_cosdec_mas_yr: -801.551,
    pm_dec_mas_yr: 10362.394,
    fov_arcmin: 4,
  }),
  Object.freeze({
    slug: 'wise-0855',
    nombre: 'WISE 0855-0714',
    tipo: 'enana_marron_Y',
    rol: 'secundario',
    ra_deg: 133.81890825,
    dec_deg: -7.247048,
    epoca: 'J2000',
    pm_ra_cosdec_mas_yr: -8123.7,
    pm_dec_mas_yr: 673.2,
    fov_arcmin: 4,
  }),
  Object.freeze({
    slug: 'epsilon-indi-b',
    nombre: 'Epsilon Indi B (par de enanas marrones)',
    tipo: 'enana_marron',
    rol: 'secundario',
    ra_deg: 331.04414659,
    dec_deg: -56.7828442,
    epoca: 'J2000',
    pm_ra_cosdec_mas_yr: 3981.977,
    pm_dec_mas_yr: -2466.832,
    fov_arcmin: 4,
  }),
  Object.freeze({
    slug: 'rw-aurigae',
    nombre: 'RW Aurigae',
    tipo: 'estrella_variable',
    rol: 'secundario',
    ra_deg: 76.95652603,
    dec_deg: 30.40143817,
    epoca: 'J2000',
    pm_ra_cosdec_mas_yr: 7.23,
    pm_dec_mas_yr: -20.33,
    fov_arcmin: 4,
  }),
  Object.freeze({
    slug: 'r-draconis',
    nombre: 'R Draconis',
    tipo: 'estrella_variable',
    rol: 'secundario',
    ra_deg: 248.16761083,
    dec_deg: 66.75497942,
    epoca: 'J2000',
    pm_ra_cosdec_mas_yr: -20.643,
    pm_dec_mas_yr: 6.149,
    fov_arcmin: 4,
  }),
]);

/**
 * Texto de presentación por objeto: lo que NO viene del backend y solo sirve
 * para la interfaz. Separado a propósito, para no ensuciar el contrato.
 */
export const PRESENTACION = Object.freeze({
  barnard: Object.freeze({
    tag: 'MOVIMIENTO',
    papel: 'Objeto principal de la demo',
    uso: 'Alineación entre fechas, desplazamiento visible y medición.',
  }),
  'wise-0855': Object.freeze({
    tag: 'BONUS',
    papel: 'Objeto bonus, solo si se detecta',
    uso: 'Caso de movimiento propio extremo; en infrarrojo cercano es muy tenue.',
  }),
  'epsilon-indi-b': Object.freeze({
    tag: 'SISTEMA',
    papel: 'Alternativa al objeto principal',
    uso: 'Caso de sistema: falta verificar si el par se resuelve con la resolución de SPHEREx.',
  }),
  'rw-aurigae': Object.freeze({
    tag: 'VARIABLE',
    papel: 'Objeto de la función "Latido"',
    uso: 'Cambia de brillo, no de posición: sirve para la curva de brillo.',
  }),
  'r-draconis': Object.freeze({
    tag: 'VARIABLE',
    papel: 'Objeto de la función "Latido"',
    uso: 'Cambia de brillo, no de posición: sirve para la curva de brillo.',
  }),
});
