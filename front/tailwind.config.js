/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          50: "#eff6ff",
          100: "#dbeafe",
          200: "#bfdbfe",
          300: "#93c5fd",
          400: "#60a5fa",
          500: "#3b82f6", // blue-500
          600: "#2563eb", // blue-600 - Primary
          700: "#1d4ed8", // blue-700 - Primary Hover
          800: "#1e40af", // blue-800 - Primary Dark
          900: "#1e3a8a",
          950: "#172554",
        },
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
      },
      boxShadow: {
        brand: "0 4px 14px 0 rgba(37, 99, 235, 0.25)",
        "brand-lg":
          "0 10px 25px -3px rgba(37, 99, 235, 0.3), 0 4px 6px -2px rgba(37, 99, 235, 0.1)",
      },
      animation: {
        "pulse-brand": "pulse-brand 2s cubic-bezier(0.4, 0, 0.6, 1) infinite",
      },
      keyframes: {
        "pulse-brand": {
          "0%, 100%": {
            opacity: "1",
            backgroundColor: "#2563eb",
          },
          "50%": {
            opacity: "0.7",
            backgroundColor: "#3b82f6",
          },
        },
      },
    },
  },
  plugins: [],
};
