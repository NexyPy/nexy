import { defineConfig, type Plugin } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import nexy from "./__nexy__/vite"
import { buildSearchIndex, writeSearchIndex } from './src/utils/search'

function searchIndexPlugin(): Plugin {
  return {
    name: 'search-index',
    configureServer(server) {
      server.middlewares.use('/public/search_index.json', (_req, res) => {
        const index = buildSearchIndex();
        res.setHeader('Content-Type', 'application/json');
        res.end(JSON.stringify(index));
      });
    },
    buildStart() {
      writeSearchIndex();
    },
  };
}

export default defineConfig({
  plugins: [
    searchIndexPlugin(),
    nexy(),
    tailwindcss(),
    react(),
  ],
  customLogger: nexy.log(),
  build: {
    rollupOptions: {
      output: {
        format: 'esm',
      },
      external: [],
    }
  }
})