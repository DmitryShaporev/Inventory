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
    """API для получения товаров с ценами для QR-печати"""
    # Получаем уникальные сочетания товар + цена
    items = Detail.objects.filter(
        Q(id_doc__oper=2) | Q(id_doc__oper=1)  # Приход и начальные остатки
    ).values(
        'id_nom',
        'id_nom__title',
        'id_nom__izm__title',
        'id_nom__category__title',
        'id_nom__category_id',
        'price'
    ).annotate(
        total_quantity=Sum('kolvo')
    ).filter(total_quantity__gt=0)

    result = []
    for item in items:
        result.append({
            'id': item['id_nom'],
            'title': item['id_nom__title'],
            'izm': item['id_nom__izm__title'] or 'шт',
            'category': item['id_nom__category__title'] or 'Без категории',
            'category_id': item['id_nom__category_id'],
            'price': float(item['price']),
            'quantity': float(item['total_quantity'])
        })

    # Сортируем по наименованию
    result.sort(key=lambda x: x['title'])

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