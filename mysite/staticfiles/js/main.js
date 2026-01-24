// ============================================
// ФАЙЛ: main.js
// ОПИСАНИЕ: Основной JavaScript файл с улучшениями UX
// ============================================

document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 DPITS-CMS загружен');
    
    // ========== RIPPLE EFFECT ДЛЯ КНОПОК ==========
    initRippleEffect();
    
    // ========== SMOOTH SCROLL ==========
    initSmoothScroll();
    
    // ========== LAZY LOADING IMAGES ==========
    initLazyLoading();
    
    // ========== INTERSECTION OBSERVER ДЛЯ АНИМАЦИЙ ==========
    initScrollAnimations();
    
    // ========== МОБИЛЬНОЕ МЕНЮ ==========
    initMobileMenu();
    
    // ========== SCROLL TO TOP ==========
    initScrollToTop();
    
    // ========== ФОРМА ОБРАТНОЙ СВЯЗИ ==========
    initFormValidation();
    
    // ========== TOAST УВЕДОМЛЕНИЯ ==========
    initToasts();
    
    // ========== HEADER SCROLL EFFECT ==========
    initHeaderScroll();
});

// ========== RIPPLE EFFECT ==========
function initRippleEffect() {
    const buttons = document.querySelectorAll('.btn, .nav-link, .card-link');
    
    buttons.forEach(button => {
        button.addEventListener('click', function(e) {
            // Создаем элемент ripple
            const ripple = document.createElement('span');
            ripple.classList.add('ripple-effect');
            this.appendChild(ripple);
            
            // Вычисляем позицию клика
            const rect = this.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            const x = e.clientX - rect.left - size / 2;
            const y = e.clientY - rect.top - size / 2;
            
            // Применяем стили
            ripple.style.width = ripple.style.height = size + 'px';
            ripple.style.left = x + 'px';
            ripple.style.top = y + 'px';
            
            // Удаляем после анимации
            setTimeout(() => ripple.remove(), 600);
        });
    });
}

// ========== SMOOTH SCROLL ==========
function initSmoothScroll() {
    // Плавная прокрутка для якорных ссылок
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            
            // Игнорируем пустые якоря и якоря для модальных окон
            if (href === '#' || href.startsWith('#modal')) return;
            
            e.preventDefault();
            const target = document.querySelector(href);
            
            if (target) {
                const headerOffset = 80; // Высота sticky header
                const elementPosition = target.getBoundingClientRect().top;
                const offsetPosition = elementPosition + window.pageYOffset - headerOffset;
                
                window.scrollTo({
                    top: offsetPosition,
                    behavior: 'smooth'
                });
            }
        });
    });
}

// ========== LAZY LOADING ==========
function initLazyLoading() {
    // Проверяем поддержку Intersection Observer
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    
                    // Загружаем изображение
                    if (img.dataset.src) {
                        img.src = img.dataset.src;
                        img.classList.add('loaded');
                        observer.unobserve(img);
                    }
                }
            });
        }, {
            rootMargin: '50px' // Начинаем загрузку за 50px до появления
        });
        
        // Наблюдаем за всеми изображениями с data-src
        document.querySelectorAll('img[data-src]').forEach(img => {
            imageObserver.observe(img);
        });
    } else {
        // Fallback для старых браузеров
        document.querySelectorAll('img[data-src]').forEach(img => {
            img.src = img.dataset.src;
            img.classList.add('loaded');
        });
    }
}

// ========== SCROLL ANIMATIONS ==========
function initScrollAnimations() {
    if ('IntersectionObserver' in window) {
        const animationObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('visible');
                }
            });
        }, {
            threshold: 0.1
        });
        
        // Наблюдаем за элементами с классом fade-in-on-scroll
        document.querySelectorAll('.fade-in-on-scroll').forEach(el => {
            animationObserver.observe(el);
        });
    }
}

// ========== МОБИЛЬНОЕ МЕНЮ ==========
function initMobileMenu() {
    const navbarToggler = document.querySelector('.navbar-toggler');
    const navbarCollapse = document.querySelector('.navbar-collapse');
    
    if (navbarToggler && navbarCollapse) {
        // Закрытие меню при клике вне его
        document.addEventListener('click', function(e) {
            if (navbarCollapse.classList.contains('show')) {
                if (!navbarCollapse.contains(e.target) && !navbarToggler.contains(e.target)) {
                    const bsCollapse = new bootstrap.Collapse(navbarCollapse, {
                        toggle: false
                    });
                    bsCollapse.hide();
                }
            }
        });
        
        // Закрытие меню при клике на ссылку
        navbarCollapse.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', function() {
                if (window.innerWidth < 992) {
                    const bsCollapse = new bootstrap.Collapse(navbarCollapse, {
                        toggle: false
                    });
                    bsCollapse.hide();
                }
            });
        });
    }
}

