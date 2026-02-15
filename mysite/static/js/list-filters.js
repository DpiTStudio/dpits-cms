/**
 * ФАЙЛ: list-filters.js
 * ОПИСАНИЕ: Общая логика фильтрации и поиска для списков (Портфолио, Новости, Услуги)
 * ФУНКЦИОНАЛ: 
 * - Автоматическое обновление при выборе категории или сортировки
 * - Поиск с задержкой (800мс) для предотвращения лишних запросов
 * - Сохранение всех фильтров в URL параметрах
 */

function initListFilters(formId) {
    const filterForm = document.getElementById(formId);
    if (!filterForm) return;

    const searchInput = filterForm.querySelector('input[name="q"]');
    const categoryFilter = filterForm.querySelector('select[name="category"]');
    const sortBy = filterForm.querySelector('select[name="sort"]');

    const updateFilters = () => {
        const formData = new FormData(filterForm);
        const params = new URLSearchParams();
        
        // Собираем все непустые значения
        for (const [key, value] of formData.entries()) {
            if (value) params.append(key, value);
        }
        
        // Сбрасываем пагинацию при поиске/фильтрации
        params.delete('page');
        
        // Обновляем страницу с новыми параметрами
        window.location.href = `?${params.toString()}`;
    };

    // Мгновенное обновление при выборе из списка
    if (categoryFilter) categoryFilter.addEventListener('change', updateFilters);
    if (sortBy) sortBy.addEventListener('change', updateFilters);

    // Поиск с дебаунсом (задержкой)
    if (searchInput) {
        let timeout = null;
        searchInput.addEventListener('input', () => {
            clearTimeout(timeout);
            timeout = setTimeout(updateFilters, 800);
        });
    }
    
    // Обработка отправки формы через Enter
    filterForm.addEventListener('submit', (e) => {
        e.preventDefault();
        updateFilters();
    });
}

// Запуск при полной загрузке DOM
document.addEventListener('DOMContentLoaded', function() {
    initListFilters('portfolio-filters');
    initListFilters('news-filters');
    initListFilters('services-filters');
});
