/** @type {import('tailwindcss').Config} */
module.exports = {
    content: ["./templates/**/*.html", "./static/js/**/*.js"],
    theme: {
        extend: {
            colors: {
                'luxury-black': '#020202', // Deepest black
                'luxury-dark': '#0a0a0a',   // Secondary black
                'luxury-gold': '#D4AF37',   // Classic Metallic Gold
                'luxury-gold-light': '#F1E5AC', // Champagne highlight
                'luxury-text': '#FAFAFA',   // Off-white for readability
                'luxury-gray': '#A1A1A1',   // Muted text
            },
            fontFamily: {
                'serif': ['Playfair Display', 'serif'],
                'sans': ['Montserrat', 'sans-serif'],
            },
            letterSpacing: {
                'widest': '.25em',
            }
        },
    },
    plugins: [],
}
