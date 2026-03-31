// ============================================
// ФАЙЛ: theme-toggle.js
// ОПИСАНИЕ: Переключение темной/светлой темы
// ============================================

(function() {
    'use strict';
    
    const themeToggles = document.querySelectorAll('.theme-toggle');
    const html = document.documentElement;
    
    // Получаем сохраненную тему из localStorage или используем системную
    function getTheme() {
        const savedTheme = localStorage.getItem('theme');
        if (savedTheme) {
            return savedTheme;
        }
        
        // Проверяем системные настройки
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            return 'dark';
        }
        
        return 'light';
    }
    
    // Применяем тему
    function setTheme(theme) {
        html.setAttribute('data-theme', theme);
        localStorage.setItem('theme', theme);
        
        // Обновляем иконки переключателей
        themeToggles.forEach(toggle => {
            const sunIcon = toggle.querySelector('.fa-sun');
            const moonIcon = toggle.querySelector('.fa-moon');
            
            if (theme === 'dark') {
                if (sunIcon) sunIcon.style.opacity = '0';
                if (moonIcon) moonIcon.style.opacity = '1';
            } else {
                if (sunIcon) sunIcon.style.opacity = '1';
                if (moonIcon) moonIcon.style.opacity = '0';
            }
        });
    }
    
    // Переключаем тему
    function toggleTheme() {
        const currentTheme = html.getAttribute('data-theme') || 'light';
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        setTheme(newTheme);
        
        // Показываем уведомление
        if (window.dpitsCMS && window.dpitsCMS.showToast) {
            window.dpitsCMS.showToast(
                `Тема изменена на ${newTheme === 'dark' ? 'темную' : 'светлую'}`,
                'success'
            );
        }
    }
    
    // Инициализация
    function init() {
        // Применяем сохраненную тему при загрузке
        const theme = getTheme();
        setTheme(theme);
        
        // Слушаем изменения системной темы
        if (window.matchMedia) {
            const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
            mediaQuery.addEventListener('change', (e) => {
                // Применяем системную тему только если пользователь не выбрал тему вручную
                if (!localStorage.getItem('theme')) {
                    setTheme(e.matches ? 'dark' : 'light');
                }
            });
        }
        
        // Обработчик клика на переключатели
        themeToggles.forEach(toggle => {
            toggle.addEventListener('click', toggleTheme);
        });
    }
    
    // Запускаем при загрузке DOM
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
    
    // Экспортируем функции для использования в других скриптах
    window.themeToggle = {
        setTheme,
        toggleTheme,
        getTheme
    };
})();
