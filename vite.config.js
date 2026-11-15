import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';

export default defineConfig({
  plugins: [vue()],
  server: {
    // Puerto fijo de Nawi. strictPort hace que Vite falle si 5178 está ocupado,
    // en vez de saltar en silencio a otro puerto (y que nadie sepa dónde mirar).
    port: 5178,
    strictPort: true,
    watch: {
      // El backend (y sobre todo backend/.venv, con miles de archivos) no debe
      // entrar en el watcher: agota el límite de inotify (ENOSPC) y tumba Vite.
      ignored: ['**/backend/**', '**/.git/**'],
    },
  },
});
