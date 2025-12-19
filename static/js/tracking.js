/* =================================================================
   TRACKING.JS - Meta Pixel, CAPI, GTM, ViewContent
   OPTIMIZADO PARA MÁXIMO EMQ (Event Match Quality)
   ================================================================= */

// =================================================================
// 1. META PIXEL INITIALIZATION (Con external_id)
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
        // Inicializar Pixel con external_id para mejor matching
        const initData = {};
        if (window.EXTERNAL_ID) {
            initData.external_id = window.EXTERNAL_ID;
        }

        fbq('init', window.META_PIXEL_ID, initData);
        fbq('track', 'PageView', {}, { eventID: window.META_EVENT_ID });
        console.log('📊 Meta Pixel initialized with external_id');
    }
})();

// =================================================================
// 2. CONFIGURACIÓN DE TRACKING
// =================================================================
const TrackingConfig = {
    services: {
        'cejas': { name: 'Microblading de Cejas', category: 'cejas', price: 350 },
        'ojos': { name: 'Delineado Permanente', category: 'ojos', price: 300 },
        'labios': { name: 'Labios Full Color', category: 'labios', price: 400 }
    },
    phone: "59176375924",
    viewedSections: new Set(),

    // Capturar fbclid de la URL para tracking
    getFbclid: function () {
        const urlParams = new URLSearchParams(window.location.search);
        return urlParams.get('fbclid') || '';
    }
};

// =================================================================
// 3. VIEWCONTENT TRACKING (Retargeting Segmentado)
// =================================================================
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

                    // Generar event_id único para deduplicación
                    const eventId = 'vc_' + Date.now() + '_' + sectionId;

                    // Enviar ViewContent a Meta Pixel (navegador)
                    if (typeof fbq === 'function') {
                        fbq('track', 'ViewContent', {
                            content_name: service.name,
                            content_category: service.category,
                            content_type: 'service',
                            value: service.price,
                            currency: 'USD'
                        }, { eventID: eventId });
                        console.log(`📊 ViewContent: ${service.name}`);
                    }

                    // Enviar a servidor (CAPI) con event_id para deduplicación
                    fetch('/track-viewcontent', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            service: service.name,
                            category: service.category,
                            price: service.price,
                            event_id: eventId
                        })
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
// 4. CONVERSION HANDLER (WhatsApp + Tracking Dual)
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
    // Event ID único para deduplicación Pixel ↔ CAPI
    const eventId = 'lead_' + Date.now();
    const serviceName = serviceMap[source] || source;

    // 1. Meta Pixel (Navegador) - Con event_id
    if (typeof fbq === 'function') {
        fbq('track', 'Lead', {
            content_name: source,
            content_category: serviceName,
            lead_source: 'whatsapp'
        }, { eventID: eventId });
        console.log('📊 Lead event sent to Pixel');
    }

    // 2. Google Tag Manager (dataLayer)
    if (typeof dataLayer !== 'undefined') {
        dataLayer.push({
            'event': 'lead_whatsapp',
            'lead_source': source,
            'lead_service': serviceName,
            'event_id': eventId
        });
    }

    // 3. Servidor (Python - Meta CAPI) - MISMO event_id para deduplicación
    try {
        await fetch('/track-lead', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                event_id: eventId,
                source: source,
                service: serviceName
            })
        });
        console.log('📊 Lead event sent to CAPI');
    } catch (e) {
        console.log('CAPI error:', e);
    }

    // 4. Redirigir a WhatsApp con mensaje persuasivo
    const text = `Hola Jorge 👋 Vi sus resultados de ${serviceName} y me encantaron. ¿Podría agendar una valoración gratuita para ver si soy candidata?`;
    const url = `https://wa.me/${TrackingConfig.phone}?text=${encodeURIComponent(text)}`;

    setTimeout(() => window.open(url, '_blank'), 300);
}

// =================================================================
// 5. INICIALIZACIÓN
// =================================================================
console.log('✅ Tracking.js loaded (v3.0 - Optimized for EMQ)');
console.log('📊 fbclid detected:', TrackingConfig.getFbclid() ? 'YES' : 'NO');
