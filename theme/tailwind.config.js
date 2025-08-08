/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./paw/templates/**/*.{html,js}",
    "./status/templates/**/*.{html,js}",
  ],
  theme: {
    extend: {},
  },
  plugins: [require("daisyui")],
  daisyui: {
    themes: [
      {
        light: {
          ...require("daisyui/src/theming/themes")["nord"],
        },
        dark: {
          ...require("daisyui/src/theming/themes")["dark"],
          accent: "#88C0D0",
          secondary: "#81A1C1",
          success: "#A3BE8C",
          warning: "#EBCB8B",
          error: "#BF616A",
          "--rounded-box": "0.4rem",
          "--rounded-btn": "0.2rem",
          "--rounded-badge": "0.4rem",
          "--tab-radius": "0.2rem",
        },
      },
    ],
  },
};
