/**
 * SkillMesh — Global JavaScript Utilities
 * Smooth interactions, page transitions, and micro-animations
 */

document.addEventListener("DOMContentLoaded", () => {

    // ---- Smooth page transition on nav link click ----
    const navLinks = document.querySelectorAll('a.nav-link');
    navLinks.forEach(link => {
        link.addEventListener('click', function (e) {
            if (e.ctrlKey || e.metaKey || this.target === '_blank') return;
            if (this.classList.contains('active')) {
                e.preventDefault();
                return;
            }

            e.preventDefault();
            const href = this.href;
            const main = document.querySelector('.main-content');

            main.style.transition = 'opacity 0.18s ease, transform 0.18s ease';
            main.style.opacity = '0';
            main.style.transform = 'translateY(6px)';

            setTimeout(() => {
                window.location.href = href;
            }, 160);
        });
    });

    // ---- Intersection Observer for fade-in on scroll ----
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -40px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    document.querySelectorAll('.card, .project-card, .table-container').forEach(el => {
        if (!el.closest('.modal-content')) {
            el.style.opacity = '0';
            el.style.transform = 'translateY(12px)';
            el.style.transition = 'opacity 0.45s ease, transform 0.45s ease';
            observer.observe(el);
        }
    });

    // ---- Keyboard shortcut: Escape to close modals ----
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            document.querySelectorAll('.modal-overlay.active').forEach(modal => {
                modal.classList.remove('active');
            });
        }
    });

});
