import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// Use different base path for production (GitHub Pages) vs local
const isProduction = process.env.NODE_ENV === 'production';
const baseUrl = isProduction ? '/KalmSkills/' : '/';

export default defineConfig({
  plugins: [react()],
  root: '.',
  publicDir: 'public',
  base: baseUrl,
  server: {
    host: '0.0.0.0', // Expose to network
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      }
    }
  },
  build: {
    outDir: 'dist',
  }
});
