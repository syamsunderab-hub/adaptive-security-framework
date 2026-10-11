/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        defcon5: "#10b981", // Green - Normal
        defcon4: "#3b82f6", // Blue - Elevated
        defcon3: "#f59e0b", // Yellow/Amber - Guarded
        defcon2: "#f97316", // Orange - Moderate
        defcon1: "#ef4444", // Red - Maximum
      }
    },
  },
  plugins: [],
}
