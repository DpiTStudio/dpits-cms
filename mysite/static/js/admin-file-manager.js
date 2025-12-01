/* static/js/admin-file-manager.js */
// JavaScript для админки управления файлами

(function($) {
    'use strict';
    
    $(document).ready(function() {
        // Подсветка строк в предпросмотре файлов
        $('.file-preview pre').each(function() {
            var content = $(this).text();
            var lines = content.split('\n');
            var highlighted = '';
            
            lines.forEach(function(line, index) {
                var lineNumber = index + 1;
                var className = '';
                
                // Подсветка ошибок в логах
                if (line.toLowerCase().includes('error') || line.includes('[ERROR]')) {
                    className = 'text-danger';
                } else if (line.toLowerCase().includes('warning') || line.includes('[WARNING]')) {
                    className = 'text-warning';
                } else if (line.toLowerCase().includes('info') || line.includes('[INFO]')) {
                    className = 'text-info';
                }
                
                highlighted += '<span class="' + className + '">' + 
                    '<span style="color: #999; margin-right: 10px; font-size: 11px;">' + 
                    lineNumber.toString().padStart(3, '0') + 
                    '</span>' + 
                    line + 
                    '</span>\n';
            });
            
            $(this).html(highlighted);
        });
        
        // Обработка кнопок в списке файлов
        $('.action-btn').on('click', function(e) {
            var action = $(this).data('action');
            var fileId = $(this).data('file-id');
            
            if (action === 'clear') {
                if (!confirm('Вы уверены, что хотите очистить содержимое файла?')) {
                    e.preventDefault();
                }
            } else if (action === 'delete') {
                if (!confirm('Вы уверены, что хотите удалить файл? Это действие нельзя отменить!')) {
                    e.preventDefault();
                }
            }
        });
        
        // Автоматическое обновление информации о файле при фокусе на поле пути
        $('#id_file_path').on('blur', function() {
            var filePath = $(this).val();
            
            if (filePath && filePath.trim() !== '') {
                // Показываем индикатор загрузки
                $(this).addClass('loading');
                
                // Здесь можно добавить AJAX запрос для проверки файла
                // ...
                
                $(this).removeClass('loading');
            }
        });
        
        // Переключение режима редактирования для текстовых файлов
        $('#id_is_text_file').on('change', function() {
            var isTextFile = $(this).is(':checked');
            var contentField = $('#id_content');
            
            if (isTextFile) {
                contentField.prop('readonly', false);
                contentField.css('background-color', '#fff');
            } else {
                contentField.prop('readonly', true);
                contentField.css('background-color', '#f8f9fa');
                contentField.val('[Редактирование недоступно для бинарных файлов]');
            }
        });
        
        // Инициализация состояния поля контента
        if ($('#id_is_text_file').is(':checked')) {
            $('#id_content').prop('readonly', false);
        } else {
            $('#id_content').prop('readonly', true);
        }
    });
})(django.jQuery);