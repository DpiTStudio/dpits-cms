// ============================================
// ФАЙЛ: mobile-enhancements.js
// ОПИСАНИЕ: Улучшения для мобильных устройств (swipe жесты, улучшенное меню)
// ============================================

(function() {
    'use strict';
    
    // Определяем мобильное устройство
    const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
    const isTouch = 'ontouchstart' in window || navigator.maxTouchPoints > 0;
    
    if (!isMobile && !isTouch) {
        return; // Не мобильное устройство
    }
    
    // ========== SWIPE ЖЕСТЫ ==========
    
    let touchStartX = 0;
    let touchStartY = 0;
    let touchEndX = 0;
    let touchEndY = 0;
    
    const swipeThreshold = 50; // Минимальное расстояние для распознавания свайпа
    
    function handleTouchStart(e) {
        touchStartX = e.changedTouches[0].screenX;
        touchStartY = e.changedTouches[0].screenY;
    }
    
    function handleTouchEnd(e) {
        touchEndX = e.changedTouches[0].screenX;
        touchEndY = e.changedTouches[0].screenY;
        
        handleSwipe();
    }
    
    function handleSwipe() {
        const deltaX = touchEndX - touchStartX;
        const deltaY = touchEndY - touchStartY;
        
        // Проверяем, что движение достаточно большое
        if (Math.abs(deltaX) < swipeThreshold && Math.abs(deltaY) < swipeThreshold) {
            return;
        }
        
        // Определяем направление свайпа
        if (Math.abs(deltaX) > Math.abs(deltaY)) {
            // Горизонтальный свайп
            if (deltaX > 0) {
                onSwipeRight();
            } else {
                onSwipeLeft();
            }
        } else {
            // Вертикальный свайп
            if (deltaY > 0) {
                onSwipeDown();
            } else {
                onSwipeUp();
            }
        }
    }
    
    function onSwipeLeft() {
        // Закрываем мобильное меню при свайпе влево
        const navbarCollapse = document.querySelector('.navbar-collapse.show');
        if (navbarCollapse) {
            const bsCollapse = new bootstrap.Collapse(navbarCollapse, {
                toggle: false
            });
            bsCollapse.hide();
        }
    }
    
    function onSwipeRight() {
        // Открываем мобильное меню при свайпе вправо (если закрыто)
        const navbarToggler = document.querySelector('.navbar-toggler');
        const navbarCollapse = document.querySelector('.navbar-collapse');
        
        if (navbarToggler && navbarCollapse && !navbarCollapse.classList.contains('show')) {
            navbarToggler.click();
        }
    }
    
    function onSwipeUp() {
        // Прокрутка вверх (можно использовать для скрытия навигации)
        // window.scrollBy({ top: -100, behavior: 'smooth' });
    }
    
    function onSwipeDown() {
        // Прокрутка вниз (можно использовать для показа навигации)
        // window.scrollBy({ top: 100, behavior: 'smooth' });
    }
    
    // Добавляем обработчики свайпов
    if (isTouch) {
        document.addEventListener('touchstart', handleTouchStart, { passive: true });
        document.addEventListener('touchend', handleTouchEnd, { passive: true });
    }
    
    // ========== УЛУЧШЕННОЕ МОБИЛЬНОЕ МЕНЮ ==========
    
    function enhanceMobileMenu() {
        const navbarToggler = document.querySelector('.navbar-toggler');
        const navbarCollapse = document.querySelector('.navbar-collapse');
        
        if (!navbarToggler || !navbarCollapse) return;
        
        // Анимация иконки гамбургера
        navbarToggler.addEventListener('click', function() {
            setTimeout(() => {
                if (navbarCollapse.classList.contains('show')) {
                    navbarToggler.classList.add('active');
                } else {
                    navbarToggler.classList.remove('active');
                }
            }, 100);
        });
        
        // Закрытие меню при клике на ссылку
        const navLinks = navbarCollapse.querySelectorAll('.nav-link');
        navLinks.forEach(link => {
            link.addEventListener('click', function() {
                setTimeout(() => {
                    const bsCollapse = new bootstrap.Collapse(navbarCollapse, {
                        toggle: false
                    });
                    bsCollapse.hide();
                    navbarToggler.classList.remove('active');
                }, 300);
            });
        });
        
        // Закрытие меню при клике вне его
        document.addEventListener('click', function(e) {
            if (navbarCollapse.classList.contains('show')) {
                if (!navbarCollapse.contains(e.target) && !navbarToggler.contains(e.target)) {
                    const bsCollapse = new bootstrap.Collapse(navbarCollapse, {
                        toggle: false
                    });
                    bsCollapse.hide();
                    navbarToggler.classList.remove('active');
                }
            }
        });
    }
    
    // ========== ОПТИМИЗАЦИЯ ПРОИЗВОДИТЕЛЬНОСТИ ==========
    
    // Отключаем hover эффекты на мобильных устройствах
    function disableHoverOnTouch() {
        if (isTouch) {
            document.body.classList.add('touch-device');
        }
    }
    
    // ========== УЛУЧШЕНИЕ ФОРМ НА МОБИЛЬНЫХ ==========
    
    function enhanceMobileForms() {
        // Автоматическое изменение типа input для email/телефона
        const emailInputs = document.querySelectorAll('input[type="email"]');
        emailInputs.forEach(input => {
            input.setAttribute('inputmode', 'email');
            input.setAttribute('autocapitalize', 'none');
        });
        
        const telInputs = document.querySelectorAll('input[type="tel"]');
        telInputs.forEach(input => {
            input.setAttribute('inputmode', 'tel');
        });
        
        // Предотвращение масштабирования при фокусе на input
        const inputs = document.querySelectorAll('input, textarea, select');
        inputs.forEach(input => {
            if (input.style.fontSize === '') {
                // Устанавливаем минимальный размер шрифта для предотвращения зума
                const computedStyle = window.getComputedStyle(input);
                const fontSize = parseFloat(computedStyle.fontSize);
                if (fontSize < 16) {
                    input.style.fontSize = '16px';
                }
            }
        });
    }
    
    // ========== ПРЕДОТВРАЩЕНИЕ ДВОЙНОГО ТАПА ==========
    
    function preventDoubleTapZoom() {
        let lastTouchEnd = 0;
        document.addEventListener('touchend', function(e) {
            const now = Date.now();
            if (now - lastTouchEnd <= 300) {
                e.preventDefault();
            }
            lastTouchEnd = now;
        }, false);
    }
    
    // ========== ИНИЦИАЛИЗАЦИЯ ==========
    
    function init() {
        enhanceMobileMenu();
        disableHoverOnTouch();
        enhanceMobileForms();
        // preventDoubleTapZoom(); // Раскомментируйте, если нужно отключить двойной тап для зума
    }
    
    // Запускаем при загрузке DOM
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
    
    // Экспортируем функции
    window.mobileEnhancements = {
        isMobile,
        isTouch,
        onSwipeLeft,
        onSwipeRight
    };
})();
