/* =================================================================
   MOTION.JS - Scrollytelling & Creative Motion
   Lenis Smooth Scroll, GSAP ScrollTrigger, Parallax
   "Motion with Meaning" - Luxury feel
   ================================================================= */

// =================================================================
// 1. LENIS SMOOTH SCROLL (Butter Feel)
// =================================================================
let lenis = null;

function initLenisScroll() {
    if (typeof Lenis === 'undefined') {
        console.warn('⚠️ Lenis not loaded, retrying...');
        setTimeout(initLenisScroll, 100);
        return;
    }

    lenis = new Lenis({
        duration: 1.2,          // Scroll duration (luxury feel)
        easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)), // Ease out expo
        orientation: 'vertical',
        gestureOrientation: 'vertical',
        smoothWheel: true,
        wheelMultiplier: 0.8,   // Slower wheel = more premium
        touchMultiplier: 1.5,   // Touch slightly faster for mobile
        infinite: false,
    });

    // RAF loop for Lenis
    function raf(time) {
        lenis.raf(time);
        requestAnimationFrame(raf);
    }
    requestAnimationFrame(raf);

    // Sync Lenis with GSAP ScrollTrigger
    if (typeof gsap !== 'undefined' && gsap.ScrollTrigger) {
        lenis.on('scroll', ScrollTrigger.update);
        gsap.ticker.add((time) => {
            lenis.raf(time * 1000);
        });
        gsap.ticker.lagSmoothing(0);
    }

    console.log('🧈 Lenis Smooth Scroll initialized');
}

// =================================================================
// 2. GSAP SCROLLTRIGGER - Staggered Entrances
// =================================================================
function initGSAPAnimations() {
    if (typeof gsap === 'undefined' || typeof ScrollTrigger === 'undefined') {
        console.warn('⚠️ GSAP not loaded, retrying...');
        setTimeout(initGSAPAnimations, 100);
        return;
    }

    gsap.registerPlugin(ScrollTrigger);

    // --- Service Cards: Staggered entrance from bottom ---
    const serviceCards = document.querySelectorAll('.service-card, [data-aos="fade-up"]');

    // Find cards in the "Proceso" section (3 steps)
    const procesoCards = document.querySelectorAll('.grid.md\\:grid-cols-3 > div');

    if (procesoCards.length >= 3) {
        // Set initial state
        gsap.set(procesoCards, {
            opacity: 0,
            y: 60,
            scale: 0.95
        });

        // Staggered entrance animation
        gsap.to(procesoCards, {
            opacity: 1,
            y: 0,
            scale: 1,
            duration: 0.8,
            ease: "power3.out",
            stagger: 0.2,  // 0.2s delay between each card
            scrollTrigger: {
                trigger: procesoCards[0].closest('section'),
                start: "top 75%",
                toggleActions: "play none none reverse"
            }
        });
    }

    // --- Testimonial Cards: Staggered entrance ---
    const testimonialCards = document.querySelectorAll('.service-card-skin');

    if (testimonialCards.length >= 1) {
        gsap.set(testimonialCards, {
            opacity: 0,
            y: 80,
            rotateX: 10
        });

        gsap.to(testimonialCards, {
            opacity: 1,
            y: 0,
            rotateX: 0,
            duration: 0.9,
            ease: "power2.out",
            stagger: 0.15,
            scrollTrigger: {
                trigger: testimonialCards[0].closest('section'),
                start: "top 70%",
                toggleActions: "play none none reverse"
            }
        });
    }

    // --- Before/After Sliders: Fade in with scale ---
    const sliders = document.querySelectorAll('.ba-slider');

    if (sliders.length >= 1) {
        gsap.set(sliders, {
            opacity: 0,
            scale: 0.9,
            y: 40
        });

        gsap.to(sliders, {
            opacity: 1,
            scale: 1,
            y: 0,
            duration: 0.7,
            ease: "power2.out",
            stagger: 0.12,
            scrollTrigger: {
                trigger: sliders[0].closest('section'),
                start: "top 75%",
                toggleActions: "play none none reverse"
            }
        });
    }

    console.log('🎬 GSAP ScrollTrigger animations initialized');
}

