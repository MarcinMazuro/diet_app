/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/**/*.{js,jsx,ts,tsx}",       // <--- ZMIANA: Skanuje CAŁY folder app (w tym screens i tabs)
    "./components/**/*.{js,jsx,ts,tsx}" // Skanuje komponenty
  ],
  presets: [require("nativewind/preset")],
  theme: {
    extend: {},
  },
  plugins: [],
}