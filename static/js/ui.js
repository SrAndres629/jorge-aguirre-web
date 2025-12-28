/**
 * UI.js - Core Frontend Logic & Interaction Manager
 * Refactored for High-Performance (60fps Mobile) & Non-Blocking Init
 */

const UI = {
    init() {
        // Critical: Nav & Basic Interactions (Immediate)
        this.NavManager.init();

        // Non-Critical: Sliders & Heavy Observers (Deferred)
        // Use requestIdleCallback if available, else setTimeout
        if ('requestIdleCallback' in window) {
            requestIdleCallback(() => {
                this.SliderManager.init();
                this.PerformanceManager.init();
            });
        } else {
            setTimeout(() => {
                this.SliderManager.init();
                this.PerformanceManager.init();
            }, 50);
        }

        console.log('✅ UI Core Initialized (Non-Blocking Pattern)');
    },

    /**
     * Module: SliderManager
     * Handles Before/After image comparison sliders with touch support
     */
    SliderManager: {
        sliders: [],
        observer: null,

        init() {
            const sliderContainers = document.querySelectorAll('.slider-container');
            if (!sliderContainers.length) return;

            // Optimization: Only initialize slider logic when visible
            this.setupIntersectionObserver();

            sliderContainers.forEach(slider => {
                this.observer.observe(slider);
            });

            // Handle resize to keep sliders synced
            window.addEventListener('resize', this.debounce(() => {
                this.syncAllSliders();
            }, 250));
        },

        setupIntersectionObserver() {
            this.observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        this.setupSlider(entry.target);
                        this.observer.unobserve(entry.target); // Initialize once
                    }
                });
            }, { rootMargin: '100px' });
        },

        setupSlider(container) {
            // Check if already initialized to avoid duplicates
            if (container.dataset.initialized) return;

            const range = container.querySelector('.slider-range');
            const foreground = container.querySelector('.foreground-img');
            const thumb = container.querySelector('.slider-thumb');

            if (!range || !foreground || !thumb) return;

            const update = () => {
                const val = range.value;
                // Use requestAnimationFrame for smooth 60fps
                requestAnimationFrame(() => {
                    foreground.style.setProperty('clip-path', `polygon(0 0, ${val}% 0, ${val}% 100%, 0 100%)`);
                    thumb.style.left = `${val}%`;
                });
            };

            // Touch events (passive for performance)
            range.addEventListener('input', update, { passive: true });
            range.addEventListener('touchmove', () => { }, { passive: true }); // iOS fix

            // Initial update
            update();
            container.dataset.initialized = "true";
            this.sliders.push({ container, range, update });
        },

        syncAllSliders() {
            this.sliders.forEach(s => s.update());
        },

        debounce(func, wait) {
            let timeout;
            return function (...args) {
                const later = () => {
                    clearTimeout(timeout);
                    func(...args);
                };
                clearTimeout(timeout);
                timeout = setTimeout(later, wait);
            };
        }
    },

    /**
     * Module: NavManager
     * Handles Sticky Header and Mobile Menu Scroll Lock
     */
    NavManager: {
        nav: document.getElementById('mainNav'),
        mobileMenuBtn: document.getElementById('mobileMenuBtn'),
        mobileMenuDiv: document.getElementById('mobileMenu'),
        body: document.body,
        isMenuOpen: false,

        init() {
            if (!this.nav) return;
            this.setupStickyObserver();
            this.setupMobileMenu();
        },

        setupStickyObserver() {
            // Create a sentinel element at the top of the body
            const sentinel = document.createElement('div');
            Object.assign(sentinel.style, {
                position: 'absolute',
                top: '100px',
                left: '0',
                width: '1px',
                height: '1px',
                pointerEvents: 'none'
            });
            document.body.prepend(sentinel);

            const observer = new IntersectionObserver((entries) => {
                const isTop = entries[0].isIntersecting;
                if (!isTop) {
                    this.nav.classList.add('glass-nav', 'border-b', 'border-white/10', 'bg-luxury-black/90', 'backdrop-blur-md');
                    this.nav.classList.remove('bg-transparent');
                } else {
                    this.nav.classList.remove('glass-nav', 'border-b', 'border-white/10', 'bg-luxury-black/90', 'backdrop-blur-md');
                    this.nav.classList.add('bg-transparent');
                }
            }, { threshold: 0 });

            observer.observe(sentinel);
        },

        setupMobileMenu() {
            if (!this.mobileMenuBtn || !this.mobileMenuDiv) return;

            const toggle = () => this.toggleMenu();
            this.mobileMenuBtn.addEventListener('click', toggle);

            // Close menu when clicking a link
            const links = this.mobileMenuDiv.querySelectorAll('a');
            links.forEach(link => link.addEventListener('click', () => {
                if (this.isMenuOpen) toggle();
            }));
        },

        toggleMenu() {
            this.isMenuOpen = !this.isMenuOpen;
            if (this.isMenuOpen) {
                this.mobileMenuDiv.classList.remove('hidden');
                this.body.style.overflow = 'hidden'; // Lock scroll
            } else {
                this.mobileMenuDiv.classList.add('hidden');
                this.body.style.overflow = ''; // Unlock scroll
            }
        }
    },

    /**
     * Module: PerformanceManager
     * Pauses heavy animations when off-screen
     */
    PerformanceManager: {
        observer: null,

        init() {
            this.setupObserver();
            this.observeHeavyElements();
        },

        setupObserver() {
            this.observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.classList.remove('paused-animation');
                    } else {
                        entry.target.classList.add('paused-animation');
                    }
                });
            }, { rootMargin: '50px' });
        },

        observeHeavyElements() {
            // Select elements with heavy CSS animations or canvas
            const targets = document.querySelectorAll('#particles-js, .animate-shine, .btn-gold-liquid');
            targets.forEach(target => this.observer.observe(target));
        }
    }
};

// Initialize when DOM is ready (deferred)
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => UI.init());
} else {
    UI.init();
}
