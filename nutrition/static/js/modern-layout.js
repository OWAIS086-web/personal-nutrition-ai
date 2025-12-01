// Modern Layout JavaScript - Interactive Features

// Mobile Menu Toggle
function toggleMobileMenu() {
    const navMenu = document.getElementById('nav-menu');
    const toggle = document.querySelector('.mobile-menu-toggle');
    
    navMenu.classList.toggle('active');
    toggle.setAttribute('aria-expanded', navMenu.classList.contains('active'));
    
    // Animate hamburger
    const lines = toggle.querySelectorAll('.hamburger-line');
    if (navMenu.classList.contains('active')) {
        lines[0].style.transform = 'rotate(45deg) translateY(10px)';
        lines[1].style.opacity = '0';
        lines[2].style.transform = 'rotate(-45deg) translateY(-10px)';
    } else {
        lines[0].style.transform = '';
        lines[1].style.opacity = '';
        lines[2].style.transform = '';
    }
}

// Profile Dropdown Toggle
function toggleProfileMenu() {
    const dropdown = document.querySelector('.nav-dropdown');
    dropdown.classList.toggle('active');
    
    const button = dropdown.querySelector('.nav-profile');
    button.setAttribute('aria-expanded', dropdown.classList.contains('active'));
}

// Close dropdown when clicking outside
document.addEventListener('click', function(e) {
    const dropdown = document.querySelector('.nav-dropdown');
    if (dropdown && !dropdown.contains(e.target)) {
        dropdown.classList.remove('active');
        const button = dropdown.querySelector('.nav-profile');
        if (button) {
            button.setAttribute('aria-expanded', 'false');
        }
    }
});

// Dismiss Flash Message
function dismissFlash(button) {
    const flash = button.closest('.flash');
    flash.style.animation = 'slideOutRight 0.4s ease-out';
    setTimeout(() => flash.remove(), 400);
}

// Auto-dismiss flash messages after 5 seconds
document.addEventListener('DOMContentLoaded', function() {
    const flashes = document.querySelectorAll('.flash');
    flashes.forEach(flash => {
        setTimeout(() => {
            if (flash.parentElement) {
                flash.style.animation = 'slideOutRight 0.4s ease-out';
                setTimeout(() => flash.remove(), 400);
            }
        }, 5000);
    });
});

// Keyboard Shortcuts
function showKeyboardShortcuts() {
    const modal = document.getElementById('shortcuts-modal');
    if (modal) {
        modal.classList.remove('hidden');
        modal.setAttribute('aria-hidden', 'false');
        document.body.style.overflow = 'hidden';
    }
}

function closeShortcutsModal() {
    const modal = document.getElementById('shortcuts-modal');
    if (modal) {
        modal.classList.add('hidden');
        modal.setAttribute('aria-hidden', 'true');
        document.body.style.overflow = '';
    }
}

// Keyboard shortcuts handler
document.addEventListener('keydown', function(e) {
    // Don't trigger if user is typing in an input
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
        return;
    }
    
    switch(e.key.toLowerCase()) {
        case 'd':
            window.location.href = '/dashboard';
            break;
        case 'a':
            window.location.href = '/meals/upload';
            break;
        case 'w':
            window.location.href = '/wearables';
            break;
        case 't':
            toggleTheme();
            break;
        case '?':
            showKeyboardShortcuts();
            break;
        case 'escape':
            closeShortcutsModal();
            break;
    }
});

// PWA Install Prompt
let deferredPrompt;

window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault();
    deferredPrompt = e;
    
    // Show custom install prompt after 3 seconds
    setTimeout(() => {
        const prompt = document.getElementById('pwa-install-prompt');
        if (prompt && !localStorage.getItem('pwa-dismissed')) {
            prompt.classList.remove('hidden');
        }
    }, 3000);
});

function installPWA() {
    const prompt = document.getElementById('pwa-install-prompt');
    prompt.classList.add('hidden');
    
    if (deferredPrompt) {
        deferredPrompt.prompt();
        deferredPrompt.userChoice.then((choiceResult) => {
            if (choiceResult.outcome === 'accepted') {
                console.log('PWA installed');
            }
            deferredPrompt = null;
        });
    }
}

function dismissPWA() {
    const prompt = document.getElementById('pwa-install-prompt');
    prompt.classList.add('hidden');
    localStorage.setItem('pwa-dismissed', 'true');
}

// Active Navigation Link
document.addEventListener('DOMContentLoaded', function() {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
        const href = link.getAttribute('href');
        if (currentPath.includes(href) && href !== '/') {
            link.classList.add('active');
        }
    });
});

// Smooth Scroll for Skip Link
document.querySelector('.skip-link')?.addEventListener('click', function(e) {
    e.preventDefault();
    const target = document.querySelector(this.getAttribute('href'));
    if (target) {
        target.focus();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
});

// Announce to screen readers
function announce(message) {
    const announcer = document.getElementById('announcements');
    if (announcer) {
        announcer.textContent = message;
        setTimeout(() => {
            announcer.textContent = '';
        }, 1000);
    }
}

// Navbar scroll effect
let lastScroll = 0;
window.addEventListener('scroll', function() {
    const navbar = document.querySelector('.navbar');
    const currentScroll = window.pageYOffset;
    
    if (currentScroll > lastScroll && currentScroll > 100) {
        navbar.style.transform = 'translateY(-100%)';
    } else {
        navbar.style.transform = 'translateY(0)';
    }
    
    lastScroll = currentScroll;
});

console.log('🥗 Modern Layout Loaded');
console.log('💡 Press ? to see keyboard shortcuts');