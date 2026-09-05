/**
 * Semantic Employee & Skill Management System
 * Global JavaScript Utilities
 */

document.addEventListener("DOMContentLoaded", () => {
    // Add subtle interactive effects globally if needed

    // Example: Add a slight delay to links for the fade-out effect (optional polish)
    const links = document.querySelectorAll('a.nav-link');
    links.forEach(link => {
        link.addEventListener('click', function(e) {
            // Don't intercept if it's open in new tab or specific actions
            if (e.ctrlKey || e.metaKey || this.target === '_blank') return;
            
            // Allow default navigation to proceed
        });
    });
});
