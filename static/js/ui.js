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
// 2. BEFORE/AFTER SLIDERS (GPU Optimized + Mobile Fixed)
// =================================================================
document.querySelectorAll('[data-slider]').forEach(slider => {
    const resize = slider.querySelector('.resize');

    // Divider removed as we moved to arrow-only navigation for mobile stability
    const resizeImg = resize?.querySelector('img');

    if (!resize) return;

    // Función para calcular y establecer el ancho correcto del slider
    const setSliderWidth = () => {
        requestAnimationFrame(() => {
            const width = slider.offsetWidth;
            if (resizeImg && width > 0) {
                // Aplicar el ancho exacto del contenedor a la imagen overlay
                resizeImg.style.width = width + 'px';
                // También establecer como variable CSS de respaldo
                slider.style.setProperty('--slider-width', width + 'px');
            }
        });
    };

    // Ejecutar después de que las imágenes carguen
    const initSlider = () => {
        setSliderWidth();
        // Doble verificación después de un pequeño delay
        setTimeout(setSliderWidth, 100);
        setTimeout(setSliderWidth, 500);
    };

    // Eventos de inicialización
    initSlider();
    window.addEventListener('resize', setSliderWidth);
    window.addEventListener('orientationchange', () => setTimeout(setSliderWidth, 100));

    // También recalcular cuando las imágenes carguen
    const images = slider.querySelectorAll('img');
    images.forEach(img => {
        if (!img.complete) {
            img.addEventListener('load', setSliderWidth);
        }
    });

    // =================================================================
    // NEW: ARROW TOGGLE LOGIC (Mobile Friendly)
    // =================================================================
    const leftArrow = slider.querySelector('.slider-arrow.left');
    const rightArrow = slider.querySelector('.slider-arrow.right');

    if (leftArrow && rightArrow) {
        // Click Right -> Show After (Overlay Width 0%)
        rightArrow.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            resize.style.width = '0%';
            slider.classList.add('show-after');
        });

        // Click Left -> Show Before (Overlay Width 100%)
        leftArrow.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            resize.style.width = '100%';
            slider.classList.remove('show-after');
        });
    }

    // Initialize state
    // Default is width: 100% (Before) via CSS
    // Optional: Ensure class sync
    // slider.classList.remove('show-after');
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

// =================================================================
// 8. SMART STICKY BAR (Mobile) - Hide when collision with other CTAs
// =================================================================
document.addEventListener('DOMContentLoaded', () => {
    // 1. Identify key elements
    const stickyBar = document.querySelector('.fixed.bottom-0.md\\:hidden');
    // Select buttons that are conceptually "Main CTAs"
    const triggers = [
        document.querySelector("button[onclick*='Hero CTA']"),
        document.querySelector("button[onclick*='CTA Final']")
    ].filter(el => el);

    if (!stickyBar || triggers.length === 0) return;

    // 2. Observer options
    const observer = new IntersectionObserver((entries) => {
        // Check if ANY of the triggers are currently visible
        // We need to know if *any* trigger is intersecting, not just the one that changed
        // So we might need to track state more robustly, but for simple toggle:
        // If *this* entry is intersecting, hide.
        // But what if two are visible? (Unlikely for Hero/Final, they are far apart)
        // Simple logic: If entry.isIntersecting -> Hide. If !isIntersecting -> Show?
        // Wait, if I scroll past Hero, it triggers !isIntersecting -> Show. Correct.

        entries.forEach(entry => {
            if (entry.isIntersecting) {
                // If a Main CTA is visible, HIDE the sticky bar
                stickyBar.classList.add('translate-y-full', 'opacity-0', 'pointer-events-none');
            } else {
                // If a Main CTA is NOT visible, SHOW the sticky bar...
                // BUT only if NO OTHER trigger is visible?
                // Given Hero and Final are far apart, this simple toggle is likely fine.
                // However, if I rely on 'forEach', one entry might say "hidden" and another "visible" in the same tick if they were close.
                // Better: Check active triggers.

                // Let's stick to the entry logic. If 'isIntersecting' is false, it means *that specific button* left view.
                // We should check if any others are visible?
                // For simplicity/robustness:
                const isAnyVisible = triggers.some(t => {
                    const rect = t.getBoundingClientRect();
                    return (rect.top < window.innerHeight && rect.bottom > 0);
                });

                if (!isAnyVisible) {
                    stickyBar.classList.remove('translate-y-full', 'opacity-0', 'pointer-events-none');
                }
            }
        });
    }, { root: null, threshold: 0.1 });

    // 3. Start observing
    triggers.forEach(trigger => observer.observe(trigger));
});
