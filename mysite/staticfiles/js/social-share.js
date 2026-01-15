// ============================================
// ФАЙЛ: social-share.js
// ОПИСАНИЕ: Функционал социального шаринга
// ============================================

(function() {
    'use strict';
    
    // URL и заголовок текущей страницы
    const currentUrl = encodeURIComponent(window.location.href);
    const currentTitle = encodeURIComponent(document.title);
    const currentDescription = encodeURIComponent(
        document.querySelector('meta[name="description"]')?.content || ''
    );
    
    // URL для разных соцсетей
    const shareUrls = {
        vk: `https://vk.com/share.php?url=${currentUrl}&title=${currentTitle}`,
        telegram: `https://t.me/share/url?url=${currentUrl}&text=${currentTitle}`,
        whatsapp: `https://wa.me/?text=${currentTitle}%20${currentUrl}`,
        facebook: `https://www.facebook.com/sharer/sharer.php?u=${currentUrl}`,
        twitter: `https://twitter.com/intent/tweet?url=${currentUrl}&text=${currentTitle}`,
    };
    
    // Копирование ссылки в буфер обмена
    function copyToClipboard(text) {
        if (navigator.clipboard && navigator.clipboard.writeText) {
            navigator.clipboard.writeText(text).then(() => {
                if (window.dpitsCMS && window.dpitsCMS.showToast) {
                    window.dpitsCMS.showToast('Ссылка скопирована в буфер обмена!', 'success');
                }
            }).catch(() => {
                fallbackCopyToClipboard(text);
            });
        } else {
            fallbackCopyToClipboard(text);
        }
    }
    
    // Fallback для старых браузеров
    function fallbackCopyToClipboard(text) {
        const textArea = document.createElement('textarea');
        textArea.value = text;
        textArea.style.position = 'fixed';
        textArea.style.opacity = '0';
        document.body.appendChild(textArea);
        textArea.select();
        
        try {
            document.execCommand('copy');
            if (window.dpitsCMS && window.dpitsCMS.showToast) {
                window.dpitsCMS.showToast('Ссылка скопирована в буфер обмена!', 'success');
            }
        } catch (err) {
            if (window.dpitsCMS && window.dpitsCMS.showToast) {
                window.dpitsCMS.showToast('Не удалось скопировать ссылку', 'error');
            }
        }
        
        document.body.removeChild(textArea);
    }
    
    // Обработчик клика на кнопку шаринга
    function handleShareClick(e) {
        const button = e.currentTarget;
        const network = button.dataset.network;
        
        if (network === 'copy') {
            copyToClipboard(window.location.href);
            e.preventDefault();
            return false;
        }
        
        const url = shareUrls[network];
        if (url) {
            window.open(url, '_blank', 'width=600,height=400');
            e.preventDefault();
            return false;
        }
    }
    
    // Инициализация кнопок шаринга
    function init() {
        const shareButtons = document.querySelectorAll('.share-btn');
        
        shareButtons.forEach(button => {
            button.addEventListener('click', handleShareClick);
        });
    }
    
    // Создание кнопок шаринга программно
    function createShareButtons(container, networks = ['vk', 'telegram', 'whatsapp', 'copy']) {
        const networksConfig = {
            vk: { icon: 'fab fa-vk', label: 'ВКонтакте' },
            telegram: { icon: 'fab fa-telegram', label: 'Telegram' },
            whatsapp: { icon: 'fab fa-whatsapp', label: 'WhatsApp' },
            facebook: { icon: 'fab fa-facebook', label: 'Facebook' },
            twitter: { icon: 'fab fa-twitter', label: 'Twitter' },
            copy: { icon: 'fas fa-copy', label: 'Копировать ссылку' }
        };
        
        networks.forEach(network => {
            const config = networksConfig[network];
            if (!config) return;
            
            const button = document.createElement('a');
            button.href = '#';
            button.className = `share-btn share-btn-${network}`;
            button.dataset.network = network;
            button.setAttribute('aria-label', config.label);
            button.setAttribute('title', config.label);
            button.innerHTML = `<i class="${config.icon}"></i>`;
            
            button.addEventListener('click', handleShareClick);
            container.appendChild(button);
        });
    }
    
    // Инициализация при загрузке DOM
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
    
    // Экспортируем функции
    window.socialShare = {
        copyToClipboard,
        createShareButtons,
        shareUrls
    };
})();
