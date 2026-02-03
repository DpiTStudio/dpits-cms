// ============================================
// ФАЙЛ: force-light-theme.js
// ОПИСАНИЕ: Принудительная установка светлой темы
// ============================================

(function() {
    'use strict';
    
    // Удаляем сохраненную тему из localStorage
    localStorage.removeItem('theme');
    
    // Удаляем атрибут data-theme, если он был установлен
    const html = document.documentElement;
    if (html.hasAttribute('data-theme')) {
        html.removeAttribute('data-theme');
    }
})();