// =================================================================
// 3. HERO PARALLAX (Subtle depth)
// =================================================================
function initParallax() {
    if (typeof gsap === 'undefined' || typeof ScrollTrigger === 'undefined') {
        setTimeout(initParallax, 100);
        return;
    }

    gsap.registerPlugin(ScrollTrigger);

    // Hero image parallax - moves 20% slower than scroll
    const heroImage = document.querySelector('header img[fetchpriority="high"]');

    if (heroImage) {
        gsap.to(heroImage, {
            yPercent: 20,  // 20% of its height
            ease: "none",
            scrollTrigger: {
                trigger: "header",
                start: "top top",
                end: "bottom top",
                scrub: 0.5  // Smooth interpolation (0.5s delay)
            }
        });
    }

    // Gold particles container - slight parallax
    const particles = document.getElementById('particles-js');
    if (particles) {
        gsap.to(particles, {
            yPercent: 10,
            ease: "none",
            scrollTrigger: {
                trigger: "header",
                start: "top top",
                end: "bottom top",
                scrub: true
            }
        });
    }

    console.log('🌟 Parallax effects initialized');
}

// =================================================================
// 4. MAGNETIC BUTTON (Mobile CTA Attraction)
// =================================================================
function initMagneticButton() {
    const magneticBtns = document.querySelectorAll('#whatsappFloat');

    magneticBtns.forEach(btn => {
        // Only on larger screens (pointer: fine)
        if (!window.matchMedia('(pointer: fine)').matches) return;

        btn.addEventListener('mousemove', (e) => {
            const rect = btn.getBoundingClientRect();
            const x = e.clientX - rect.left - rect.width / 2;
            const y = e.clientY - rect.top - rect.height / 2;

            // Magnetic attraction (30% of distance)
            btn.style.transform = `translate(${x * 0.3}px, ${y * 0.3}px) scale(1.05)`;
        });

        btn.addEventListener('mouseleave', () => {
            // Elastic snap back
            btn.style.transition = 'transform 0.4s cubic-bezier(0.34, 1.56, 0.64, 1)';
            btn.style.transform = 'translate(0, 0) scale(1)';
            setTimeout(() => {
                btn.style.transition = '';
            }, 400);
        });
    });

    console.log('🧲 Magnetic button effects initialized');
}

// =================================================================
// 5. MOBILE AUTO-HOVER (Scroll Triggered)
// =================================================================
function initMobileScrollTriggers() {
    if (!window.matchMedia('(max-width: 768px)').matches) return;

    if (typeof gsap === 'undefined' || typeof ScrollTrigger === 'undefined') {
        setTimeout(initMobileScrollTriggers, 100);
        return;
    }

    gsap.registerPlugin(ScrollTrigger);

    // Target cards to animate state when centered
    const targets = document.querySelectorAll('.service-card-skin, .process-step, .ba-slider');

    targets.forEach(target => {
        ScrollTrigger.create({
            trigger: target,
            start: "top center+=100", // Start slightly below center
            end: "bottom center-=100", // End slightly above center
            toggleClass: { targets: target, className: "mobile-active" },
            // markers: true, // debug
        });
    });

    console.log('📱 Mobile ScrollTrigger auto-hover active');
}

// =================================================================
// 6. MOUSE SPOTLIGHT (Global Ambient)
// =================================================================
function initSpotlight() {
    const spotlight = document.getElementById('mouse-spotlight');
    if (!spotlight) return;

    // Use requestAnimationFrame for performance
    let x = 0, y = 0;
    let currentX = 0, currentY = 0;

    window.addEventListener('mousemove', (e) => {
        x = e.clientX;
        y = e.clientY;
    });

    function updateSpotlight() {
        // Smooth follow with simple lerp
        currentX += (x - currentX) * 0.1;
        currentY += (y - currentY) * 0.1;

        // Dynamic gold gradient
        spotlight.style.background = `radial-gradient(800px circle at ${currentX}px ${currentY}px, rgba(212, 175, 55, 0.08), transparent 50%)`;

        requestAnimationFrame(updateSpotlight);
    }
    updateSpotlight();

    console.log('🔦 Spotlight effect initialized');
}

// =================================================================
// 7. INITIALIZATION
// =================================================================
document.addEventListener('DOMContentLoaded', () => {
    // Wait a frame for all scripts to be ready
    requestAnimationFrame(() => {
        initLenisScroll();
        initGSAPAnimations();
        initParallax();
        initParallax();
        initMagneticButton();
        initMobileScrollTriggers();
        initSpotlight();
    });
});

// Fallback if DOMContentLoaded already fired
if (document.readyState === 'complete' || document.readyState === 'interactive') {
    requestAnimationFrame(() => {
        initLenisScroll();
        initGSAPAnimations();
        initParallax();
        initParallax();
        initMagneticButton();
        initMobileScrollTriggers();
        initSpotlight();
    });
}

console.log('✅ Motion.js loaded (Scrollytelling v1.1)');
