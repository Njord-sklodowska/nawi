const NOT_CONNECTED =
  'La fuente de API todavía no está conectada: los endpoints del backend siguen pendientes. ' +
  'Mientras tanto usá la fuente de demostración (VITE_NAWI_DATA_SOURCE=mock).';

function notConnected() {
  return Promise.reject(new Error(NOT_CONNECTED));
}

/**
 * Fuente reservada para cuando el backend publique los datos precalculados (M2)
 * y los recortes alineados (M3).
 *
 * A propósito NO define URLs ni hace fetch: esta tarea no cambia endpoints ni
 * toca el backend. Para activarla:
 *   1. implementar listObjects() y listFrames(objectId) con el contrato de ./index.js,
 *   2. verificar que cada objeto/frame real traiga `illustrative: false`,
 *   3. arrancar o compilar con VITE_NAWI_DATA_SOURCE=api.
 *
 * Sobre `illustrative`: acá vale `null`, no `false`. `false` significaría "hay
 * observaciones reales del backend", y esta fuente todavía no tiene ni una, así
 * que afirmarlo sería mentir. `status: 'pending'` es lo que la interfaz usa para
 * decir "catálogo sin conectar" y mostrar el error en vez de inventar datos.
 */
export const apiSource = Object.freeze({
  mode: 'api',
  status: 'pending',
  label: 'API del backend',
  illustrative: null,
  listObjects: notConnected,
  listFrames: notConnected,
});
