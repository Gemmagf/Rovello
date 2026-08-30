/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      colors: {
        forest: {
          900: '#2E4B3A',
          700: '#526B5B',
        },
        sage: {
          500: '#819482',
          200: '#C7D0C5',
        },
        cream: {
          100: '#F2EFE6',
          50:  '#FAF8F2',
        },
        ink: '#23352B',
        muted: '#68736C',
        alert: '#C93A32',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        'card': '0 6px 18px rgba(35,53,43,0.08)',
      },
      borderRadius: {
        card:   '24px',
        btn:    '16px',
        input:  '14px',
        pill:   '999px',
      },
    },
  },
  plugins: [],
};
