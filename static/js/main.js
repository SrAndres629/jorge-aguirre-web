/* =================================================================
   JORGE AGUIRRE FLORES - MAIN.JS
   Lógica de conversiones, tracking avanzado y UI interactiva
   ================================================================= */

// =================================================================
// 1. META PIXEL INITIALIZATION
// =================================================================
(function () {
    !function (f, b, e, v, n, t, s) {
        if (f.fbq) return; n = f.fbq = function () {
            n.callMethod ?
            n.callMethod.apply(n, arguments) : n.queue.push(arguments)
        }; if (!f._fbq) f._fbq = n;
        n.push = n; n.loaded = !0; n.version = '2.0'; n.queue = []; t = b.createElement(e); t.async = !0;
        t.src = v; s = b.getElementsByTagName(e)[0]; s.parentNode.insertBefore(t, s)
    }(window,
        document, 'script', 'https://connect.facebook.net/en_US/fbevents.js');

    if (window.META_PIXEL_ID) {
        fbq('init', window.META_PIXEL_ID);
        fbq('track', 'PageView', {}, { eventID: window.META_EVENT_ID });
    }
})();

// =================================================================
// 2. VIEWCONTENT TRACKING POR SERVICIO (Retargeting Segmentado)
// =================================================================
(function () {
    // Mapeo de secciones a categorías para retargeting
    const serviceCategories = {
        'cejas': { name: 'Microblading de Cejas', category: 'cejas', price: 350 },
        'ojos': { name: 'Delineado Permanente', category: 'ojos', price: 300 },
        'labios': { name: 'Labios Full Color', category: 'labios', price: 400 }
    };

    // Trackear qué secciones ya se enviaron (evitar duplicados)
    const viewedSections = new Set();

    // Observer para detectar cuando una sección es visible
    const observerOptions = {
        root: null,
        rootMargin: '0px',
        threshold: 0.5 // 50% visible = usuario está viendo la sección
    };

    const sectionObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const sectionId = entry.target.dataset.serviceCategory;
                
                if (sectionId && !viewedSections.has(sectionId) && serviceCategories[sectionId]) {
                    viewedSections.add(sectionId);
                    const service = serviceCategories[sectionId];
                    
                    // Enviar ViewContent a Meta Pixel
                    if (typeof fbq === 'function') {
                        fbq('track', 'ViewContent', {
                            content_name: service.name,
                            content_category: service.category,
                            content_type: 'service',
                            value: service.price,
                            currency: 'USD'
                        });
                        console.log(`📊 ViewContent enviado: ${service.name}`);
                    }

                    // También notificar al servidor (CAPI)
                    try {
                        fetch('/track-viewcontent', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ 
                                service: service.name,
                                category: service.category
                            })
                        });
                    } catch (e) {
                        console.log('ViewContent CAPI fallback:', e);
                    }
                }
            }
        });
    }, observerOptions);

    // Observar las secciones de servicios cuando el DOM esté listo
    document.addEventListener('DOMContentLoaded', () => {
        document.querySelectorAll('[data-service-category]').forEach(section => {
            sectionObserver.observe(section);
        });
    });
})();

// =================================================================
// 3. CONVERSION HANDLER (WhatsApp + Tracking Mejorado)
// =================================================================
async function handleConversion(source) {
    const eventId = 'lead_' + Date.now();

    // Mapeo de fuentes a servicios para mensaje personalizado
    const serviceMap = {
        'Hero CTA': 'maquillaje permanente',
        'Sticky Header': 'maquillaje permanente',
        'Floating Button': 'servicios',
        'Galería CTA': 'transformación',
        'CTA Final': 'valoración',
        'Servicio Cejas': 'Microblading de Cejas',
        'Servicio Ojos': 'Delineado Permanente de Ojos',
        'Servicio Labios': 'Labios Full Color'
    };

    const serviceName = serviceMap[source] || source;

    // Notificar a Meta Pixel (Navegador)
    if (typeof fbq === 'function') {
        fbq('track', 'Lead', { 
            content_name: source,
            content_category: serviceName
        }, { eventID: eventId });
    }

    // Notificar a Google Tag Manager (dataLayer)
    if (typeof dataLayer !== 'undefined') {
        dataLayer.push({
            'event': 'lead_whatsapp',
            'lead_source': source,
            'lead_service': serviceName
        });
    }

    // Notificar al Servidor (Python - Meta CAPI)
    try {
        fetch('/track-lead', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ event_id: eventId, source: source })
        });
    } catch (e) {
        console.log('CAPI fallback failed:', e);
    }

    // Redirigir a WhatsApp con MENSAJE PERSUASIVO MEJORADO
    const phone = "59176375924";
    const text = `Hola Jorge 👋 Vi sus resultados de ${serviceName} y me encantaron. ¿Podría agendar una valoración gratuita para ver si soy candidata?`;
    const url = `https://wa.me/${phone}?text=${encodeURIComponent(text)}`;

    setTimeout(() => {
        window.open(url, '_blank');
    }, 300);
}

// =================================================================
// 4. STICKY HEADER SCROLL HANDLER
// =================================================================
(function () {
    const stickyNav = document.getElementById('stickyNav');
    const urgencyBanner = document.getElementById('urgencyBanner');

    if (stickyNav && urgencyBanner) {
        window.addEventListener('scroll', () => {
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
        }, { passive: true });
    }
})();

// =================================================================
// 5. BEFORE/AFTER SLIDERS (GPU Optimized)
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

    slider.addEventListener('mousedown', (e) => {
        isDown = true;
        updateSlider(e.clientX);
    });
    slider.addEventListener('mousemove', (e) => {
        if (isDown) updateSlider(e.clientX);
    });
    slider.addEventListener('mouseup', () => isDown = false);
    slider.addEventListener('mouseleave', () => isDown = false);

    slider.addEventListener('touchstart', (e) => {
        isDown = true;
        updateSlider(e.touches[0].clientX);
    }, { passive: true });
    slider.addEventListener('touchmove', (e) => {
        if (isDown) updateSlider(e.touches[0].clientX);
    }, { passive: true });
    slider.addEventListener('touchend', () => isDown = false);
});

// =================================================================
// 6. FAQ ACCORDION (Auto-close others)
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

console.log('✅ Jorge Aguirre Flores Web - Scripts loaded (v2.0 - ViewContent + Retargeting)');
