/**
 * UI.js - Core Frontend Logic & Interaction Manager
 * Handles Sliders, Navigation, and Performance Optimization
 */

const UI = {
    init() {
        this.SliderManager.init();
        this.NavManager.init();
        this.PerformanceManager.init();
        console.log('✅ UI Core Initialized');
    },

    /**
     * Module: SliderManager
     * Handles Before/After image comparison sliders with touch support
     */
    SliderManager: {
        sliders: [],

        init() {
            const sliders = document.querySelectorAll('.slider-container');
            if (!sliders.length) return;

            sliders.forEach(slider => {
                this.setupSlider(slider);
            });

            // Handle resize to keep sliders synced
            window.addEventListener('resize', this.debounce(() => {
                this.syncAllSliders();
            }, 250));
        },

        setupSlider(container) {
            const range = container.querySelector('.slider-range');
            const foreground = container.querySelector('.foreground-img');
            const thumb = container.querySelector('.slider-thumb');

            if (!range || !foreground || !thumb) return;

            const update = () => {
                const val = range.value;
                requestAnimationFrame(() => {
                    foreground.style.setProperty('clip-path', `polygon(0 0, ${val}% 0, ${val}% 100%, 0 100%)`);
                    thumb.style.left = `${val}%`;
                });
            };

            // Touch events (passive for performance)
            range.addEventListener('input', update);
            range.addEventListener('touchmove', (e) => {
                // Logic to handle custom touch tracking if range input fails on specific iOS versions
                // For now, relying on native range with passive listener usually works well
            }, { passive: true });

            // Initial update
            update();

            this.sliders.push({ container, range, update });
        },

        syncAllSliders() {
            this.sliders.forEach(s => s.update());
        },

        debounce(func, wait) {
            let timeout;
            return function executedFunction(...args) {
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
            sentinel.style.position = 'absolute';
            sentinel.style.top = '100px'; // Trigger point
            sentinel.style.left = '0';
            sentinel.style.width = '1px';
            sentinel.style.height = '1px';
            sentinel.style.pointerEvents = 'none';
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

            this.mobileMenuBtn.addEventListener('click', () => {
                this.toggleMenu();
            });

            // Close menu when clicking a link
            const links = this.mobileMenuDiv.querySelectorAll('a');
            links.forEach(link => {
                link.addEventListener('click', () => {
                    if (this.isMenuOpen) this.toggleMenu();
                });
            });
        },

        toggleMenu() {
            this.isMenuOpen = !this.isMenuOpen;

            if (this.isMenuOpen) {
                // Lock Scroll
                this.mobileMenuDiv.classList.remove('hidden');
                // Small delay to allow display block to apply before transition could ideally be handled here, 
                // but for simple visibility toggle:
                this.body.style.overflow = 'hidden';
            } else {
                // Unlock Scroll
                this.mobileMenuDiv.classList.add('hidden');
                this.body.style.overflow = '';
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

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => UI.init());
