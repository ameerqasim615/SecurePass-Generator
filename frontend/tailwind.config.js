/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        // Navy accent; purple accent uses Tailwind's built-in `violet` scale.
        navy: {
          50: '#f3f6fb',
          100: '#e3eaf5',
          200: '#c5d3ea',
          300: '#9bb3d9',
          400: '#6b8cc4',
          500: '#4a6ba8',
          600: '#37548c',
          700: '#2c4372',
          800: '#1f3158',
          900: '#16244a',
          950: '#0d1730',
        },
      },
    },
  },
  plugins: [],
}
