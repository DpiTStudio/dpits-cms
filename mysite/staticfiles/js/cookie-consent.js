/*
 * ФАЙЛ: cookie-consent.js
 * ОПИСАНИЕ: Управление уведомлением о файлах cookie
 */

(function() {
    'use strict';

    const cookieStorageKey = 'dpits_cookie_consent';
    
    function initCookieConsent() {
        if (localStorage.getItem(cookieStorageKey)) {
            return;
        }
        
        createCookieBanner();
    }
    
    function createCookieBanner() {
        const banner = document.createElement('div');
        banner.className = 'cookie-consent-banner fade-in';
        banner.innerHTML = `
            <div class="cookie-content">
                <div class="cookie-text">
                    <strong>Мы используем файлы cookie</strong>
                    <p>Продолжая использовать сайт, вы соглашаетесь на сбор файлов cookie для улучшения работы сайта.</p>
                </div>
                <div class="cookie-buttons">
                    <button id="accept-cookies" class="btn btn-primary btn-sm">Принять</button>
                    <button id="decline-cookies" class="btn btn-outline-light btn-sm">Закрыть</button>
                </div>
            </div>
        `;
        
        document.body.appendChild(banner);
        
        document.getElementById('accept-cookies').addEventListener('click', function() {
            localStorage.setItem(cookieStorageKey, 'true');
            closeBanner(banner);
        });
        
        document.getElementById('decline-cookies').addEventListener('click', function() {
            // Можно просто закрыть, не сохраняя "согласие", или сохранить "отказ"
            closeBanner(banner);
        });
    }
    
    function closeBanner(banner) {
        banner.classList.remove('fade-in');
        banner.classList.add('fade-out');
        setTimeout(() => {
            banner.remove();
        }, 300);
    }
    
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initCookieConsent);
    } else {
        initCookieConsent();
    }
})();
