/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: '#4f46e5',
        secondary: '#9333ea',
        background: '#0f172a',
        surface: '#1e293b',
        muted: '#94a3b8'
      }
    },
  },
  plugins: [],
}
