/* =================================================================
   TRACKING.JS - Meta Pixel, CAPI, GTM, ViewContent
   Archivo separado para tracking y conversiones
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
    }(window, document, 'script', 'https://connect.facebook.net/en_US/fbevents.js');

    if (window.META_PIXEL_ID) {
        fbq('init', window.META_PIXEL_ID);
        fbq('track', 'PageView', {}, { eventID: window.META_EVENT_ID });
        console.log('📊 Meta Pixel initialized');
    }
})();

// =================================================================
// 2. VIEWCONTENT TRACKING POR SERVICIO (Retargeting Segmentado)
// =================================================================
const TrackingConfig = {
    services: {
        'cejas': { name: 'Microblading de Cejas', category: 'cejas', price: 350 },
        'ojos': { name: 'Delineado Permanente', category: 'ojos', price: 300 },
        'labios': { name: 'Labios Full Color', category: 'labios', price: 400 }
    },
    phone: "59176375924",
    viewedSections: new Set()
};

// Observer para detectar cuando una sección es visible
(function () {
    const observerOptions = {
        root: null,
        rootMargin: '0px',
        threshold: 0.5
    };

    const sectionObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const sectionId = entry.target.dataset.serviceCategory;

                if (sectionId && !TrackingConfig.viewedSections.has(sectionId) && TrackingConfig.services[sectionId]) {
                    TrackingConfig.viewedSections.add(sectionId);
                    const service = TrackingConfig.services[sectionId];

                    // Enviar ViewContent a Meta Pixel
                    if (typeof fbq === 'function') {
                        fbq('track', 'ViewContent', {
                            content_name: service.name,
                            content_category: service.category,
                            content_type: 'service',
                            value: service.price,
                            currency: 'USD'
                        });
                        console.log(`📊 ViewContent: ${service.name}`);
                    }

                    // Notificar al servidor (CAPI)
                    fetch('/track-viewcontent', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ service: service.name, category: service.category })
                    }).catch(e => console.log('ViewContent CAPI:', e));
                }
            }
        });
    }, observerOptions);

    document.addEventListener('DOMContentLoaded', () => {
        document.querySelectorAll('[data-service-category]').forEach(section => {
            sectionObserver.observe(section);
        });
    });
})();

// =================================================================
// 3. CONVERSION HANDLER (WhatsApp + Tracking)
// =================================================================
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

async function handleConversion(source) {
    const eventId = 'lead_' + Date.now();
    const serviceName = serviceMap[source] || source;

    // Meta Pixel (Navegador)
    if (typeof fbq === 'function') {
        fbq('track', 'Lead', {
            content_name: source,
            content_category: serviceName
        }, { eventID: eventId });
    }

    // Google Tag Manager (dataLayer)
    if (typeof dataLayer !== 'undefined') {
        dataLayer.push({
            'event': 'lead_whatsapp',
            'lead_source': source,
            'lead_service': serviceName
        });
    }

    // Servidor (Python - Meta CAPI)
    fetch('/track-lead', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ event_id: eventId, source: source })
    }).catch(e => console.log('CAPI:', e));

    // WhatsApp con mensaje persuasivo
    const text = `Hola Jorge 👋 Vi sus resultados de ${serviceName} y me encantaron. ¿Podría agendar una valoración gratuita para ver si soy candidata?`;
    const url = `https://wa.me/${TrackingConfig.phone}?text=${encodeURIComponent(text)}`;

    setTimeout(() => window.open(url, '_blank'), 300);
}

console.log('✅ Tracking.js loaded');
