/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./src/**/*.{astro,html,js,jsx,md,mdx,svelte,ts,tsx,vue}'],
  theme: {
    extend: {
      height: {
        parallax: '95%'
      },
      width: {
        parallax: '98%'
      },
      dropShadow: {
        '3xl': '2em 2em 2em #FFF68F',
        '4xl': [
          '0 35px 35px rgba(0, 0, 0, 0.25)',
          '0 45px 65px rgba(0, 0, 0, 0.15)'
        ]
      }
    }
  },
  plugins: []
}
