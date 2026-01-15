// ============================================
// ФАЙЛ: lazy-loading.js
// ОПИСАНИЕ: Ленивая загрузка изображений для улучшения производительности
// ============================================

(function() {
    'use strict';
    
    // Конфигурация
    const config = {
        rootMargin: '50px',
        threshold: 0.01,
        placeholder: 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="400" height="300"%3E%3Crect fill="%23e5e5e5" width="400" height="300"/%3E%3C/svg%3E'
    };
    
    // Проверка поддержки Intersection Observer
    if (!('IntersectionObserver' in window)) {
        // Fallback для старых браузеров
        loadAllImages();
        return;
    }
    
    // Создаем observer
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                loadImage(entry.target);
                observer.unobserve(entry.target);
            }
        });
    }, {
        rootMargin: config.rootMargin,
        threshold: config.threshold
    });
    
    // Загрузка изображения
    function loadImage(img) {
        // Проверяем наличие data-src
        if (!img.dataset.src) {
            return;
        }
        
        // Создаем новое изображение для предзагрузки
        const imageLoader = new Image();
        
        // Обработчик успешной загрузки
        imageLoader.onload = function() {
            img.src = this.src;
            img.classList.add('loaded');
            img.classList.remove('loading');
            
            // Анимация появления
            img.style.opacity = '0';
            img.style.transition = 'opacity 0.3s ease';
            setTimeout(() => {
                img.style.opacity = '1';
            }, 10);
        };
        
        // Обработчик ошибки
        imageLoader.onerror = function() {
            img.classList.add('error');
            img.classList.remove('loading');
            img.alt = 'Ошибка загрузки изображения';
        };
        
        // Начинаем загрузку
        img.classList.add('loading');
        imageLoader.src = img.dataset.src;
        
        // Удаляем data-src после загрузки
        delete img.dataset.src;
    }
    
    // Инициализация
    function init() {
        // Находим все изображения с data-src
        const lazyImages = document.querySelectorAll('img[data-src]');
        
        // Устанавливаем placeholder для всех изображений
        lazyImages.forEach(img => {
            if (!img.src || img.src === window.location.href) {
                img.src = config.placeholder;
            }
            img.classList.add('lazy-image');
            
            // Наблюдаем за изображением
            imageObserver.observe(img);
        });
        
        // Также обрабатываем изображения с классом lazy
        const lazyClassImages = document.querySelectorAll('img.lazy:not([data-src])');
        lazyClassImages.forEach(img => {
            if (img.src) {
                img.dataset.src = img.src;
                img.src = config.placeholder;
                imageObserver.observe(img);
            }
        });
    }
    
    // Fallback: загрузить все изображения сразу
    function loadAllImages() {
        const lazyImages = document.querySelectorAll('img[data-src]');
        lazyImages.forEach(img => {
            if (img.dataset.src) {
                img.src = img.dataset.src;
                img.classList.add('loaded');
            }
        });
    }
    
    // CSS для состояний загрузки
    function addStyles() {
        const style = document.createElement('style');
        style.textContent = `
            .lazy-image {
                opacity: 0.7;
                transition: opacity 0.3s ease;
            }
            
            .lazy-image.loading {
                filter: blur(5px);
                opacity: 0.5;
            }
            
            .lazy-image.loaded {
                opacity: 1;
                filter: blur(0);
            }
            
            .lazy-image.error {
                opacity: 0.3;
                filter: grayscale(100%);
            }
            
            .lazy-image.error::after {
                content: '⚠';
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                font-size: 2rem;
                color: var(--danger-color);
            }
        `;
        document.head.appendChild(style);
    }
    
    // Инициализация при загрузке DOM
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            addStyles();
            init();
        });
    } else {
        addStyles();
        init();
    }
    
    // Экспортируем функции
    window.lazyLoading = {
        loadImage,
        init,
        imageObserver
    };
})();
