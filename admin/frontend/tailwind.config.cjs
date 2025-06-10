/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx,mdx}"
  ],
  theme: {
    // Никаких ручных colors — все «brand»-цвета мы задаём в CSS через @theme
    extend: {}
  },
  plugins: []
}
