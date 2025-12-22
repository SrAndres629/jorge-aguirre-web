/** @type {import('tailwindcss').Config} */
module.exports = {
    content: ["./templates/**/*.html", "./static/js/**/*.js"],
    theme: {
        extend: {
            colors: {
                'luxury-black': '#0a0a0a',
                'luxury-gold': '#C5A059',
                'luxury-gold-light': '#E5C585',
                'luxury-dark': '#121212',
                'luxury-text': '#e5e7eb',
                'test-color': '#ff0000'
            },
            fontFamily: {
                'serif': ['Playfair Display', 'serif'],
                'sans': ['Montserrat', 'sans-serif'],
            }
        },
    },
    plugins: [],
}
