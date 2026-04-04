/**
 * news/static/news/js/category-image.js
 * 
 * Данный скрипт обеспечивает динамический предпросмотр изображения категории
 * в административной панели Django при выборе категории для новости.
 */

document.addEventListener('DOMContentLoaded', function() {
    // Находим поля в админке Django
    const categorySelect = document.getElementById('id_category');
    const imageInput = document.getElementById('id_image');
    
    if (!categorySelect || !imageInput) return;

    // Создаем контейнер для предпросмотра, если его нет
    let previewContainer = document.getElementById('category-image-preview-container');
    if (!previewContainer) {
        previewContainer = document.createElement('div');
        previewContainer.id = 'category-image-preview-container';
        previewContainer.style.marginTop = '10px';
        previewContainer.style.padding = '10px';
        previewContainer.style.border = '1px dashed #ccc';
        previewContainer.style.borderRadius = '4px';
        previewContainer.style.display = 'none';
        
        const label = document.createElement('div');
        label.innerText = 'Предпросмотр изображения категории (будет использовано, если своё не загружено):';
        label.style.fontSize = '12px';
        label.style.color = '#666';
        label.style.marginBottom = '5px';
        
        const img = document.createElement('img');
        img.id = 'category-image-preview';
        img.style.maxWidth = '200px';
        img.style.maxHeight = '200px';
        img.style.display = 'block';
        img.style.borderRadius = '4px';
        
        previewContainer.appendChild(label);
        previewContainer.appendChild(img);
        
        // Вставляем после поля выбора изображения
        const imageFieldRow = imageInput.closest('.form-row');
        if (imageFieldRow) {
            imageFieldRow.appendChild(previewContainer);
        }
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
        
        // Показываем предпросмотр только если своё изображение не выбрано
        // В Django админке ImageField имеет input[type=file]
        // Если есть ссылка на текущий файл (при редактировании), imageInput.nextElementSibling содержит ссылку
        const hasOwnImage = imageInput.getAttribute('data-has-file') === 'true' || imageInput.value !== '';
        
        if (imageUrl && !hasOwnImage) {
            previewImg.src = imageUrl;
            previewContainer.style.display = 'block';
        } else {
            previewContainer.style.display = 'none';
        }
    }

    // Отслеживаем изменения категории
    categorySelect.addEventListener('change', updatePreview);
    
    // Отслеживаем выбор своего файла (скрываем предпросмотр категории если выбран файл)
    imageInput.addEventListener('change', function() {
        updatePreview();
    });

    // Специальная проверка для существующего файла (Django ClearableFileInput)
    // Если есть текущий файл, он обычно отображается выше инпута
    const currentLink = imageInput.closest('.form-row')?.querySelector('a');
    if (currentLink && (currentLink.href.includes('/media/'))) {
        imageInput.setAttribute('data-has-file', 'true');
    }
});
