/**
 * Автоматическая подстановка изображения категории при выборе категории в админке.
 */
document.addEventListener('DOMContentLoaded', function() {
    const categorySelect = document.getElementById('id_category');
    const imageInput = document.getElementById('id_image');
    
    // Создаем контейнер для превью под основным изображением
    const previewWrapper = document.createElement('div');
    previewWrapper.id = 'category-previews-wrapper';
    previewWrapper.style.marginTop = '15px';
    previewWrapper.style.display = 'flex';
    previewWrapper.style.gap = '20px';
    previewWrapper.style.flexWrap = 'wrap';
    
    if (imageInput && imageInput.parentNode) {
        // Находим родительский .form-row для News.image
        const formRow = imageInput.closest('.form-row');
        if (formRow) {
            formRow.appendChild(previewWrapper);
        } else {
            imageInput.parentNode.appendChild(previewWrapper);
        }
    }

    if (categorySelect) {
        categorySelect.addEventListener('change', function() {
            const categoryId = this.value;
            if (!categoryId) {
                previewWrapper.innerHTML = '';
                return;
            }

            fetch(`/news/api/category-image/${categoryId}/`)
                .then(response => response.json())
                .then(data => {
                    previewWrapper.innerHTML = '';
                    
                    if (data.image_url || data.hero_image_url) {
                        let html = '';
                        
                        if (data.image_url) {
                            html += `
                                <div style="padding: 10px; background: rgba(0,0,0,0.05); border: 1px dashed #ccc; border-radius: 4px; min-width: 220px;">
                                    <p style="margin: 0 0 5px 0; color: #666; font-size: 11px; font-weight: bold;">Основное изображение:</p>
                                    <img src="${data.image_url}" style="max-width: 200px; max-height: 150px; display: block; border-radius: 4px; margin-bottom: 5px;">
                                    <span style="color: #28a745; font-size: 10px;">Будет унаследовано из категории</span>
                                </div>
                            `;
                        }
                        
                        if (data.hero_image_url) {
                            html += `
                                <div style="padding: 10px; background: rgba(0,0,0,0.05); border: 1px dashed #ccc; border-radius: 4px; min-width: 220px;">
                                    <p style="margin: 0 0 5px 0; color: #666; font-size: 11px; font-weight: bold;">Hero изображение:</p>
                                    <img src="${data.hero_image_url}" style="max-width: 200px; max-height: 150px; display: block; border-radius: 4px; margin-bottom: 5px;">
                                    <span style="color: #28a745; font-size: 10px;">Будет унаследовано из категории</span>
                                </div>
                            `;
                        }
                        
                        previewWrapper.innerHTML = html;
                    }
                })
                .catch(error => {
                    console.error('Error fetching category image:', error);
                });
        });

        // Инициализация при загрузке страницы
        if (categorySelect.value) {
            categorySelect.dispatchEvent(new Event('change'));
        }
    }
});
