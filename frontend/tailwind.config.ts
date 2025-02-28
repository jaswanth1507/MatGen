/** @type {import('tailwindcss').Config} */
export default {
    content: ['./src/**/*.{html,js,svelte,ts}'],
    theme: {
      extend: {
        colors: {
          'primary': '#4299e1',
          'primary-dark': '#3182ce',
          'primary-light': '#ebf8ff',
          'secondary': '#2d3748',
          'accent': '#FFC107',
        },
      },
    },
    plugins: [
      require('@tailwindcss/typography'),
      require('@tailwindcss/forms')
    ],
  }