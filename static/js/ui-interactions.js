/**
 * TechMate - UI Interactions & Animations
 * Custom JavaScript for enhanced user experience
 */
document.addEventListener("DOMContentLoaded", () => {
    
    // 1. Animated Number Counters for Dashboard Stats
    function animateCounters() {
        const counters = document.querySelectorAll('.counter-value');
        const speed = 200;

        counters.forEach(counter => {
            const updateCount = () => {
                const target = +counter.getAttribute('data-target');
                const count = +counter.innerText.replace(/,/g, '');
                const inc = target / speed;

                if (count < target) {
                    counter.innerText = Math.ceil(count + inc).toLocaleString();
                    setTimeout(updateCount, 15);
                } else {
                    counter.innerText = target.toLocaleString();
                }
            };
            updateCount();
        });
    }

    // Initialize counters if they exist
    if (document.querySelectorAll('.counter-value').length > 0) {
        setTimeout(animateCounters, 300);
    }

    // 2. Scroll Animation Observer (Staggered Fade-Ins)
    const observerOptions = {
        root: null,
        rootMargin: '0px',
        threshold: 0.1
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in-up');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    document.querySelectorAll('.animate-on-scroll').forEach((el) => {
        el.style.opacity = '0';
        observer.observe(el);
    });

    // 3. Navbar Glass Effect on Scroll
    const navbar = document.querySelector('#top-navbar');
    if (navbar) {
        window.addEventListener('scroll', () => {
            if (window.scrollY > 50) {
                navbar.style.boxShadow = '0 8px 32px 0 rgba(31, 38, 135, 0.15)';
                navbar.style.background = 'rgba(255, 255, 255, 0.95)';
            } else {
                navbar.style.boxShadow = '0 1px 3px 0 rgba(0, 0, 0, 0.1)';
                navbar.style.background = 'white';
            }
        });
    }

    // 4. Initialize Bootstrap Tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }

    // 5. Card Hover Effects Enhancement
    document.querySelectorAll('.card, .tm-card').forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transition = 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)';
        });
    });

    // 6. Button Click Ripple Effect
    document.querySelectorAll('.btn-modern, .tm-btn-primary').forEach(button => {
        button.addEventListener('click', function(e) {
            const ripple = document.createElement('span');
            const rect = this.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            const x = e.clientX - rect.left - size / 2;
            const y = e.clientY - rect.top - size / 2;
            
            ripple.style.width = ripple.style.height = size + 'px';
            ripple.style.left = x + 'px';
            ripple.style.top = y + 'px';
            ripple.classList.add('ripple');
            
            this.appendChild(ripple);
            
            setTimeout(() => ripple.remove(), 600);
        });
    });

    // 7. Smooth Scroll for Anchor Links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const targetId = this.getAttribute('href');
            if (targetId !== '#' && document.querySelector(targetId)) {
                e.preventDefault();
                document.querySelector(targetId).scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
});

// 8. Chart Export Functionality
function exportChart(chartId, filename) {
    const canvas = document.getElementById(chartId);
    if(canvas) {
        const imageURL = canvas.toDataURL("image/png");
        const a = document.createElement('a');
        a.href = imageURL;
        a.download = `${filename}_TechMate.png`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
    }
}

// 9. Toast Notification System
window.tmToast = function(message, type = 'success') {
    const container = document.getElementById('tm-toast-container') || createToastContainer();
    
    const toast = document.createElement('div');
    toast.className = `tm-card tm-glass p-3 mb-2 d-flex align-items-center shadow-lg`;
    toast.style.borderLeft = `4px solid var(--tm-${type})`;
    toast.style.animation = 'slideInRight 0.3s forwards';
    
    const iconMap = {
        success: 'check-circle-fill text-success',
        danger: 'exclamation-triangle-fill text-danger',
        info: 'info-circle-fill text-info'
    };
    
    toast.innerHTML = `
        <i class="bi bi-${iconMap[type]} fs-4 me-3"></i>
        <div class="fw-semibold text-dark">${message}</div>
    `;
    
    container.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'fadeOut 0.3s forwards';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
};

function createToastContainer() {
    const div = document.createElement('div');
    div.id = 'tm-toast-container';
    div.style.position = 'fixed';
    div.style.bottom = '20px';
    div.style.right = '20px';
    div.style.zIndex = '9999';
    document.body.appendChild(div);
    return div;
}
