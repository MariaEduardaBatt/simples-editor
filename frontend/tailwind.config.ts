import type { Config } from 'tailwindcss'

export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        galaxy: {
          950: '#020015',
          900: '#07051a',
          800: '#0f0a2e',
          700: '#1a1145',
          600: '#281a5c',
          500: '#3b2678',
        },
        nebula: {
          400: '#a78bfa',
          500: '#8b5cf6',
          600: '#7c3aed',
        },
      },
      animation: {
        'twinkle-slow': 'twinkle 5s ease-in-out infinite alternate',
        'twinkle-mid': 'twinkle 3s ease-in-out infinite alternate',
        'twinkle-fast': 'twinkle 2s ease-in-out infinite alternate',
        'drift-slow': 'drift 30s linear infinite',
        'drift-mid': 'drift 20s linear infinite',
        'drift-fast': 'drift 15s linear infinite',
        'shoot': 'shoot 10s ease-in infinite',
        'pulse-glow': 'pulseGlow 4s ease-in-out infinite alternate',
      },
      keyframes: {
        twinkle: {
          '0%': { opacity: '0.15' },
          '50%': { opacity: '0.8' },
          '100%': { opacity: '0.2' },
        },
        drift: {
          '0%': { transform: 'translateY(0) translateX(0)' },
          '100%': { transform: 'translateY(-120%) translateX(10%)' },
        },
        shoot: {
          '0%': { transform: 'translateX(0px) translateY(0px)', opacity: '1' },
          '70%': { opacity: '1' },
          '100%': { transform: 'translateX(2500px) translateY(-100px)', opacity: '0' },
        },
        pulseGlow: {
          '0%': { opacity: '0.15', transform: 'scale(1)' },
          '100%': { opacity: '0.35', transform: 'scale(1.05)' },
        },
      },
    },
  },
  plugins: [],
} satisfies Config
