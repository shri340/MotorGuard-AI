/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        industrial: {
          950: '#0a0d12',
          900: '#10141d',
          850: '#151b27',
          800: '#1b2333',
          700: '#28344c',
          600: '#3c4c6d',
          border: '#222d42',
          accent: '#38bdf8', // electric cyan
          amber: '#f59e0b',  // warning amber
          danger: '#ef4444', // critical red
          safe: '#10b981',   // optimal green
          purple: '#a855f7'  // ml purple
        }
      },
      fontFamily: {
        mono: ['JetBrains Mono', 'Fira Code', 'Consolas', 'monospace'],
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif']
      }
    },
  },
  plugins: [],
}
