/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["../paw/templates/**/*.{html,js}"],
  theme: {
    extend: {},
  },
  plugins: [require("daisyui")],
  daisyui: {
    themes: ["nord"],
  },
}

