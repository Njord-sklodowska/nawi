import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';

export default defineConfig({
  plugins: [vue()],
  // Puerto fijo de Nawi. strictPort hace que Vite falle si 5178 está ocupado,
  // en vez de saltar en silencio a otro puerto (y que nadie sepa dónde mirar).
  server: {
    port: 5178,
    strictPort: true,
  },
});
