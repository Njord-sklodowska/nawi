/**
 * Capa de datos de Nawi: un único punto de entrada que la interfaz consume,
 * hoy respaldado por el mock y mañana por la API del backend.
 *
 * Contrato que debe cumplir cualquier fuente (`source`):
 *
 *   source.mode          'mock' | 'api'
 *   source.status        'demo' | 'live' | 'pending'
 *                          demo    = datos de demostración, no observaciones
 *                          live    = datos reales servidos por el backend
 *                          pending = la fuente existe pero no está conectada
 *   source.label         nombre corto para mostrar en la interfaz
 *   source.illustrative  true | false | null
 *                          true  = los datos NO son observaciones reales
 *                          false = los datos SÍ son observaciones reales
 *                          null  = no hay datos todavía, no se puede afirmar nada
 *                        (una fuente sin conectar NO debe declarar false)
 *
 *   await source.listObjects()            -> NawiObject[]
 *   await source.listFrames(objectId)     -> NawiFrame[]
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

export const catalog = SOURCES[DATA_SOURCE_MODE];

/**
 * Metadatos para la interfaz. `status` es la fuente de verdad de lo que se
 * puede afirmar: 'pending' nunca se presenta como datos del backend.
 */
export const DATA_SOURCE_INFO = Object.freeze({
  mode: catalog.mode,
  status: catalog.status,
  label: catalog.label,
  illustrative: catalog.illustrative,
});

export default catalog;
