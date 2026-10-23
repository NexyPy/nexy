import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import nexy from "./__nexy__/vite"

export default defineConfig({
  plugins: [
    nexy(),
    react(),
  ],
  customLogger: nexy.log(),
  build: {
    rollupOptions: {
      output: { format: 'esm' },
      external: [],
    },
  },
})
