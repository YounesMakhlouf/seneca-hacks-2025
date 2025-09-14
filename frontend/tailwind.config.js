/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./public/index.html", "./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#22e3a7', // mint green accent from screenshots
          dark: '#17c592'
        },
        ink: '#0f172a',
        soft: '#f5f8f7'
      },
      boxShadow: {
        card: '0 4px 14px rgba(15, 23, 42, 0.06)'
      },
      borderRadius: {
        xl: '1rem'
      },
      fontFamily: {
        sans: [
          "Inter",
          "ui-sans-serif",
          "system-ui",
          "-apple-system",
          "Segoe UI",
          "Roboto",
          "Noto Sans",
          "Ubuntu",
          "Cantarell",
          "Helvetica Neue",
          "Arial",
          "Apple Color Emoji",
          "Segoe UI Emoji",
          "Segoe UI Symbol"
        ]
      }
    }
  },
  plugins: []
}
