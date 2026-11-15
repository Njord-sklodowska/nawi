/**
 * Cuadros ilustrativos del visor (fuente `mock`).
 *
 * Son las mismas imágenes de relleno que ya usaba la maqueta, sin ningún dato
 * observacional detrás: la URL es un paisaje genérico y las fechas y las bandas
 * son PLACEHOLDERS. Cada cuadro viaja con `illustrative: true` y la interfaz
 * muestra el rótulo "IMAGEN ILUSTRATIVA · DATOS REALES PENDIENTES".
 *
 * Cuando Sergio entregue los recortes reales (M2/M3), esta fuente se reemplaza
 * por la de API sin tocar la interfaz.
 */

const ILLUSTRATIVE_IMAGE =
  'https://images.unsplash.com/photo-1462331940025-496dfbfc7564?auto=format&fit=crop&w=1400&q=85';

export const MOCK_FRAMES = Object.freeze([
  Object.freeze({ date: '2024-04-18', band: 'Banda 1 · 0.75 μm', url: ILLUSTRATIVE_IMAGE, illustrative: true }),
  Object.freeze({ date: '2024-05-02', band: 'Banda 2 · 0.82 μm', url: ILLUSTRATIVE_IMAGE, illustrative: true }),
  Object.freeze({ date: '2024-05-16', band: 'Banda 3 · 0.91 μm', url: ILLUSTRATIVE_IMAGE, illustrative: true }),
  Object.freeze({ date: '2024-05-30', band: 'Banda 4 · 1.02 μm', url: ILLUSTRATIVE_IMAGE, illustrative: true }),
]);
