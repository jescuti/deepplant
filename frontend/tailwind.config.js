/** @type {import('tailwindcss').Config} */
export default {
  content: [
    'index.html',
    "src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        customRed: '#C00404',
        customBrown: '#4E3629', 
        customLightBrown: '#DACFC5',
      },
      fontSize: {
        xxs: ['0.625rem', { lineHeight: '1rem' }],
      },
      height: {
        '110': '30rem', 
      },
    },
  },
  plugins: [],
}

