/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Dark theme color system
        dark: {
          bg: {
            primary: '#0B0F1A',
            secondary: '#0E1627',
            tertiary: '#111827',
          },
          surface: {
            base: '#111827',
            elevated: '#161E2E',
            sidebar: '#0F172A',
          },
          border: '#1F2937',
          text: {
            primary: '#E5E7EB',
            secondary: '#9CA3AF',
            muted: '#6B7280',
          },
        },
        accent: {
          primary: '#38BDF8',
          success: '#22C55E',
          warning: '#F59E0B',
          critical: '#EF4444',
        },
        neon: {
          blue: '#38BDF8',
          green: '#22C55E',
          red: '#EF4444',
          amber: '#F59E0B'
        }
      }
    },
  },
  plugins: [],
}