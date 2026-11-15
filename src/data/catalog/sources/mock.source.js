import { MOCK_FRAMES } from '../frames.mock.js';
import { MOCK_OBJECTS } from '../objects.mock.js';

// Copia defensiva: la interfaz nunca muta el catálogo original.
const copy = (value) => JSON.parse(JSON.stringify(value));

/**
 * Fuente de datos de demostración (mock).
 * Cumple el contrato descrito en ./index.js.
 */
export const mockSource = Object.freeze({
  mode: 'mock',
  status: 'demo',
  label: 'Datos de demostración',
  illustrative: true,
  async listObjects() {
    return copy(MOCK_OBJECTS);
  },
  async listFrames(/* objectId */) {
    // Por ahora los cinco objetos comparten los mismos cuadros ilustrativos:
    // todavía no hay recortes reales por objeto.
    return copy(MOCK_FRAMES);
  },
});
