/** @type {import('tailwindcss').Config} */
export default { 
  content: ['./index.html', './src/**/*.{js,jsx}'], 
  theme: { 
    extend: { 
      colors: { 
        govnavy: '#0b2046', 
        govgreen: '#1a7a4c', 
        govlight: '#f8f9fa',
        ink: '#1e293b' 
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      }
    } 
  }, 
  plugins: [] 
}
