/**
 * news/static/news/js/category-image.js
 * 
 * Данный скрипт обеспечивает динамический предпросмотр изображения категории
 * в административной панели Django при выборе категории для новости.
 */

document.addEventListener('DOMContentLoaded', function() {
    // Ждем полной загрузки, включая возможные табы
    setTimeout(initCategoryImage, 100);
    
    function initCategoryImage() {
        const categorySelect = document.getElementById('id_category');
        const imageInput = document.getElementById('id_image');
        
        if (!categorySelect || !imageInput) return;

        // Определяем контейнер поля для вставки превью
        const imageFieldRow = imageInput.closest('.form-row') || imageInput.parentElement;
        
        // Создаем контейнер для превью
        let previewContainer = document.getElementById('category-image-preview-container');
        if (!previewContainer) {
            previewContainer = document.createElement('div');
            previewContainer.id = 'category-image-preview-container';
            previewContainer.className = 'category-preview-box';
            previewContainer.style.marginTop = '10px';
            previewContainer.style.padding = '15px';
            previewContainer.style.background = '#f8f9fa';
            previewContainer.style.border = '2px dashed #007bff';
            previewContainer.style.borderRadius = '8px';
            previewContainer.style.display = 'none';
            previewContainer.style.maxWidth = 'fit-content';
            
            const header = document.createElement('div');
            header.innerHTML = '<strong style="color: #007bff; display: block; margin-bottom: 5px;">📷 Автоматическое изображение категории:</strong>';
            header.style.fontSize = '13px';
            
            const img = document.createElement('img');
            img.id = 'category-image-preview';
            img.style.maxWidth = '300px';
            img.style.maxHeight = '300px';
            img.style.display = 'block';
            img.style.borderRadius = '6px';
            img.style.boxShadow = '0 4px 6px rgba(0,0,0,0.1)';
            
            const footer = document.createElement('div');
            footer.innerText = 'Это изображение будет сохранено автоматически, так как вы не выбрали своё.';
            footer.style.fontSize = '11px';
            footer.style.color = '#666';
            footer.style.marginTop = '8px';
            
            previewContainer.appendChild(header);
            previewContainer.appendChild(img);
            previewContainer.appendChild(footer);
            
            // Вставляем после поля выбора изображения
            imageFieldRow.appendChild(previewContainer);
        }

        const previewImg = document.getElementById('category-image-preview');
        let categoryImages = {};

        // Загружаем данные о картинках категорий через API
        fetch('/news/api/category-images/')
            .then(response => response.json())
            .then(data => {
                categoryImages = data;
                updatePreview();
            })
            .catch(error => console.error('Error fetching category images:', error));

        function updatePreview() {
            const categoryId = categorySelect.value;
            const imageUrl = categoryImages[categoryId];
            
            // Проверяем, есть ли уже загруженное изображение у новости
            // В Django админке при наличии файла появляется элемент "Сейчас:" (Currently:)
            const currentFileLink = imageFieldRow.querySelector('a[href*="/media/"]');
            const hasExistingFile = !!currentFileLink;
            
            // Проверяем, выбрал ли пользователь новый файл прямо сейчас
            const hasNewFile = imageInput.files && imageInput.files.length > 0;
            
            // Показываем превью категории ТОЛЬКО если нет своего файла (ни старого, ни нового)
            if (imageUrl && !hasExistingFile && !hasNewFile) {
                previewImg.src = imageUrl;
                previewContainer.style.display = 'block';
                // Подсвечиваем поле выбора категории, чтобы было понятно, откуда картинка
                categorySelect.style.borderColor = '#007bff';
                categorySelect.style.boxShadow = '0 0 0 2px rgba(0,123,255,0.25)';
            } else {
                previewContainer.style.display = 'none';
                categorySelect.style.borderColor = '';
                categorySelect.style.boxShadow = '';
            }
        }

        // Слушатели событий
        categorySelect.addEventListener('change', updatePreview);
        imageInput.addEventListener('change', updatePreview);
        
        // Малозаметный хак: если пользователь очищает файл (checkbox 'clear'), превью должно вернуться
        const clearCheckbox = imageFieldRow.querySelector('input[type="checkbox"][name$="-clear"]');
        if (clearCheckbox) {
            clearCheckbox.addEventListener('change', updatePreview);
        }
    }
});
