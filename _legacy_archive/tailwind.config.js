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
            },
            blur: {
                'luxury-sm': '40px',
                'luxury-md': '80px',
                'luxury-lg': '120px',
                'luxury-xl': '150px',
                'luxury-2xl': '180px',
            },
            backgroundImage: {
                'noise': "url('data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 200 200%22 width=%22200%22 height=%22200%22><filter id=%22noise%22><feTurbulence type=%22fractalNoise%22 baseFrequency=%220.85%22 stitchTiles=%22stitch%22/></filter><rect width=%22100%25%22 height=%22100%25%22 filter=%22url(%23noise)%22/></svg>')",
            }
        }
    },
    plugins: [],
}
