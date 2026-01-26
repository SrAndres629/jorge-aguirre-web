/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
        "./core/templates/**/*.html",
        "./core/static/js/**/*.js"
    ],
    theme: {
        extend: {
            colors: {
                luxury: {
                    gold: '#C5A059',
                    'gold-light': '#E5C585',
                    'gold-dark': '#B08D45',
                    black: '#050505',
                    dark: '#0a0a0a',
                    text: '#f5f5f7',
                }
            },
            fontFamily: {
                sans: ['Montserrat', 'system-ui', 'sans-serif'],
                serif: ['Playfair Display', 'serif'],
            }
        },
    },
    plugins: [],
}
