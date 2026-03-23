// static/inventory/js/search.js

$(document).ready(function() {
    console.log('Search.js loaded');  // Проверка загрузки

    // Инициализируем поиск для всех полей с классом global-search
    initGlobalSearch();
});

function initGlobalSearch() {
    const searchInput = $('.global-search');

    if (!searchInput.length) {
        console.log('No .global-search found');
        return;
    }

    console.log('Found', searchInput.length, 'search inputs');

    searchInput.on('keyup', function() {
        const searchText = $(this).val().toLowerCase().trim();
        console.log('Searching for:', searchText);

        // Находим таблицу — ищем ближайший контейнер с таблицей
        const $container = $(this).closest('.card, .container-fluid, .row');
        const $table = $container.find('table');

        if (!$table.length) {
            console.log('No table found');
            return;
        }

        const $rows = $table.find('tbody tr');
        console.log('Found', $rows.length, 'rows');

        if (searchText === '') {
            $rows.show();
            // Убираем сообщение "ничего не найдено"
            $table.find('.empty-search-row').remove();
            return;
        }

        let visibleCount = 0;

        $rows.each(function() {
            const $row = $(this);
            let rowText = '';

            // Собираем текст из всех ячеек (кроме последней с кнопками)
            $row.find('td:not(:last-child)').each(function() {
                rowText += $(this).text().toLowerCase() + ' ';
            });

            if (rowText.indexOf(searchText) > -1) {
                $row.show();
                visibleCount++;
            } else {
                $row.hide();
            }
        });

        // Показываем сообщение, если ничего не найдено
        showEmptyResult($table, searchText, visibleCount);
    });
}

function showEmptyResult($table, searchText, visibleCount) {
    const $emptyRow = $table.find('.empty-search-row');

    if (visibleCount === 0 && searchText !== '') {
        if ($emptyRow.length === 0) {
            const colCount = $table.find('thead th').length || 2;
            const emptyHtml = `
                <tr class="empty-search-row">
                    <td colspan="${colCount}" class="text-center py-4 text-muted">
                        🔍 Ничего не найдено по запросу "<strong>${escapeHtml(searchText)}</strong>"
                    </td>
                 </tr>
            `;
            $table.find('tbody').append(emptyHtml);
        } else {
            $emptyRow.find('strong').text(searchText);
            $emptyRow.show();
        }
    } else {
        $emptyRow.remove();
    }
}

function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, function(m) { return map[m]; });
}