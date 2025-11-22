import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  root: '.',
  publicDir: 'public',
  base: '/simplilearn/', // GitHub Pages base path
  server: {
    host: '0.0.0.0', // Expose to network
    port: 5173,
  },
  build: {
    outDir: 'dist',
  }
});
