// Mobile menu functionality
document.addEventListener('DOMContentLoaded', function() {
    const mobileMenuButton = document.getElementById('mobile-menu-button');
    const mobileMenu = document.getElementById('mobile-menu');

    // Initialize fade-up animations
    const contentTexts = document.querySelectorAll('.content-text.fade-up');

    // Create intersection observer for fade-up animations
    const observerOptions = {
        threshold: 0.2,
        rootMargin: '0px 0px -50px 0px'
    };

    const fadeUpObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                fadeUpObserver.unobserve(entry.target); // Only animate once
            }
        });
    }, observerOptions);

    // Observe all content text elements
    contentTexts.forEach(text => {
        fadeUpObserver.observe(text);
    });

    mobileMenuButton.addEventListener('click', function() {
        mobileMenu.classList.toggle('hidden');
    });

    // Close mobile menu when clicking outside
    document.addEventListener('click', function(event) {
        if (!mobileMenuButton.contains(event.target) && !mobileMenu.contains(event.target)) {
            mobileMenu.classList.add('hidden');
        }
    });

    // Enhanced smooth scrolling for all anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href').slice(1);
            const targetElement = document.getElementById(targetId);
            
            if (targetElement) {
                const headerHeight = 80; // Height of fixed header
                const elementPosition = targetElement.getBoundingClientRect().top;
                const offsetPosition = elementPosition + window.pageYOffset - headerHeight;

                window.scrollTo({
                    top: offsetPosition,
                    behavior: 'smooth'
                });
            }
        });
    });

    // Enhanced scroll to top functionality
    const scrollToTopBtn = document.querySelector('a[href="#hero"]');
    if (scrollToTopBtn) {
        scrollToTopBtn.addEventListener('click', function(e) {
            e.preventDefault();
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }

    // Show/Hide scroll to top button based on scroll position
    window.addEventListener('scroll', function() {
        const scrollToTopBtn = document.querySelector('a[href="#hero"]');
        if (scrollToTopBtn) {
            if (window.pageYOffset > 300) {
                scrollToTopBtn.style.opacity = '1';
                scrollToTopBtn.style.transform = 'translateY(0)';
            } else {
                scrollToTopBtn.style.opacity = '0';
                scrollToTopBtn.style.transform = 'translateY(20px)';
            }
        }
    });
});

// Enhanced FAQ functionality with smooth animations
document.addEventListener('DOMContentLoaded', function() {
    const faqItems = document.querySelectorAll('.faq-item');
    
    faqItems.forEach(item => {
        const question = item.querySelector('.faq-question');
        const answer = item.querySelector('.faq-answer');
        const icon = question.querySelector('span:last-child');
        
        // Function to close all FAQ items except the current one
        const closeOtherFaqs = (currentItem) => {
            faqItems.forEach(otherItem => {
                if (otherItem !== currentItem) {
                    const otherAnswer = otherItem.querySelector('.faq-answer');
                    otherItem.classList.remove('active');
                    otherAnswer.classList.add('hidden');
                }
            });
        };
        
        question.addEventListener('click', () => {
            const isActive = item.classList.contains('active');
            
            // Close other FAQs
            closeOtherFaqs(item);
            
            // Toggle current FAQ
            if (!isActive) {
                item.classList.add('active');
                answer.classList.remove('hidden');
                
                // Smooth scroll if needed
                const rect = item.getBoundingClientRect();
                const isFullyVisible = (
                    rect.top >= 0 &&
                    rect.bottom <= window.innerHeight
                );
                
                if (!isFullyVisible) {
                    const headerHeight = 80; // Height of fixed header
                    const offset = rect.top + window.pageYOffset - headerHeight - 20;
                    window.scrollTo({
                        top: offset,
                        behavior: 'smooth'
                    });
                }
            } else {
                item.classList.remove('active');
                answer.classList.add('hidden');
            }
        });
        
        // Keyboard accessibility
        question.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                question.click();
            }
        });
    });
    
    // Close FAQ when clicking outside
    document.addEventListener('click', (e) => {
        if (!e.target.closest('.faq-item')) {
            faqItems.forEach(item => {
                const answer = item.querySelector('.faq-answer');
                item.classList.remove('active');
                answer.classList.add('hidden');
            });
        }
    });
}); 