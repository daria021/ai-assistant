import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from "@tailwindcss/vite";

// https://vite.dev/config/
export default defineConfig({
    base: './',
    plugins: [
      react(),
    tailwindcss(),
  ],
    server: {
        host: '0.0.0.0',
        port: 3000,
        allowedHosts: ['9328-45-91-236-218.ngrok-free.app'],
    },
})
