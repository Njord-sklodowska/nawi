/**
 * Capa de datos de Nawi: un único punto de entrada que consume la interfaz.
 *
 * Fuente activa:
 *   - `mock` por defecto (datos de demostración, sin red).
 *   - `api` real del backend Django, solo con VITE_NAWI_DATA_SOURCE=api.
 *
 * Cualquier fuente entrega datos con el shape del backend (`slug`, `ra_deg`,
 * `cuadros[]`) y este módulo los traduce al modelo de vista con ./adapters.js,
 * así que la interfaz no sabe de dónde vienen.
 *
 * Contrato que debe cumplir cualquier fuente (`source`):
 *
 *   source.mode          'mock' | 'api'
 *   source.status        'demo' | 'live' | 'pending' | 'error'
 *                          demo    = datos de demostración, no observaciones
 *                          live    = la última consulta al backend salió bien
 *                          pending = todavía no se consultó al backend
 *                          error   = la última consulta falló (red, 404, no-JSON)
 *                        En la práctica el estado lo calcula ./sourceInfo.js a
 *                        partir de apiHealth; la fuente no lo fija a mano.
 *   source.label         nombre corto para mostrar en la interfaz
 *   source.illustrative  true | false | null
 *                          true  = los datos NO son observaciones reales
 *                          false = los datos SÍ son observaciones reales
 *                          null  = no hay datos todavía, no se puede afirmar nada
 *                        (una fuente sin conectar NO debe declarar false)
 *
 *   await source.listObjects()            -> NawiObject[] (shape backend, se adapta acá)
 *   await source.listFrames(objectId)     -> NawiFrame[]
 *   await source.getDetalleObjeto(slug)   -> Detalle[]
 *     {
 *       slug, estado, motivo,
 *       latido: [{ fecha, flujo, error, longitudOndaUm }],   // curva de brillo
 *       cuadros: NawiFrame[],
 *       rastro, revelar, conocido
 *     }
 *     Sin puntos reales, la fuente devuelve `estado: 'sin_datos'` y `latido: []`;
 *     nunca se rellena la curva con valores inventados.
 *
 *   El `source` devuelve, en `listObjects()`, objetos con el shape del
 *   `objetos.json` del backend (slug, nombre, tipo, rol, ra_deg, dec_deg,
 *   epoca, pm_ra_cosdec_mas_yr, pm_dec_mas_yr, fov_arcmin). El adaptador
 *   ./adapters.js lo traduce al modelo de vista:
 *
 *   NawiObject {
 *     id: string                  identificador estable (se usa en la URL)
 *     name: string
 *     kind: string                tipo de objeto
 *     purpose: 'movimiento' | 'bonus' | 'sistema' | 'variabilidad'
 *     purposeLabel: string        texto legible del propósito
 *     tag: string                 etiqueta corta para el visor
 *     demoRole: string            papel en la demo
 *     demoUse: string             para qué se puede mostrar honestamente
 *     coordinates: null | {
 *       ra, dec                   placeholder; nunca se presenta como verificado
 *       status                    'ilustrativo' | 'referencia-de-plan'
 *       statusLabel               rótulo visible ('NO VALIDADO', 'A CONFIRMAR')
 *       note                      aclaración en texto
 *     }
 *   }
 *
 *   NawiFrame {
 *     date, band                  placeholders mientras illustrative === true
 *     url: string
 *     illustrative: boolean       true si el cuadro NO es una observación real
 *   }
 *
 * Regla de honestidad: si `illustrative` es true, la interfaz debe mostrar el
 * rótulo de imagen ilustrativa y ninguna cifra se presenta como medida.
 */

import { toObjetoVista } from './adapters.js';
import { DATA_SOURCE_INFO as SOURCE_INFO, conEstado, initSourceInfo } from './sourceInfo.js';
import { apiSource } from './sources/api.source.js';
import { mockSource } from './sources/mock.source.js';

const SOURCES = { api: apiSource, mock: mockSource };

function readRequestedMode() {
  try {
    return String(import.meta.env?.VITE_NAWI_DATA_SOURCE ?? '').trim().toLowerCase();
  } catch {
    return '';
  }
}

const requestedMode = readRequestedMode();

/** Fuente activa: `mock` por defecto; `api` solo si se pide explícitamente. */
export const DATA_SOURCE_MODE = Object.hasOwn(SOURCES, requestedMode) ? requestedMode : 'mock';

const source = SOURCES[DATA_SOURCE_MODE];

// El estado de la fuente (demo | live | pending | error) vive en ./sourceInfo.js
// y se actualiza con cada consulta, a partir de apiHealth de la fuente api.
initSourceInfo(source);

/**
 * Fuente activa envuelta por el adaptador: cualquier `source` devuelve el shape
 * del backend (`slug`, `ra_deg`…) y acá se traduce al modelo de vista. Así la
 * vista no sabe si los datos vienen del mock o de la API.
 *
 * Cada llamada pasa por `conEstado`, que refleja el resultado en DATA_SOURCE_INFO.
 */
export const catalog = Object.freeze({
  mode: source.mode,
  get status() {
    return SOURCE_INFO.status;
  },
  label: source.label,
  illustrative: source.illustrative,
  listObjects: conEstado(async () => (await source.listObjects()).map(toObjetoVista)),
  listFrames: conEstado((slug) => source.listFrames(slug)),
  /** Detalle de la ficha, incluido el latido (curva de brillo). */
  getDetalleObjeto: conEstado((slug) => source.getDetalleObjeto(slug)),
});

/**
 * Metadatos para la interfaz (store reactivo de ./sourceInfo.js).
 * `status` es la fuente de verdad de lo que se puede afirmar:
 *   'demo' | 'live' | 'pending' | 'error'
 */
export const DATA_SOURCE_INFO = SOURCE_INFO;

export default catalog;
