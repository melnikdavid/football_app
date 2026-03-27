/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        primary: {
          50: "#eff6ff",
          500: "#3b82f6",
          600: "#2563eb",
          700: "#1d4ed8",
        },
        brand: {
          green: "#16a34a",
          gold: "#d97706",
        },
      },
      fontFamily: {
        hebrew: ["Heebo", "Arial", "sans-serif"],
      },
    },
  },
  plugins: [],
};
