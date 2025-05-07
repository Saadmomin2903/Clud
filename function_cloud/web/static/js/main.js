// Initialize syntax highlighting
document.addEventListener('DOMContentLoaded', function() {
    // Highlight all code blocks
    document.querySelectorAll('pre code').forEach((block) => {
        hljs.highlightBlock(block);
    });

    // Copy code functionality
    document.querySelectorAll('pre').forEach((block) => {
        const button = document.createElement('button');
        button.className = 'copy-button btn btn-sm btn-light position-absolute end-0 m-2';
        button.innerHTML = '<i class="fas fa-copy"></i>';
        
        // Position the pre relatively for absolute button positioning
        block.style.position = 'relative';
        block.appendChild(button);

        button.addEventListener('click', async () => {
            const code = block.querySelector('code').innerText;
            await navigator.clipboard.writeText(code);
            
            button.innerHTML = '<i class="fas fa-check"></i>';
            setTimeout(() => {
                button.innerHTML = '<i class="fas fa-copy"></i>';
            }, 2000);
        });
    });

    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            document.querySelector(this.getAttribute('href')).scrollIntoView({
                behavior: 'smooth'
            });
        });
    });

    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Add copy button hover effect
    const style = document.createElement('style');
    style.textContent = `
        .copy-button {
            opacity: 0;
            transition: opacity 0.2s;
        }
        pre:hover .copy-button {
            opacity: 1;
        }
    `;
    document.head.appendChild(style);

    // Add animation for feature cards
    const cards = document.querySelectorAll('.feature-card');
    const observerOptions = {
        threshold: 0.1
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);

    cards.forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = 'opacity 0.5s, transform 0.5s';
        observer.observe(card);
    });
});