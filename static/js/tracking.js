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
// 3. VIEWCONTENT TRACKING (Interés Específico - Scroll)
// =================================================================
(function () {
    const observerOptions = {
        root: null,
        rootMargin: '0px',
        threshold: 0.6 // Requiere 60% de visibilidad para confirmar interés
    };

    const sectionObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const sectionId = entry.target.dataset.serviceCategory || entry.target.dataset.trackingId;

                // Evitar duplicados en la misma sesión
                if (sectionId && !TrackingConfig.viewedSections.has(sectionId)) {
                    TrackingConfig.viewedSections.add(sectionId);

                    // Datos enriquecidos del servicio
                    const serviceData = TrackingConfig.services[sectionId] || { name: sectionId, category: 'General', price: 0 };
                    const eventId = 'vc_' + Date.now() + '_' + sectionId;

                    // A) Meta Pixel
                    if (typeof fbq === 'function') {
                        fbq('track', 'ViewContent', {
                            content_name: serviceData.name,
                            content_category: serviceData.category,
                            content_ids: [sectionId], // ID técnico para catálogo
                            content_type: 'product',
                            value: serviceData.price,
                            currency: 'USD'
                        }, { eventID: eventId });
                        console.log(`👁️ ViewContent: Interés en ${serviceData.name}`);
                    }

                    // B) Meta CAPI (Server)
                    sendToCAPI('ViewContent', {
                        event_id: eventId,
                        ...serviceData
                    });
                }
            }
        });
    }, observerOptions);

    document.addEventListener('DOMContentLoaded', () => {
        // Observar tarjetas de servicio
        document.querySelectorAll('[data-service-category]').forEach(el => sectionObserver.observe(el));
    });
})();

// =================================================================
// 4. ACTIVE INTEREST TRACKING (Interacción con Sliders)
// =================================================================
document.addEventListener('DOMContentLoaded', () => {
    // Detectar cuando alguien "juega" con el antes/después
    const sliders = document.querySelectorAll('.ba-slider');

    sliders.forEach((slider, index) => {
        // Identificar qué servicio es basado en el título cercano o orden
        // Asumimos orden: 0=Microblading, 1=Cejas Sombra, 2=Ojos, 3=Labios
        const serviceNames = ['Microblading 3D', 'Cejas Sombra', 'Delineado Permanente', 'Labios Full Color'];
        const serviceIds = ['microblading_3d', 'cejas_sombra', 'delineado_ojos', 'labios_full'];
        const serviceName = serviceNames[index] || 'Servicio Desconocido';
        const serviceId = serviceIds[index] || 'unknown_service';

        // Listener de 'una sola vez' para no saturar
        const trackInteraction = () => {
            if (slider.dataset.tracked) return;
            slider.dataset.tracked = "true";

            // Custom Event: "UserInterestedInResult"
            // Esto le dice a Facebook: "Este usuario comparó resultados activamente"
            if (typeof fbq === 'function') {
                fbq('trackCustom', 'SliderInteraction', {
                    content_name: serviceName,
                    content_id: serviceId,
                    interaction_type: 'compare_before_after'
                });
                console.log(`🔥 SliderInteraction: Jugó con ${serviceName}`);
            }
        };

        // Trigger en click o touch en el slider
        slider.addEventListener('click', trackInteraction);
        slider.addEventListener('touchmove', trackInteraction);
        // También en las flechas
        const arrows = slider.querySelectorAll('.slider-arrow');
        arrows.forEach(arrow => arrow.addEventListener('click', trackInteraction));
    });
});

// =================================================================
// 5. CONVERSION HANDLER (Smart Lead Tracking)
// =================================================================
const triggerMap = {
    // Mapa de "Fuente" -> { Nombre Servicio, ID Contenido, Intención }
    'Hero CTA': { name: 'Diseño de Cejas', id: 'hero_offer', intent: 'discovery' },
    'Sticky Header': { name: 'Consulta General', id: 'sticky_bar', intent: 'convenience' },
    'Floating Button': { name: 'Consulta WhatsApp', id: 'float_btn', intent: 'convenience' },
    'Galería CTA': { name: 'Transformación Completa', id: 'gallery_cta', intent: 'inspiration' },
    'CTA Final': { name: 'Oferta Limitada', id: 'final_offer', intent: 'urgency' },
    'Servicio Cejas': { name: 'Microblading 3D', id: 'service_brows', intent: 'service_interest' },
    'Servicio Ojos': { name: 'Delineado Ojos', id: 'service_eyes', intent: 'service_interest' },
    'Servicio Labios': { name: 'Labios Full Color', id: 'service_lips', intent: 'service_interest' },
    'Sticky Mobile CTA': { name: 'Cita VIP Móvil', id: 'mobile_sticky', intent: 'convenience' }
};

async function handleConversion(source) {
    const eventId = 'lead_' + Date.now();

    // Obtener datos ricos del trigger
    const triggerData = triggerMap[source] || { name: source, id: 'unknown', intent: 'general' };

    // 1. Meta Pixel (Browser)
    if (typeof fbq === 'function') {
        fbq('track', 'Lead', {
            content_name: triggerData.name,    // Ej: Microblading 3D
            content_category: triggerData.intent, // Ej: service_interest
            content_ids: [triggerData.id],     // Ej: service_brows
            lead_source: 'whatsapp',
            trigger_location: source
        }, { eventID: eventId });
        console.log(`🚀 Lead Enviado: Interés en ${triggerData.name} (${source})`);
    }

    // 2. DataLayer (GTM)
    if (typeof dataLayer !== 'undefined') {
        dataLayer.push({
            'event': 'lead_uwu', // Unique WhatsApp User
            'lead_context': triggerData,
            'event_id': eventId
        });
    }

    // 3. Meta CAPI (Server Helper)
    sendToCAPI('Lead', {
        event_id: eventId,
        source: source,
        service_data: triggerData
    });

    // 4. Redirigir a WhatsApp
    // Personalizamos el mensaje según lo que vio
    let message = `Hola Jorge 👋`;
    if (triggerData.intent === 'service_interest') {
        message += ` Me interesa el *${triggerData.name}*. ¿Podría ver si soy candidata?`;
    } else if (triggerData.intent === 'urgency') {
        message += ` Quisiera aprovechar la *Oferta Limitada* de valoración gratuita.`;
    } else {
        message += ` Quisiera información sobre sus servicios de maquillaje permanente.`;
    }

    const url = `https://wa.me/${TrackingConfig.phone}?text=${encodeURIComponent(message)}`;
    setTimeout(() => window.open(url, '_blank'), 300);
}

// Helper para CAPI
async function sendToCAPI(eventName, eventData) {
    try {
        await fetch('/track-' + eventName.toLowerCase(), {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(eventData)
        });
    } catch (e) {
        // Silent fail para no interrumpir UX
    }
}

// =================================================================
// 6. INICIALIZACIÓN
// =================================================================
console.log('⚡ Tracking.js v4.0 Loaded: Granular Interest Enabled');
console.log('🎯 Objetivos: Sliders, Tarjetas y Ofertas Específicas');
