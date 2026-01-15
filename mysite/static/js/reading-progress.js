// ============================================
// ФАЙЛ: reading-progress.js
// ОПИСАНИЕ: Индикатор прогресса чтения страницы
// ============================================

(function() {
    'use strict';
    
    let readingProgress = null;
    
    function init() {
        // Создаем элемент индикатора, если его нет
        readingProgress = document.getElementById('readingProgress');
        
        if (!readingProgress) {
            readingProgress = document.createElement('div');
            readingProgress.id = 'readingProgress';
            readingProgress.className = 'reading-progress';
            document.body.insertBefore(readingProgress, document.body.firstChild);
        }
        
        // Обновляем прогресс при прокрутке
        window.addEventListener('scroll', updateProgress, { passive: true });
        
        // Обновляем прогресс при загрузке
        updateProgress();
    }
    
    function updateProgress() {
        if (!readingProgress) return;
        
        const windowHeight = window.innerHeight;
        const documentHeight = document.documentElement.scrollHeight;
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        
        // Вычисляем процент прочитанного
        const scrollableHeight = documentHeight - windowHeight;
        const progress = scrollableHeight > 0 
            ? (scrollTop / scrollableHeight) * 100 
            : 0;
        
        // Обновляем ширину индикатора
        readingProgress.style.width = Math.min(100, Math.max(0, progress)) + '%';
    }
    
    // Инициализация при загрузке DOM
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
