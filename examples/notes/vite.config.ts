import { defineConfig } from 'vite'
import {svelte} from '@sveltejs/vite-plugin-svelte'
import UnoCSS from 'unocss/vite'
import nexy from "./__nexy__/vite"

export default defineConfig({
  
  plugins: [
    nexy(),
    UnoCSS(),
    svelte(),
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
