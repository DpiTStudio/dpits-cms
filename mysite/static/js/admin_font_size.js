document.addEventListener("DOMContentLoaded", function () {
    // Configuration
    const STORAGE_KEY = 'admin_font_size_scale';
    const DEFAULT_SCALE = 0.9; // Default requested "smaller" size (90% of original)
    const MIN_SCALE = 0.7;
    const MAX_SCALE = 1.2;
    const STEP = 0.05;

    // Helper to apply font size
    function setScale(scale) {
        // We adjust the percentage of the base font size on the HTML element
        // Standard Bootstap/Browsers is 16px = 100%. 
        // We set it to scale * 100 + "%" is not quite right if existing CSS sets it.
        // It's safer to set a pixel value assuming 16px is base, or use percentage.
        // Let's use percentage: 100% = 16px. 0.9 = 90%.
        const percent = Math.round(scale * 100);
        document.documentElement.style.fontSize = percent + '%';
        localStorage.setItem(STORAGE_KEY, scale);
        
        // Update display text
        const display = document.getElementById('font-size-display');
        if (display) {
            display.innerText = percent + '%';
        }
    }

    // Load saved settings or default
    let currentScale = parseFloat(localStorage.getItem(STORAGE_KEY));
    if (isNaN(currentScale)) {
        currentScale = DEFAULT_SCALE;
    }
    // Apply immediate
    setScale(currentScale);

    // Create UI Controls
    function createControls() {
        // Try to find the navbar to attach to
        const navbar = document.querySelector('.main-header .navbar-nav.ml-auto') || document.querySelector('.navbar-nav');
        
        if (!navbar) return;

        const li = document.createElement('li');
        li.className = 'nav-item d-none d-sm-inline-block';
        li.style.display = 'flex';
        li.style.alignItems = 'center';
        li.style.marginRight = '10px';

        const container = document.createElement('div');
        container.className = 'btn-group btn-group-sm';
        container.style.alignItems = 'center';

        // Decrease Button
        const btnDec = document.createElement('button');
        btnDec.className = 'btn btn-default btn-sm';
        btnDec.innerHTML = '<i class="fas fa-minus" style="font-size: 10px;"></i>';
        btnDec.title = "Уменьшить шрифт";
        btnDec.type = "button";
        btnDec.onclick = function(e) {
            e.preventDefault();
            if (currentScale > MIN_SCALE) {
                currentScale -= STEP;
                setScale(currentScale);
            }
        };

        // Display
        const span = document.createElement('span');
        span.id = 'font-size-display';
        span.className = 'btn btn-default btn-sm disabled';
        span.style.background = '#fff';
        span.style.color = '#333';
        span.style.width = '55px';
        span.innerText = Math.round(currentScale * 100) + '%';

        // Increase Button
        const btnInc = document.createElement('button');
        btnInc.className = 'btn btn-default btn-sm';
        btnInc.innerHTML = '<i class="fas fa-plus" style="font-size: 10px;"></i>';
        btnInc.title = "Увеличить шрифт";
        btnInc.type = "button";
        btnInc.onclick = function(e) {
            e.preventDefault();
            if (currentScale < MAX_SCALE) {
                currentScale += STEP;
                setScale(currentScale);
            }
        };

        // Reset Button (optional, maybe specific icon)
        const btnReset = document.createElement('button');
        btnReset.className = 'btn btn-default btn-sm';
        btnReset.innerHTML = '<i class="fas fa-redo" style="font-size: 10px;"></i>';
        btnReset.title = "Сброс";
        btnReset.type = "button";
        btnReset.onclick = function(e) {
            e.preventDefault();
            currentScale = DEFAULT_SCALE;
            setScale(currentScale);
        };

        container.appendChild(btnDec);
        container.appendChild(span);
        container.appendChild(btnInc);
        container.appendChild(btnReset);

        li.appendChild(container);

        // Prepend to the list so it's visible
        navbar.insertBefore(li, navbar.firstChild);
    }

    // Wait slightly for DOM to settle (Jazzmin sometimes modifies navbar)
    setTimeout(createControls, 500);
});
