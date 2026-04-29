import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import nexy from "./__nexy__/vite"

export default defineConfig({
  
  plugins: [
    nexy(), 
    tailwindcss(),
    react(),
  ],
  customLogger: nexy.log(),
  build :{
    rollupOptions: {
    output: {
      format: 'esm',
    },
    // Ne pas mettre 'react' en external si tu veux que Vite 
    // l'inclue proprement dans le bundle généré
    external: [], 
  }
  }
})