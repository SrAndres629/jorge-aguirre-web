/* =================================================================
   UI.JS - Interactividad Spaceship / High-End Desire
   Sliders, Sticky Header, Particles, AOS, Vanilla-Tilt
   ================================================================= */

// =================================================================
// 1. STICKY HEADER SCROLL HANDLER
// =================================================================
(function () {
    const stickyNav = document.getElementById('stickyNav');
    const urgencyBanner = document.getElementById('urgencyBanner');

    if (stickyNav && urgencyBanner) {
        let ticking = false;

        window.addEventListener('scroll', () => {
            if (!ticking) {
                window.requestAnimationFrame(() => {
                    const currentScroll = window.pageYOffset;

                    if (currentScroll > 400) {
                        stickyNav.style.transform = 'translateY(0)';
                        urgencyBanner.style.opacity = '0';
                        urgencyBanner.style.pointerEvents = 'none';
                    } else {
                        stickyNav.style.transform = 'translateY(-100%)';
                        urgencyBanner.style.opacity = '1';
                        urgencyBanner.style.pointerEvents = 'auto';
                    }
                    ticking = false;
                });
                ticking = true;
            }
        }, { passive: true });
    }
})();

// =================================================================
// 2. BEFORE/AFTER SLIDERS (GPU Optimized)
// =================================================================
document.querySelectorAll('[data-slider]').forEach(slider => {
    const resize = slider.querySelector('.resize');
    const divider = slider.querySelector('.divider');

    if (!resize || !divider) return;

    let rafId = null;
    let isDown = false;

    const updateSlider = (x) => {
        const rect = slider.getBoundingClientRect();
        const position = ((x - rect.left) / rect.width) * 100;
        const clamped = Math.max(0, Math.min(position, 100));

        if (rafId) cancelAnimationFrame(rafId);

        rafId = requestAnimationFrame(() => {
            resize.style.width = clamped + '%';
            divider.style.left = clamped + '%';
        });
    };

    slider.addEventListener('mousedown', (e) => { isDown = true; updateSlider(e.clientX); });
    slider.addEventListener('mousemove', (e) => { if (isDown) updateSlider(e.clientX); });
    slider.addEventListener('mouseup', () => isDown = false);
    slider.addEventListener('mouseleave', () => isDown = false);
    slider.addEventListener('touchstart', (e) => { isDown = true; updateSlider(e.touches[0].clientX); }, { passive: true });
    slider.addEventListener('touchmove', (e) => { if (isDown) updateSlider(e.touches[0].clientX); }, { passive: true });
    slider.addEventListener('touchend', () => isDown = false);
});

// =================================================================
// 3. FAQ ACCORDION (Auto-close others)
// =================================================================
document.querySelectorAll('details').forEach((detail) => {
    detail.addEventListener('toggle', () => {
        if (detail.open) {
            document.querySelectorAll('details').forEach((otherDetail) => {
                if (otherDetail !== detail && otherDetail.open) {
                    otherDetail.open = false;
                }
            });
        }
    });
});

// =================================================================
// 4. WHATSAPP BUTTON ATTENTION ANIMATION
// =================================================================
(function () {
    const whatsappBtn = document.getElementById('whatsappFloat');

    if (whatsappBtn) {
        setInterval(() => {
            whatsappBtn.classList.add('animate-bounce');
            setTimeout(() => whatsappBtn.classList.remove('animate-bounce'), 2000);
        }, 10000);

        setTimeout(() => {
            whatsappBtn.classList.add('animate-bounce');
            setTimeout(() => whatsappBtn.classList.remove('animate-bounce'), 2000);
        }, 3000);
    }
})();

// =================================================================
// 5. PARTICLES.JS - Gold Dust (Atmósfera Premium)
// =================================================================
(function () {
    if (typeof particlesJS !== 'undefined' && document.getElementById('particles-js')) {
        particlesJS("particles-js", {
            "particles": {
                "number": {
                    "value": 40,
                    "density": { "enable": true, "value_area": 800 }
                },
                "color": { "value": "#C5A059" },
                "shape": { "type": "circle" },
                "opacity": {
                    "value": 0.3,
                    "random": true,
                    "anim": { "enable": true, "speed": 0.3, "opacity_min": 0.1 }
                },
                "size": {
                    "value": 3,
                    "random": true,
                    "anim": { "enable": true, "speed": 0.5, "size_min": 0.5 }
                },
                "line_linked": { "enable": false },
                "move": {
                    "enable": true,
                    "speed": 0.5,
                    "direction": "top",
                    "random": true,
                    "straight": false,
                    "out_mode": "out"
                }
            },
            "interactivity": {
                "detect_on": "window",
                "events": {
                    "onhover": { "enable": true, "mode": "repulse" },
                    "onclick": { "enable": false }
                },
                "modes": {
                    "repulse": {
                        "distance": 100,
                        "duration": 0.4
                    }
                }
            },
            "retina_detect": true
        });
        console.log('✨ Particles.js initialized (Gold Dust + Repulse)');
    }
})();

// =================================================================
// 6. AOS (Animate On Scroll)
// =================================================================
if (typeof AOS !== 'undefined') {
    AOS.init({
        duration: 800,
        easing: 'ease-out-quart',
        once: true,
        offset: 50
    });
    console.log('✅ AOS initialized');
}

// =================================================================
// 7. VANILLA-TILT (Física 3D) - Auto-init via data-tilt
// =================================================================
// Vanilla-Tilt se inicializa automáticamente con data-tilt attributes
if (typeof VanillaTilt !== 'undefined') {
    console.log('🎯 Vanilla-Tilt.js ready (3D Physics)');
}

console.log('✅ UI.js loaded (Spaceship v3.0)');
