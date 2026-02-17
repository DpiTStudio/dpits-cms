/**
 * ============================================
 * ФАЙЛ: header_menu_dropdown.js
 * ОПИСАНИЕ: Скрипт для управления выпадающим меню в шапке сайта
 * ============================================
 */

// Функция для показа подменю при наведении мыши
function showDropdown(menuId) {
    const dropdownMenu = document.getElementById(menuId);
    if (dropdownMenu) {
        dropdownMenu.classList.add('show');
    }
}

// Функция для скрытия подменю при уходе мыши
function hideDropdown(menuId) {
    const dropdownMenu = document.getElementById(menuId);
    if (dropdownMenu) {
        setTimeout(() => {
            if (!dropdownMenu.matches(':hover')) {
                dropdownMenu.classList.remove('show');
            }
        }, 100);
    }
}

// Функция для удержания подменю открытым
function keepDropdownOpen(menuId) {
    const dropdownMenu = document.getElementById(menuId);
    if (dropdownMenu) {
        dropdownMenu.classList.add('show');
    }
}

// Функция для закрытия подменю
function closeDropdown(menuId) {
    const dropdownMenu = document.getElementById(menuId);
    if (dropdownMenu) {
        dropdownMenu.classList.remove('show');
    }
}

// Добавляем слушатели событий после полной загрузки DOM-дерева страницы

