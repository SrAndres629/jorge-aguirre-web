/**
 * UI.JS - Core Frontend Logic & Interaction Manager (Senior Edition)
 * Architecture: Optimized Modular UI Engine
 */

const UIEngine = {
    initialized: false,

    init() {
        if (this.initialized) return;
        this.initialized = true;

        this.NavManager.init();

        // Performance-safe initialization
        if ('requestIdleCallback' in window) {
            requestIdleCallback(() => this.deferredInit());
        } else {
            setTimeout(() => this.deferredInit(), 50);
        }

        console.log('✨ [Senior Architecture] UI Engine Active');
    },

    deferredInit() {
        this.SliderManager.init();
        this.PerformanceManager.init();
    },

    /**
     * 1. SLIDER MANAGER (Before/After Comparisons)
     */
    SliderManager: {
        sliders: [],
        observer: null,

        init() {
            const containers = document.querySelectorAll('.slider-container');
            if (!containers.length) return;

            this.setupObserver();
            containers.forEach(el => this.observer.observe(el));

            // Sync on resize
            window.addEventListener('resize', this.debounce(() => {
                this.sliders.forEach(s => s.update());
            }, 250), { passive: true });
        },

        setupObserver() {
            this.observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        this.setupSlider(entry.target);
                        this.observer.unobserve(entry.target);
                    }
                });
            }, { rootMargin: '100px' });
        },

        setupSlider(container) {
            if (container.dataset.initialized) return;

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

            range.addEventListener('input', update, { passive: true });

            update();
            container.dataset.initialized = "true";
            this.sliders.push({ update });
        },

        debounce(func, wait) {
            let timeout;
            return (...args) => {
                clearTimeout(timeout);
                timeout = setTimeout(() => func(...args), wait);
            };
        }
    },

    /**
     * 2. NAV MANAGER (Sticky Glass Logic)
     */
    NavManager: {
        init() {
            this.nav = document.getElementById('mainNav');
            this.menuBtn = document.getElementById('mobileMenuBtn');
            this.menuDiv = document.getElementById('mobileMenu');

            if (!this.nav) return;
            this.setupMobileMenu();
        },

        setupMobileMenu() {
            if (!this.menuBtn || !this.menuDiv) return;

            const toggle = () => {
                const isOpen = !this.menuDiv.classList.contains('hidden');
                this.menuDiv.classList.toggle('hidden', isOpen);
                document.body.style.overflow = isOpen ? '' : 'hidden';
            };

            this.menuBtn.addEventListener('click', toggle);
            this.menuDiv.querySelectorAll('a').forEach(link => {
                link.addEventListener('click', () => {
                    this.menuDiv.classList.add('hidden');
                    document.body.style.overflow = '';
                });
            });
        }
    },

    /**
     * 3. PERFORMANCE MANAGER (Eco-Mode Animations)
     */
    PerformanceManager: {
        init() {
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    entry.target.classList.toggle('paused-animation', !entry.isIntersecting);
                });
            }, { rootMargin: '50px' });

            document.querySelectorAll('#particles-js, .animate-shine, .btn-gold-liquid')
                .forEach(el => observer.observe(el));
        }
    }
};

// Init
if (document.readyState === 'complete' || document.readyState === 'interactive') {
    UIEngine.init();
} else {
    document.addEventListener('DOMContentLoaded', () => UIEngine.init(), { once: true });
}
