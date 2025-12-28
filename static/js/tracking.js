/* =================================================================
   TRACKING.JS - Meta Pixel & CAPI Universal Engine (Senior Edition)
   Architecture: Idempotent Single-Instance Tracker
   ================================================================= */

const TrackingEngine = {
    initialized: false,
    viewedSections: new Set(),

    config: {
        services: window.SERVICES_CONFIG || {},
        phone: (window.CONTACT_CONFIG && window.CONTACT_CONFIG.phone) || "59176375924",
    },

    init() {
        if (this.initialized) return;
        this.initialized = true;

        this.setupPixel();
        this.setupViewContentObserver();
        this.setupSliderListeners();

        console.log('📊 [Senior Architecture] Tracking Engine Active (Pixel + CAPI)');
    },

    /**
     * 1. META PIXEL INITIALIZATION
     */
    setupPixel() {
        if (window.fbq) return;

        !function (f, b, e, v, n, t, s) {
            if (f.fbq) return; n = f.fbq = function () {
                n.callMethod ? n.callMethod.apply(n, arguments) : n.queue.push(arguments)
            }; if (!f._fbq) f._fbq = n;
            n.push = n; n.loaded = !0; n.version = '2.0'; n.queue = []; t = b.createElement(e); t.async = !0;
            t.src = v; s = b.getElementsByTagName(e)[0]; s.parentNode.insertBefore(t, s)
        }(window, document, 'script', 'https://connect.facebook.net/en_US/fbevents.js');

        if (window.META_PIXEL_ID) {
            const initData = window.EXTERNAL_ID ? { external_id: window.EXTERNAL_ID } : {};
            fbq('init', window.META_PIXEL_ID, initData);
            fbq('track', 'PageView', {}, { eventID: window.META_EVENT_ID });
        }
    },

    /**
     * 2. VIEWCONTENT OBSERVER (Specific Interest)
     */
    setupViewContentObserver() {
        const observerOptions = { threshold: 0.6 };
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const sectionId = entry.target.dataset.serviceCategory || entry.target.dataset.trackingId;
                    if (sectionId && !this.viewedSections.has(sectionId)) {
                        this.viewedSections.add(sectionId);
                        this.trackIndividualView(sectionId);
                    }
                }
            });
        }, observerOptions);

        document.querySelectorAll('[data-service-category]').forEach(el => observer.observe(el));
    },

    trackIndividualView(sectionId) {
        const serviceData = this.config.services[sectionId] || { name: sectionId, category: 'General', price: 0 };
        const eventId = `vc_${Date.now()}_${sectionId}`;

        // Pixel
        if (window.fbq) {
            fbq('track', 'ViewContent', {
                content_name: serviceData.name,
                content_category: serviceData.category,
                content_ids: [sectionId],
                content_type: 'product',
                value: serviceData.price,
                currency: 'USD'
            }, { eventID: eventId });
        }

        // CAPI
        this.sendToCAPI('ViewContent', {
            event_id: eventId,
            service: serviceData.name,
            category: serviceData.category,
            price: serviceData.price
        });
    },

    /**
     * 3. SLIDER INTERACTION LISTENERS
     */
    setupSliderListeners() {
        const sliders = document.querySelectorAll('.ba-slider');
        const serviceNames = ['Microblading 3D', 'Cejas Sombra', 'Delineado Permanente', 'Labios Full Color'];
        const serviceIds = ['microblading_3d', 'cejas_sombra', 'delineado_ojos', 'labios_full'];

        sliders.forEach((slider, index) => {
            const trackInteraction = () => {
                if (slider.dataset.tracked) return;
                slider.dataset.tracked = "true";

                const serviceName = serviceNames[index] || 'Servicio Desconocido';
                const serviceId = serviceIds[index] || 'unknown';

                if (window.fbq) {
                    fbq('trackCustom', 'SliderInteraction', {
                        content_name: serviceName,
                        content_id: serviceId,
                        interaction_type: 'compare_before_after'
                    });
                }

                this.sendToCAPI('SliderInteraction', {
                    event_id: `slider_${Date.now()}_${serviceId}`,
                    service_name: serviceName,
                    service_id: serviceId,
                    interaction_type: 'compare_before_after'
                });
            };

            slider.addEventListener('click', trackInteraction, { passive: true });
            slider.addEventListener('touchmove', trackInteraction, { passive: true });
        });
    },

    /**
     * 4. CONVERSION HANDLER (WhatsApp Leads)
     */
    async handleConversion(source) {
        const triggerMap = {
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

        const eventId = `lead_${Date.now()}`;
        const data = triggerMap[source] || { name: source, id: 'unknown', intent: 'general' };

        // Pixel
        if (window.fbq) {
            fbq('track', 'Lead', {
                content_name: data.name,
                content_category: data.intent,
                content_ids: [data.id],
                lead_source: 'whatsapp',
                trigger_location: source
            }, { eventID: eventId });
        }

        // CAPI
        this.sendToCAPI('Lead', {
            event_id: eventId,
            source: source,
            service_data: data
        });

        // WhatsApp Redirect
        let message = `Hola Jorge 👋`;
        if (data.intent === 'service_interest') message += ` Me interesa el *${data.name}*. ¿Podría ver si soy candidata?`;
        else if (data.intent === 'urgency') message += ` Quisiera aprovechar la *Oferta Limitada* de valoración gratuita.`;
        else message += ` Quisiera información sobre sus servicios de maquillaje permanente.`;

        window.open(`https://wa.me/${this.config.phone}?text=${encodeURIComponent(message)}`, '_blank');
    },

    /**
     * 5. CAPI HELPER
     */
    async sendToCAPI(eventName, customData) {
        const fbclid = new URLSearchParams(window.location.search).get('fbclid');
        const payload = {
            event_name: eventName,
            event_time: Math.floor(Date.now() / 1000),
            event_id: customData.event_id || `${eventName.toLowerCase()}_${Date.now()}`,
            event_source_url: window.location.href,
            action_source: "website",
            user_data: {
                external_id: window.EXTERNAL_ID || '',
                fbc: fbclid ? `fb.1.${Math.floor(Date.now() / 1000)}.${fbclid}` : null
            },
            custom_data: { ...customData, fbclid }
        };

        try {
            await fetch('/track/event', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload),
                keepalive: true
            });
        } catch (e) {
            console.warn(`[CAPI] Network Error for ${eventName}`);
        }
    }
};

// Global Exposure for UI clicks
window.handleConversion = (source) => TrackingEngine.handleConversion(source);

// Init
if (document.readyState === 'complete' || document.readyState === 'interactive') {
    TrackingEngine.init();
} else {
    document.addEventListener('DOMContentLoaded', () => TrackingEngine.init(), { once: true });
}
