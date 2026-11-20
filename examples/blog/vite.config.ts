import { defineConfig } from 'vite'
import nexy from "./__nexy__/vite"

export default defineConfig({
  
  plugins: [
    nexy(),
  ],
  customLogger: nexy.log(),
  build :{
    rollupOptions: {
    output: {
      format: 'esm',
    },
    external: [],
  }
  }
})
