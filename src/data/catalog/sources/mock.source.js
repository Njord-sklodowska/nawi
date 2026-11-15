import { MOCK_FRAMES } from '../frames.mock.js';
import { MOCK_OBJETOS } from '../objects.mock.js';

// Copia defensiva: la interfaz nunca muta el catálogo original.
const copy = (value) => JSON.parse(JSON.stringify(value));

/**
 * Fuente de datos de demostración (mock).
 * Devuelve el catálogo con el mismo shape que el `objetos.json` del backend;
 * la traducción a modelo de vista la hace ../adapters.js.
 */
export const mockSource = Object.freeze({
  mode: 'mock',
  status: 'demo',
  label: 'Datos de demostración',
  illustrative: true,
  async listObjects() {
    return copy(MOCK_OBJETOS);
  },
  async listFrames(/* slug */) {
    // Por ahora los cinco objetos comparten los mismos cuadros ilustrativos:
    // todavía no hay recortes reales por objeto.
    return copy(MOCK_FRAMES);
  },
});
