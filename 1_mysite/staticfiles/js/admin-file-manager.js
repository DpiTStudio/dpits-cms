// static/js/admin-file-manager.js
// JavaScript для админки управления файлами

(function($) {
    'use strict';
    
    $(document).ready(function() {
        // Добавляем подсветку синтаксиса для файлов
        function highlightSyntax() {
            $('textarea').each(function() {
                var textarea = $(this);
                var filePath = $('input[name="file_path"]').val();
                
                if (filePath) {
                    var extension = filePath.split('.').pop().toLowerCase();
                    
                    // CSS для разных типов файлов
                    switch(extension) {
                        case 'js':
                        case 'json':
                        case 'py':
                        case 'html':
                        case 'css':
                            textarea.css({
                                'font-family': 'Monaco, Consolas, monospace',
                                'font-size': '12px'
                            });
                            break;
                        case 'log':
                            textarea.css({
                                'font-family': 'Monaco, Consolas, monospace',
                                'font-size': '11px',
                                'background-color': '#f8f9fa'
                            });
                            break;
                        case 'conf':
                        case 'ini':
                        case 'cfg':
                        case 'env':
                            textarea.css({
                                'font-family': 'Monaco, Consolas, monospace',
                                'font-size': '12px',
                                'color': '#d63384'
                            });
                            break;
                    }
                }
            });
        }
        
        // Инициализация
        highlightSyntax();
        
        // Обновляем при изменении пути к файлу
        $('input[name="file_path"]').on('change', highlightSyntax);
        
        // Подтверждение опасных действий
        $('.dangerous-action').on('click', function(e) {
            if (!confirm('Вы уверены? Это действие нельзя отменить.')) {
                e.preventDefault();
                return false;
            }
        });
        
        // Автообновление информации о файле
        $('.refresh-file').on('click', function(e) {
            e.preventDefault();
            var url = $(this).attr('href');
            
            $.ajax({
                url: url,
                type: 'GET',
                success: function(data) {
                    location.reload();
                },
                error: function() {
                    alert('Ошибка при обновлении информации о файле');
                }
            });
        });
    });
})(django.jQuery);