// ========== SCROLL TO TOP ==========
function initScrollToTop() {
    // Создаем кнопку "Наверх"
    const scrollBtn = document.createElement('button');
    scrollBtn.innerHTML = '<i class="fas fa-arrow-up"></i>';
    scrollBtn.className = 'scroll-to-top';
    scrollBtn.setAttribute('aria-label', 'Прокрутить наверх');
    document.body.appendChild(scrollBtn);
    
    // Показываем/скрываем кнопку при прокрутке
    window.addEventListener('scroll', function() {
        if (window.pageYOffset > 300) {
            scrollBtn.classList.add('visible');
        } else {
            scrollBtn.classList.remove('visible');
        }
    });
    
    // Прокрутка наверх при клике
    scrollBtn.addEventListener('click', function() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
}

// ========== ВАЛИДАЦИЯ ФОРМ ==========
function initFormValidation() {
    const forms = document.querySelectorAll('.needs-validation');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!form.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
            }
            
            form.classList.add('was-validated');
        }, false);
    });
    
    // Добавляем loading состояние для кнопок отправки
    const submitButtons = document.querySelectorAll('form button[type="submit"]');
    
    submitButtons.forEach(button => {
        button.closest('form').addEventListener('submit', function(e) {
            if (this.checkValidity()) {
                button.disabled = true;
                
                // Сохраняем оригинальный текст
                const originalText = button.innerHTML;
                
                // Показываем loader
                button.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Отправка...';
                
                // Восстанавливаем через 3 секунды (если форма не перезагрузила страницу)
                setTimeout(() => {
                    button.disabled = false;
                    button.innerHTML = originalText;
                }, 3000);
            }
        });
    });
}

// ========== TOAST УВЕДОМЛЕНИЯ ==========
function initToasts() {
    // Инициализируем все toast уведомления
    const toastElList = [].slice.call(document.querySelectorAll('.toast'));
    const toastList = toastElList.map(function(toastEl) {
        return new bootstrap.Toast(toastEl, {
            autohide: true,
            delay: 5000
        });
    });
    
    // Показываем toast при загрузке страницы
    toastList.forEach(toast => toast.show());
}

// ========== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ==========

// Функция для показа toast уведомления
function showToast(message, type = 'success') {
    const toastContainer = document.querySelector('.toast-container') || createToastContainer();
    
    const toastHTML = `
        <div class="toast" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="toast-header">
                <i class="fas fa-${getToastIcon(type)} text-${type} me-2"></i>
                <strong class="me-auto">${getToastTitle(type)}</strong>
                <small>только что</small>
                <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Закрыть"></button>
            </div>
            <div class="toast-body">
                ${message}
            </div>
        </div>
    `;
    
    toastContainer.insertAdjacentHTML('beforeend', toastHTML);
    
    const toastElement = toastContainer.lastElementChild;
    const toast = new bootstrap.Toast(toastElement);
    toast.show();
    
    // Удаляем toast после скрытия
    toastElement.addEventListener('hidden.bs.toast', function() {
        this.remove();
    });
}

function createToastContainer() {
    const container = document.createElement('div');
    container.className = 'toast-container position-fixed top-0 end-0 p-3';
    container.style.zIndex = '1100';
    document.body.appendChild(container);
    return container;
}

function getToastIcon(type) {
    const icons = {
        success: 'check-circle',
        error: 'exclamation-circle',
        warning: 'exclamation-triangle',
        info: 'info-circle'
    };
    return icons[type] || 'info-circle';
}

function getToastTitle(type) {
    const titles = {
        success: 'Успешно',
        error: 'Ошибка',
        warning: 'Внимание',
        info: 'Информация'
    };
    return titles[type] || 'Уведомление';
}

// ========== DEBOUNCE ФУНКЦИЯ ==========
function debounce(func, wait) {
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

// ========== THROTTLE ФУНКЦИЯ ==========
function throttle(func, limit) {
    let inThrottle;
    return function(...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// ========== HEADER SCROLL EFFECT ==========
function initHeaderScroll() {
    const header = document.querySelector('.glass-header');
    if (!header) return;
    
    const handleScroll = () => {
        if (window.scrollY > 50) {
            header.classList.add('scrolled');
        } else {
            header.classList.remove('scrolled');
        }
    };
    
    window.addEventListener('scroll', handleScroll);
    // Вызываем один раз при загрузке на случай если страница уже прокручена
    handleScroll();
}

// Экспортируем функции для использования в других скриптах
window.dpitsCMS = {
    showToast,
    debounce,
    throttle
};