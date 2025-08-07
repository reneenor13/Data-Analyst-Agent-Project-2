// Main JavaScript for Data Analyst Agent
class DataAnalystAgent {
    constructor() {
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.setupAnimations();
        this.setupFormHandling();
        this.checkApiHealth();
    }

    setupEventListeners() {
        // Smooth scrolling for anchor links
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', (e) => {
                e.preventDefault();
                const target = document.querySelector(anchor.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });

        // Copy code blocks
        document.querySelectorAll('.code-block').forEach(block => {
            const copyBtn = document.createElement('button');
            copyBtn.innerHTML = '<i class="fas fa-copy"></i>';
            copyBtn.className = 'absolute top-2 right-2 p-2 bg-white/20 hover:bg-white/30 rounded transition-all';
            copyBtn.onclick = () => this.copyToClipboard(block.textContent);
            block.style.position = 'relative';
            block.appendChild(copyBtn);
        });

        // Feature card interactions
        document.querySelectorAll('.feature-card').forEach(card => {
            card.addEventListener('mouseenter', () => {
                card.style.transform = 'translateY(-10px) scale(1.02)';
            });
            
            card.addEventListener('mouseleave', () => {
                card.style.transform = 'translateY(0) scale(1)';
            });
        });
    }

    setupAnimations() {
        // Intersection Observer for scroll animations
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-slideInUp');
                }
            });
        }, observerOptions);

        // Observe elements for animation
        document.querySelectorAll('.feature-card, .glassmorphism').forEach(el => {
            observer.observe(el);
        });

        // Typing effect for hero title
        this.typeWriter();
    }

    typeWriter() {
        const titleElement = document.querySelector('.hero-title');
        if (!titleElement) return;

        const text = 'AI-Powered Data Analysis';
        const originalText = titleElement.textContent;
        titleElement.textContent = '';
        
        let i = 0;
        const speed = 100;
        
        function type() {
            if (i < text.length) {
                titleElement.textContent += text.charAt(i);
                i++;
                setTimeout(type, speed);
            }
        }
        
        // Start typing after a delay
        setTimeout(type, 1000);
    }

    setupFormHandling() {
        // Demo form submission
        const demoForm = document.getElementById('demo-form');
        if (demoForm) {
            demoForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.runDemo();
            });
        }

        // File upload handling
        document.querySelectorAll('input[type="file"]').forEach(input => {
            input.addEventListener('change', (e) => {
                this.handleFileUpload(e);
            });
        });
    }

    async runDemo() {
        const demoResult = document.getElementById('demo-result');
        const demoOutput = document.getElementById('demo-output');
        
        if (!demoResult || !demoOutput) return;

        // Show loading state
        demoResult.classList.remove('hidden');
        demoOutput.innerHTML = '<div class="loading-spinner mx-auto"></div>';

        try {
            // Simulate API call
            await this.sleep(2000);
            
            const mockResult = [
                1,
                "Titanic",
                0.485782,
                "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
            ];

            demoOutput.innerHTML = `<pre class="text-green-400">${JSON.stringify(mockResult, null, 2)}</pre>`;
            demoResult.className = 'mt-6 p-4 bg-green-900/30 rounded-lg success-state';
        } catch (error) {
            demoOutput.innerHTML = `<pre class="text-red-400">Error: ${error.message}</pre>`;
            demoResult.className = 'mt-6 p-4 bg-red-900/30 rounded-lg error-state';
        }
    }

    async checkApiHealth() {
        try {
            const response = await fetch('/health');
            const data = await response.json();
            
            const statusIndicator = document.getElementById('api-status');
            if (statusIndicator) {
                if (data.status === 'healthy') {
                    statusIndicator.className = 'w-3 h-3 bg-green-400 rounded-full animate-pulse';
                    statusIndicator.title = 'API is healthy';
                } else {
                    statusIndicator.className = 'w-3 h-3 bg-red-400 rounded-full animate-pulse';
                    statusIndicator.title = 'API is unhealthy';
                }
            }
        } catch (error) {
            console.warn('Could not check API health:', error);
        }
    }

    handleFileUpload(event) {
        const file = event.target.files[0];
        if (!file) return;

        const fileInfo = document.createElement('div');
        fileInfo.className = 'mt-2 p-2 bg-blue-900/30 rounded text-sm';
        fileInfo.innerHTML = `
            <i class="fas fa-file mr-2"></i>
            ${file.name} (${this.formatFileSize(file.size)})
        `;
        
        event.target.parentNode.appendChild(fileInfo);
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    async copyToClipboard(text) {
        try {
            await navigator.clipboard.writeText(text);
            this.showToast('Copied to clipboard!', 'success');
        } catch (error) {
            console.error('Failed to copy:', error);
            this.showToast('Failed to copy', 'error');
        }
    }

    showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `fixed top-4 right-4 p-4 rounded-lg text-white z-50 animate-slideInUp ${
            type === 'success' ? 'bg-green-600' : 
            type === 'error' ? 'bg-red-600' : 'bg-blue-600'
        }`;
        toast.textContent = message;
        
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateX(100%)';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }

    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new DataAnalystAgent();
});

// Add some interactive particles for visual enhancement
class ParticleSystem {
    constructor() {
        this.particles = [];
        this.canvas = this.createCanvas();
        this.ctx = this.canvas.getContext('2d');
        this.init();
    }

    createCanvas() {
        const canvas = document.createElement('canvas');
        canvas.style.position = 'fixed';
        canvas.style.top = '0';
        canvas.style.left = '0';
        canvas.style.width = '100%';
        canvas.style.height = '100%';
        canvas.style.pointerEvents = 'none';
        canvas.style.zIndex = '-1';
        document.body.appendChild(canvas);
        return canvas;
    }

    init() {
        this.resize();
        this.createParticles();
        this.animate();
        
        window.addEventListener('resize', () => this.resize());
    }

    resize() {
        this.canvas.width = window.innerWidth;
        this.canvas.height = window.innerHeight;
    }

    createParticles() {
        const particleCount = Math.min(50, window.innerWidth / 20);
        
        for (let i = 0; i < particleCount; i++) {
            this.particles.push({
                x: Math.random() * this.canvas.width,
                y: Math.random() * this.canvas.height,
                vx: (Math.random() - 0.5) * 0.5,
                vy: (Math.random() - 0.5) * 0.5,
                size: Math.random() * 2 + 1,
                opacity: Math.random() * 0.5 + 0.2
            });
        }
    }

    animate() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        this.particles.forEach(particle => {
            particle.x += particle.vx;
            particle.y += particle.vy;
            
            if (particle.x < 0 || particle.x > this.canvas.width) particle.vx *= -1;
            if (particle.y < 0 || particle.y > this.canvas.height) particle.vy *= -1;
            
            this.ctx.beginPath();
            this.ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2);
            this.ctx.fillStyle = `rgba(102, 126, 234, ${particle.opacity})`;
            this.ctx.fill();
        });
        
        requestAnimationFrame(() => this.animate());
    }
}

// Initialize particle system on load
window.addEventListener('load', () => {
    if (window.innerWidth > 768) { // Only on desktop
        new ParticleSystem();
    }
});
