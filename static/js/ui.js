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
// 2. BEFORE/AFTER SLIDERS (Modern Range Input Approach)
// =================================================================
window.updateSlider = function (id, value) {
    const clip = document.getElementById(`clip-${id}`);
    const handle = document.getElementById(`handle-line-${id}`);

    if (clip && handle) {
        // GPU Accelerated updates
        requestAnimationFrame(() => {
            clip.style.width = `${value}%`;
            handle.style.left = `${value}%`;
        });
    }
};

// Sync Inner Image Width to Container Width to prevent distortion
const syncSliderImages = () => {
    const sliders = document.querySelectorAll('[id^="clip-"]');
    sliders.forEach(clip => {
        const container = clip.parentElement;
        const innerImg = clip.querySelector('img');

        if (container && innerImg) {
            const width = container.offsetWidth;
            innerImg.style.width = `${width}px`;
        }
    });
};

// Init & Observers
window.addEventListener('load', syncSliderImages);
window.addEventListener('resize', syncSliderImages);
// Also use ResizeObserver for robustness
const sliderObserver = new ResizeObserver(() => {
    requestAnimationFrame(syncSliderImages);
});
document.querySelectorAll('#galeria .group').forEach(el => sliderObserver.observe(el));

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
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                // If a Main CTA is visible, HIDE the sticky bar
                stickyBar.classList.add('translate-y-full', 'opacity-0', 'pointer-events-none');
            } else {
                // Only show if none are visible (simplified logic for now, works for distant sections)
                // Re-check all triggers in case multiple observers fire
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


// =================================================================
// 9. SMART ANIMATION ENGINE (Premium Performance)
// =================================================================
document.addEventListener('DOMContentLoaded', () => {
    // Select heavy animated elements
    const heavyElements = document.querySelectorAll(
        '.btn-gold-liquid, .animate-pulse-gold, .glass-card, .service-card-skin, #particles-js'
    );

    if (heavyElements.length === 0) return;

    const smartObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                // In viewport: RESUME animation
                entry.target.classList.remove('paused');
            } else {
                // Out viewport: PAUSE animation (Release CPU/GPU)
                entry.target.classList.add('paused');
            }
        });
    }, {
        root: null,
        rootMargin: '100px 0px', // Resume slightly before entering screen
        threshold: 0.01
    });

    heavyElements.forEach(el => smartObserver.observe(el));
    console.log(`⚡ Smart Animation Engine: Managing ${heavyElements.length} premium elements`);
});
