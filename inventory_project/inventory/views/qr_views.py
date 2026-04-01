import json

from django.http import JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string


def qr_simple(request):
    """Простая страница для теста QR-кода"""
    return render(request, 'inventory/qr_simple.html')

def print_qr_from_doc(request):
    """Генерация страницы с QR-кодами для строк документа"""
    if request.method == 'POST':
        data = json.loads(request.body)
        items = data.get('items', [])

        # Формируем данные для QR-кодов
        qr_items = []
        for item in items:
            # Формат: айди|цена
            qr_data = f"{item['nom_id']}|{item['price']}"
            qr_items.append({
                'title': item['title'],
                'izm': item['izm'],
                'price': item['price'],
                'qr_data': qr_data
            })

        # Рендерим страницу с QR-кодами
        html = render_to_string('inventory/qr_print.html', {
            'qr_items': qr_items,
            'doc_nomer': data.get('doc_nomer', ''),
            'doc_datadoc': data.get('doc_datadoc', '')
        })

        return JsonResponse({'html': html})

    return JsonResponse({'error': 'Метод не поддерживается'}, status=405)