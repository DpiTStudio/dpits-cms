/**
 * ============================================
 * ФАЙЛ: header_menu_dropdown.js
 * ОПИСАНИЕ: Скрипт для управления выпадающим меню в шапке сайта
 * ============================================
 */

// Функция для показа подменю при наведении мыши
function showMainDropdown() {
    // Получаем элемент выпадающего меню по его ID
    const dropdownMenu = document.getElementById('mainDropdownMenu');
    // Проверяем, существует ли элемент на странице
    if (dropdownMenu) {
        // Добавляем класс 'show', который делает меню видимым (CSS display: block)
        dropdownMenu.classList.add('show');
    }
}

// Функция для скрытия подменю при уходе мыши
function hideMainDropdown() {
    // Получаем элемент выпадающего меню по его ID
    const dropdownMenu = document.getElementById('mainDropdownMenu');
    // Проверяем, существует ли элемент
    if (dropdownMenu) {
        // Устанавливаем задержку перед скрытием, чтобы пользователь успел перевести курсор на меню
        setTimeout(() => {
            // Проверяем, не находится ли курсор все еще над меню (псевдокласс :hover)
            if (!dropdownMenu.matches(':hover')) {
                // Если курсор ушел, удаляем класс 'show', скрывая меню
                dropdownMenu.classList.remove('show');
            }
        }, 100); // 100 миллисекунд задержки
    }
}

// Функция для удержания подменю открытым, когда курсор находится над ним
function keepDropdownOpen() {
    // Получаем элемент выпадающего меню по его ID
    const dropdownMenu = document.getElementById('mainDropdownMenu');
    // Проверяем, существует ли элемент
    if (dropdownMenu) {
        // Гарантируем, что класс 'show' присутствует, пока курсор над меню
        dropdownMenu.classList.add('show');
    }
}

// Функция для закрытия подменю, когда курсор уходит с самого меню
function closeDropdown() {
    // Получаем элемент выпадающего меню по его ID
    const dropdownMenu = document.getElementById('mainDropdownMenu');
    // Проверяем, существует ли элемент
    if (dropdownMenu) {
        // Удаляем класс 'show', скрывая меню
        dropdownMenu.classList.remove('show');
    }
}

// Добавляем слушатели событий после полной загрузки DOM-дерева страницы
document.addEventListener('DOMContentLoaded', function() {
    // Получаем основной элемент пункта меню, который открывает выпадающий список
    const mainDropdown = document.getElementById('mainDropdown');
    // Проверяем, существует ли этот элемент
    if (mainDropdown) {
        // Добавляем обработчик события наведения мыши (mouseenter)
        mainDropdown.addEventListener('mouseenter', showMainDropdown);
        // Добавляем обработчик события ухода мыши (mouseleave)
        mainDropdown.addEventListener('mouseleave', hideMainDropdown);
    }
});
