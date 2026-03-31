/**
 * cart.js — Инновационная система корзины с AJAX
 * Drawer, анимации, тосты, живое обновление
 */

(function () {
    'use strict';

    // ======================================================
    // КОНФИГУРАЦИЯ
    // ======================================================
    const CART_CONFIG = {
        drawerSelector: '#cartDrawer',
        overlaySelector: '#cartOverlay',
        badgeSelector: '.cart-badge',
        fabBadgeSelector: '.cart-fab-badge',
        itemsContainerSelector: '#cartDrawerItems',
        totalSelector: '#cartDrawerTotal',
        toastSelector: '#cartToast',
        fabSelector: '#cartFab',
        csrfToken: document.querySelector('[name=csrfmiddlewaretoken]')?.value || getCookie('csrftoken'),
        urls: {
            add: window.CART_URLS?.add || '/services/cart/add/',
            remove: window.CART_URLS?.remove || '/services/cart/remove/',
            clear: window.CART_URLS?.clear || '/services/cart/clear/',
            detail: window.CART_URLS?.detail || '/services/cart/detail/',
        }
    };

    // ======================================================
    // ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
    // ======================================================
    function getCookie(name) {
        const val = `; ${document.cookie}`;
        const parts = val.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop().split(';').shift();
    }

    function formatPrice(price) {
        const num = parseFloat(price);
        if (isNaN(num)) return price;
        return num.toLocaleString('ru-RU', { minimumFractionDigits: 0, maximumFractionDigits: 0 }) + ' ₽';
    }

    async function apiRequest(url, method = 'POST', body = null) {
        const headers = {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': CART_CONFIG.csrfToken || getCookie('csrftoken'),
        };
        if (body) headers['Content-Type'] = 'application/json';

        const resp = await fetch(url, {
            method,
            headers,
            body: body ? JSON.stringify(body) : null,
        });

        if (!resp.ok) {
            const err = await resp.json().catch(() => ({}));
            throw new Error(err.message || 'Ошибка сервера');
        }
        return resp.json();
    }

    // ======================================================
    // ТОСТ-УВЕДОМЛЕНИЯ
    // ======================================================
    let toastTimer = null;

    function showToast(message, detail = '', isError = false) {
        const toast = document.querySelector(CART_CONFIG.toastSelector);
        if (!toast) return;

        const icon = toast.querySelector('.cart-toast-icon i');
        const strong = toast.querySelector('.cart-toast-text strong');
        const span = toast.querySelector('.cart-toast-text span');

        if (icon) icon.className = isError ? 'fas fa-exclamation-circle' : 'fas fa-check-circle';
        if (strong) strong.textContent = message;
        if (span) span.textContent = detail;

        toast.classList.toggle('error', isError);
        toast.classList.add('show');

        clearTimeout(toastTimer);
        toastTimer = setTimeout(() => {
            toast.classList.remove('show');
        }, 3500);
    }

    // ======================================================
    // ОБНОВЛЕНИЕ СЧЁТЧИКОВ (BADGE)
    // ======================================================
    function updateBadges(count) {
        document.querySelectorAll(CART_CONFIG.badgeSelector).forEach(badge => {
            badge.textContent = count;
            badge.classList.toggle('hidden', count === 0);
            if (count > 0) badge.classList.add('bounce');
            setTimeout(() => badge.classList.remove('bounce'), 600);
        });

        // FAB badge
        document.querySelectorAll(CART_CONFIG.fabBadgeSelector).forEach(fab => {
            fab.textContent = count;
            fab.style.display = count > 0 ? 'flex' : 'none';
        });
    }

    // ======================================================
    // DRAWER (БОКОВАЯ ПАНЕЛЬ)
    // ======================================================
    function openDrawer() {
        const drawer = document.querySelector(CART_CONFIG.drawerSelector);
        const overlay = document.querySelector(CART_CONFIG.overlaySelector);
        if (!drawer) return;
        drawer.classList.add('open');
        if (overlay) overlay.classList.add('active');
        document.body.style.overflow = 'hidden';
        loadCartItems();
    }

    function closeDrawer() {
        const drawer = document.querySelector(CART_CONFIG.drawerSelector);
        const overlay = document.querySelector(CART_CONFIG.overlaySelector);
        if (!drawer) return;
        drawer.classList.remove('open');
        if (overlay) overlay.classList.remove('active');
        document.body.style.overflow = '';
    }

    // ======================================================
    // РЕНДЕР ЭЛЕМЕНТОВ В DRAWER
    // ======================================================
    function renderCartItems(data) {
        const container = document.querySelector(CART_CONFIG.itemsContainerSelector);
        const totalEl = document.querySelector(CART_CONFIG.totalSelector);

        if (!container) return;

        updateBadges(data.count);

        if (data.count === 0) {
            container.innerHTML = `
                <div class="cart-empty-state">
                    <div class="cart-empty-icon">
                        <i class="fas fa-shopping-basket"></i>
                    </div>
                    <h5>Корзина пуста</h5>
                    <p>Добавьте услуги, чтобы сформировать заказ</p>
                    <a href="${window.CART_URLS?.servicesList || '/services/'}" class="btn btn-primary rounded-pill px-4" onclick="closeDrawer()">
                        <i class="fas fa-th-large me-2"></i>Перейти к услугам
                    </a>
                </div>`;
            if (totalEl) totalEl.textContent = '0 ₽';
            // Скрыть footer-кнопки
            const footer = document.querySelector('#cartDrawerFooterActions');
            if (footer) footer.style.display = 'none';
            return;
        }

        const footer = document.querySelector('#cartDrawerFooterActions');
        if (footer) footer.style.display = '';

        container.innerHTML = data.items.map((item, idx) => `
            <div class="cart-item adding" data-service-id="${item.id}" style="animation-delay: ${idx * 0.05}s">
                <div class="cart-item-icon">
                    ${item.icon
                        ? `<img src="${item.icon}" alt="${item.name}">`
                        : `<i class="fas fa-cube"></i>`
                    }
                </div>
                <div class="cart-item-info">
                    <a href="${item.url}" class="cart-item-name">${item.name}</a>
                    <div class="cart-item-price">${formatPrice(item.price)}</div>
                </div>
                <button 
                    class="cart-item-remove" 
                    data-remove-id="${item.id}"
                    title="Удалить из корзины"
                    aria-label="Удалить ${item.name}">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `).join('');

        if (totalEl) totalEl.textContent = formatPrice(data.total);

        // Навесить обработчики на кнопки удаления
        container.querySelectorAll('[data-remove-id]').forEach(btn => {
            btn.addEventListener('click', () => removeFromCart(btn.dataset.removeId, btn.closest('.cart-item')));
        });
    }

    // ======================================================
    // ЗАГРУЗКА КОРЗИНЫ (AJAX)
    // ======================================================
    async function loadCartItems() {
        const container = document.querySelector(CART_CONFIG.itemsContainerSelector);
        if (container) {
            container.innerHTML = `
                <div class="cart-empty-state" style="min-height: 200px;">
                    <div class="cart-spinner" style="width: 36px; height: 36px; border-color: rgba(99,102,241,0.2); border-top-color: #6366f1;"></div>
                </div>`;
        }

        try {
            const data = await apiRequest(CART_CONFIG.urls.detail, 'GET');
            renderCartItems(data);
        } catch (e) {
            if (container) {
                container.innerHTML = `<div class="cart-empty-state"><p class="text-danger">Не удалось загрузить корзину</p></div>`;
            }
        }
    }

    // ======================================================
    // ДОБАВЛЕНИЕ В КОРЗИНУ (AJAX)
    // ======================================================
    async function addToCart(serviceId, btn) {
        if (btn) {
            btn.classList.add('loading');
            btn.disabled = true;
        }

        // Анимация пульса на иконке хедера
        document.querySelectorAll('.cart-header-btn').forEach(b => {
            b.classList.add('pulse-add');
            setTimeout(() => b.classList.remove('pulse-add'), 700);
        });

        try {
            const url = CART_CONFIG.urls.add.replace('0/', `${serviceId}/`);
            const data = await apiRequest(url, 'POST');
            updateBadges(data.count);

            showToast('Добавлено в корзину', data.message || '', false);

            if (btn) {
                btn.classList.remove('loading');
                btn.classList.add('success');
                const btnText = btn.querySelector('.btn-text');
                if (btnText) btnText.innerHTML = '<i class="fas fa-check me-1"></i>Добавлено';
                setTimeout(() => {
                    btn.classList.remove('success');
                    btn.disabled = false;
                    if (btnText) btnText.innerHTML = '<i class="fas fa-cart-plus me-2"></i><span>В корзину</span>';
                }, 2500);
            }

            // Обновить виджет в сайдбаре если открыт
            refreshSidebarWidget();

        } catch (err) {
            showToast('Ошибка', err.message, true);
            if (btn) {
                btn.classList.remove('loading');
                btn.disabled = false;
            }
        }
    }

    // ======================================================
    // УДАЛЕНИЕ ИЗ КОРЗИНЫ (AJAX)
    // ======================================================
    async function removeFromCart(serviceId, itemEl) {
        if (itemEl) itemEl.classList.add('removing');

        try {
            const url = CART_CONFIG.urls.remove.replace('0/', `${serviceId}/`);
            const data = await apiRequest(url, 'GET');

            if (itemEl) {
                setTimeout(() => {
                    itemEl.remove();
                    // Если корзина опустела
                    const container = document.querySelector(CART_CONFIG.itemsContainerSelector);
                    if (container && !container.querySelector('.cart-item')) {
                        renderCartItems(data);
                    }
                }, 350);
            }

            updateBadges(data.count);

            // Обновить итог
            const totalEl = document.querySelector(CART_CONFIG.totalSelector);
            if (totalEl) totalEl.textContent = formatPrice(data.total);

            showToast('Удалено из корзины', data.message || '');
            refreshSidebarWidget();

        } catch (err) {
            showToast('Ошибка удаления', err.message, true);
            if (itemEl) itemEl.classList.remove('removing');
        }
    }

    // ======================================================
    // ОЧИСТКА КОРЗИНЫ (AJAX)
    // ======================================================
    async function clearCart() {
        const clearBtn = document.querySelector('#cartClearBtn');
        if (clearBtn) {
            clearBtn.innerHTML = '<div class="cart-spinner"></div>';
            clearBtn.disabled = true;
        }

        try {
            const data = await apiRequest(CART_CONFIG.urls.clear, 'GET');
            renderCartItems(data);
            showToast('Корзина очищена', '');

            if (clearBtn) {
                clearBtn.innerHTML = '<i class="fas fa-trash-alt me-2"></i>Очистить корзину';
                clearBtn.disabled = false;
            }

            refreshSidebarWidget();
        } catch (err) {
            showToast('Ошибка', err.message, true);
            if (clearBtn) {
                clearBtn.innerHTML = '<i class="fas fa-trash-alt me-2"></i>Очистить корзину';
                clearBtn.disabled = false;
            }
        }
    }

    // ======================================================
    // ОБНОВЛЕНИЕ ВИДЖЕТА В САЙДБАРЕ
    // ======================================================
    async function refreshSidebarWidget() {
        const widget = document.querySelector('.cart-widget-dynamic');
        if (!widget) return;

        try {
            const data = await apiRequest(CART_CONFIG.urls.detail, 'GET');
            renderSidebarWidget(widget, data);
        } catch (e) {
            // Тихая ошибка
        }
    }

    function renderSidebarWidget(widget, data) {
        const itemsContainer = widget.querySelector('.cart-widget-items');
        const totalPrice = widget.querySelector('.cart-widget-total-price');
        const widgetBadge = widget.querySelector('.cart-widget-badge');

        if (widgetBadge) widgetBadge.textContent = data.count;

        if (!itemsContainer) return;

        if (data.count === 0) {
            itemsContainer.innerHTML = `
                <div class="cart-widget-empty">
                    <div class="cart-widget-empty-icon"><i class="fas fa-shopping-basket"></i></div>
                    <p class="text-muted small mb-0">Корзина пуста</p>
                </div>`;
            if (totalPrice) totalPrice.textContent = '0 ₽';
            return;
        }

        itemsContainer.innerHTML = data.items.map(item => `
            <div class="cart-widget-item" data-service-id="${item.id}">
                <div class="cart-widget-item-icon">
                    ${item.icon ? `<img src="${item.icon}" alt="">` : `<i class="fas fa-cube text-primary"></i>`}
                </div>
                <div class="cart-widget-item-name">${item.name}</div>
                <div class="cart-widget-item-price">${formatPrice(item.price)}</div>
                <button class="cart-widget-item-remove" data-remove-id="${item.id}">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `).join('');

        if (totalPrice) totalPrice.textContent = formatPrice(data.total);

        itemsContainer.querySelectorAll('[data-remove-id]').forEach(btn => {
            btn.addEventListener('click', async () => {
                const id = btn.dataset.removeId;
                try {
                    const url = CART_CONFIG.urls.remove.replace('0/', `${id}/`);
                    const resp = await apiRequest(url, 'GET');
                    updateBadges(resp.count);
                    renderSidebarWidget(widget, resp);
                    // Обновить drawer если открыт
                    const drawer = document.querySelector(CART_CONFIG.drawerSelector);
                    if (drawer && drawer.classList.contains('open')) {
                        loadCartItems();
                    }
                    showToast('Удалено из корзины', '');
                } catch (e) {
                    showToast('Ошибка', e.message, true);
                }
            });
        });
    }

    // ======================================================
    // ИНИЦИАЛИЗАЦИЯ
    // ======================================================
    function init() {
        // Клик по кнопке корзины в хедере -> открыть drawer
        document.querySelectorAll('[data-cart-open]').forEach(btn => {
            btn.addEventListener('click', e => {
                e.preventDefault();
                openDrawer();
            });
        });

        // Закрытие drawer
        const closeBtn = document.querySelector('#cartDrawerClose');
        if (closeBtn) closeBtn.addEventListener('click', closeDrawer);

        // Закрытие по оверлею
        const overlay = document.querySelector(CART_CONFIG.overlaySelector);
        if (overlay) overlay.addEventListener('click', closeDrawer);

        // Закрытие по ESC
        document.addEventListener('keydown', e => {
            if (e.key === 'Escape') closeDrawer();
        });

        // Кнопка очистки корзины
        const clearBtn = document.querySelector('#cartClearBtn');
        if (clearBtn) clearBtn.addEventListener('click', clearCart);

        // AJAX-добавление в корзину: все формы с data-cart-form
        document.querySelectorAll('[data-cart-form]').forEach(form => {
            form.addEventListener('submit', async e => {
                e.preventDefault();
                const serviceId = form.dataset.serviceId;
                const btn = form.querySelector('[data-cart-submit]');
                await addToCart(serviceId, btn);
            });
        });

        // Закрытие тоста по клику
        const toast = document.querySelector(CART_CONFIG.toastSelector);
        if (toast) toast.addEventListener('click', () => toast.classList.remove('show'));

        // Начальная загрузка виджета в сайдбаре
        refreshSidebarWidget();

        // Swipe для закрытия drawer на мобильных
        initSwipeClose();

        // Закрыть drawer при клике на ссылку внутри
        const drawer = document.querySelector(CART_CONFIG.drawerSelector);
        if (drawer) {
            drawer.addEventListener('click', e => {
                if (e.target.closest('a[href]') && !e.target.closest('[data-no-close]')) {
                    // Небольшая задержка для плавности
                    setTimeout(closeDrawer, 120);
                }
            });
        }
    }

    // ======================================================
    // SWIPE ЗАКРЫТИЕ DRAWER (мобильные)
    // ======================================================
    function initSwipeClose() {
        const drawer = document.querySelector(CART_CONFIG.drawerSelector);
        if (!drawer) return;

        let startX = 0;
        let isDragging = false;

        drawer.addEventListener('touchstart', e => {
            startX = e.touches[0].clientX;
            isDragging = true;
        }, { passive: true });

        drawer.addEventListener('touchmove', e => {
            if (!isDragging) return;
            const deltaX = e.touches[0].clientX - startX;
            if (deltaX > 0) {
                drawer.style.transform = `translateX(${deltaX}px)`;
            }
        }, { passive: true });

        drawer.addEventListener('touchend', e => {
            if (!isDragging) return;
            isDragging = false;
            const deltaX = e.changedTouches[0].clientX - startX;
            drawer.style.transform = '';
            if (deltaX > 120) {
                closeDrawer();
            }
        });
    }

    // Экспорт для внешнего использования
    window.CartSystem = { open: openDrawer, close: closeDrawer, refresh: loadCartItems, addToCart };

    // Запуск
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
