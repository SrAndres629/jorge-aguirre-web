/* =================================================================
   UI.JS - Interactividad y componentes UI
   Sliders, Sticky Header, FAQ Accordion
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

    // Mouse events
    slider.addEventListener('mousedown', (e) => { isDown = true; updateSlider(e.clientX); });
    slider.addEventListener('mousemove', (e) => { if (isDown) updateSlider(e.clientX); });
    slider.addEventListener('mouseup', () => isDown = false);
    slider.addEventListener('mouseleave', () => isDown = false);

    // Touch events (mobile)
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

console.log('✅ UI.js loaded');
