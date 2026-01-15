// ============================================
// ФАЙЛ: search.js
// ОПИСАНИЕ: Поиск по сайту с автодополнением
// ============================================

(function() {
    'use strict';
    
    let searchTimeout = null;
    let currentSearchQuery = '';
    
    // Конфигурация поиска
    const config = {
        minLength: 2,
        debounceDelay: 300,
        maxResults: 10
    };
    
    // Иконки для разных типов контента
    const contentIcons = {
        news: 'fa-newspaper',
        portfolio: 'fa-briefcase',
        review: 'fa-star',
        page: 'fa-file-alt',
        category: 'fa-folder'
    };
    
    // Инициализация поиска
    function init() {
        const searchInput = document.querySelector('.search-input');
        const searchButton = document.querySelector('.search-button');
        const searchContainer = document.querySelector('.search-container');
        
        if (!searchInput || !searchContainer) return;
        
        // Создаем контейнер для результатов
        let resultsContainer = searchContainer.querySelector('.search-results');
        if (!resultsContainer) {
            resultsContainer = document.createElement('div');
            resultsContainer.className = 'search-results';
            searchContainer.appendChild(resultsContainer);
        }
        
        // Обработчик ввода
        searchInput.addEventListener('input', function(e) {
            const query = e.target.value.trim();
            
            if (query.length < config.minLength) {
                hideResults();
                return;
            }
            
            // Debounce для оптимизации запросов
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                performSearch(query);
            }, config.debounceDelay);
        });
        
        // Обработчик фокуса
        searchInput.addEventListener('focus', function() {
            if (currentSearchQuery && currentSearchQuery.length >= config.minLength) {
                showResults();
            }
        });
        
        // Обработчик клика на кнопку поиска
        if (searchButton) {
            searchButton.addEventListener('click', function(e) {
                e.preventDefault();
                const query = searchInput.value.trim();
                if (query.length >= config.minLength) {
                    window.location.href = `/search/?q=${encodeURIComponent(query)}`;
                }
            });
        }
        
        // Обработчик Enter
        searchInput.addEventListener('keydown', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                const query = e.target.value.trim();
                if (query.length >= config.minLength) {
                    window.location.href = `/search/?q=${encodeURIComponent(query)}`;
                }
            }
        });
        
        // Закрытие результатов при клике вне области поиска
        document.addEventListener('click', function(e) {
            if (!searchContainer.contains(e.target)) {
                hideResults();
            }
        });
    }
    
    // Выполнение поиска
    async function performSearch(query) {
        currentSearchQuery = query;
        const resultsContainer = document.querySelector('.search-results');
        
        if (!resultsContainer) return;
        
        // Показываем индикатор загрузки
        showLoading();
        
        try {
            // Здесь должен быть реальный API запрос
            // Для примера используем простой поиск по DOM
            const results = searchInDOM(query);
            
            if (results.length === 0) {
                showNoResults();
            } else {
                showResults(results);
            }
        } catch (error) {
            console.error('Ошибка поиска:', error);
            showError();
        }
    }
    
    // Поиск в DOM (заглушка для реального API)
    function searchInDOM(query) {
        const results = [];
        const lowerQuery = query.toLowerCase();
        
        // Поиск по заголовкам новостей
        document.querySelectorAll('.news-card .card-title, .news-title').forEach(el => {
            const text = el.textContent.toLowerCase();
            if (text.includes(lowerQuery)) {
                const link = el.closest('a') || el.querySelector('a');
                if (link) {
                    results.push({
                        title: el.textContent.trim(),
                        url: link.href,
                        type: 'news',
                        icon: contentIcons.news
                    });
                }
            }
        });
        
        // Поиск по портфолио
        document.querySelectorAll('.portfolio-card .card-title, .portfolio-title').forEach(el => {
            const text = el.textContent.toLowerCase();
            if (text.includes(lowerQuery)) {
                const link = el.closest('a') || el.querySelector('a');
                if (link) {
                    results.push({
                        title: el.textContent.trim(),
                        url: link.href,
                        type: 'portfolio',
                        icon: contentIcons.portfolio
                    });
                }
            }
        });
        
        return results.slice(0, config.maxResults);
    }
    
    // Показать результаты
    function showResults(results = []) {
        const resultsContainer = document.querySelector('.search-results');
        if (!resultsContainer) return;
        
        resultsContainer.innerHTML = '';
        
        results.forEach(result => {
            const item = document.createElement('div');
            item.className = 'search-result-item';
            item.innerHTML = `
                <i class="fas ${result.icon} search-result-icon"></i>
                <div class="search-result-content">
                    <div class="search-result-title">${escapeHtml(result.title)}</div>
                    <span class="search-result-category">${result.type}</span>
                </div>
            `;
            
            item.addEventListener('click', function() {
                window.location.href = result.url;
            });
            
            resultsContainer.appendChild(item);
        });
        
        resultsContainer.classList.add('active');
    }
    
    // Показать индикатор загрузки
    function showLoading() {
        const resultsContainer = document.querySelector('.search-results');
        if (!resultsContainer) return;
        
        resultsContainer.innerHTML = `
            <div class="search-loading">
                <div class="spinner"></div>
                <div style="margin-top: 10px;">Поиск...</div>
            </div>
        `;
        resultsContainer.classList.add('active');
    }
    
    // Показать сообщение "ничего не найдено"
    function showNoResults() {
        const resultsContainer = document.querySelector('.search-results');
        if (!resultsContainer) return;
        
        resultsContainer.innerHTML = `
            <div class="search-no-results">
                <i class="fas fa-search"></i>
                <div>Ничего не найдено</div>
            </div>
        `;
        resultsContainer.classList.add('active');
    }
    
    // Показать ошибку
    function showError() {
        const resultsContainer = document.querySelector('.search-results');
        if (!resultsContainer) return;
        
        resultsContainer.innerHTML = `
            <div class="search-no-results">
                <i class="fas fa-exclamation-triangle"></i>
                <div>Ошибка при выполнении поиска</div>
            </div>
        `;
        resultsContainer.classList.add('active');
    }
    
    // Скрыть результаты
    function hideResults() {
        const resultsContainer = document.querySelector('.search-results');
        if (resultsContainer) {
            resultsContainer.classList.remove('active');
        }
    }
    
    // Экранирование HTML
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    // Инициализация при загрузке DOM
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
    
    // Экспортируем функции
    window.siteSearch = {
        performSearch,
        showResults,
        hideResults
    };
})();
