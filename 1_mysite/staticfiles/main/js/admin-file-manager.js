// JavaScript для файлового менеджера в админке

document.addEventListener('DOMContentLoaded', function() {
    // Подтверждение опасных действий
    const dangerousLinks = document.querySelectorAll('a[onclick*="confirm"]');
    dangerousLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            const confirmMessage = this.getAttribute('onclick').match(/confirm\('([^']+)'\)/);
            if (confirmMessage && !confirm(confirmMessage[1])) {
                e.preventDefault();
            }
        });
    });
    
    // Автозаполнение пути при вводе имени файла
    const nameField = document.querySelector('input[name="name"]');
    const pathField = document.querySelector('input[name="file_path"]');
    
    if (nameField && pathField && !pathField.value) {
        nameField.addEventListener('blur', function() {
            if (!pathField.value && this.value) {
                // Предлагаем путь на основе имени файла
                const fileName = this.value.replace(/\s+/g, '_').toLowerCase();
                pathField.value = '/path/to/' + fileName;
            }
        });
    }
    
    // Обновление информации о файле при изменении пути
    if (pathField) {
        pathField.addEventListener('change', function() {
            // Можно добавить AJAX запрос для проверки существования файла
            console.log('Проверка файла:', this.value);
        });
    }
    
    // Подсветка строк с ошибками в предпросмотре логов
    const filePreview = document.querySelector('.file-preview');
    if (filePreview && filePreview.textContent.includes('ERROR')) {
        const lines = filePreview.innerHTML.split('\n');
        filePreview.innerHTML = lines.map(line => {
            if (line.includes('ERROR')) {
                return '<span style="color: red; background: #ffe6e6;">' + line + '</span>';
            } else if (line.includes('WARNING')) {
                return '<span style="color: orange; background: #fff3cd;">' + line + '</span>';
            }
            return line;
        }).join('\n');
    }
});