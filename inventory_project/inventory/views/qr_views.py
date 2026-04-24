import json

from django.db.models import Sum, Q
from ..models import Nom, Category, Detail
from django.http import JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string

def my_view(request):
    if request.user.username != 'operator':
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("Доступ только для операторов")


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





def qr_selector(request):
    """Страница выбора товаров для печати QR-кодов"""
    categories = Category.objects.all().order_by('title')
    context = {
        'categories': categories
    }
    return render(request, 'inventory/qr_selector.html', context)


def api_qr_items(request):
    """API для получения товаров с ценами для QR-печати (только товары в наличии)"""
    from django.db.models import Sum, Q, F
    from django.db import connection

    # Более точный запрос через raw SQL (как в отчёте остатков)
    query = """
        SELECT 
            n.id as nom_id,
            n.title as title,
            COALESCE(i.title, 'шт') as izm,
            c.id as category_id,
            COALESCE(c.title, 'Без категории') as category_title,
            d.price,
            SUM(d.kolvo) as quantity
        FROM detail d
        INNER JOIN nom n ON d.id_nom = n.id
        LEFT JOIN izm i ON n.izm_id = i.id
        LEFT JOIN category c ON n.category_id = c.id
        INNER JOIN doc ON d.id_doc = doc.id
        WHERE doc.oper IN (1, 2, 4, 3, 5)
        GROUP BY n.id, n.title, i.title, c.id, c.title, d.price
        HAVING SUM(d.kolvo) > 0
        ORDER BY n.title, d.price
    """

    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()

    result = []
    for row in rows:
        result.append({
            'id': row[0],
            'title': row[1] or 'Без названия',
            'izm': row[2] or 'шт',
            'category_id': row[3],
            'category': row[4] or 'Без категории',
            'price': float(row[5]),
            'quantity': float(row[6])  # ← добавляем количество
        })

    return JsonResponse({'status': 'ok', 'data': result})


def print_selected_qr(request):
    """Печать QR-кодов для выбранных товаров"""
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        items = data.get('items', [])

        qr_items = []
        for item in items:
            qr_data = f"{item['id']}|{item['price']}"
            qr_items.append({
                'title': item['title'],
                'izm': item['izm'],
                'price': item['price'],
                'qr_data': qr_data
            })

        html = render_to_string('inventory/qr_print.html', {
            'qr_items': qr_items,
            'title': 'Выбранные товары'
        })
        return JsonResponse({'html': html})

    return JsonResponse({'error': 'Метод не поддерживается'}, status=405)