from datetime import datetime, date
import json
from django.http import JsonResponse
from django.db import transaction
from django.shortcuts import render, get_object_or_404
from ..models import Izm, Podraz, Fio, Category, Postav, Spis, Obct, Nom,Doc,Detail,Manage
from django.db.models.deletion import ProtectedError
from django.http import JsonResponse
from django.views.decorators.http import require_POST



def parse_decimal(value):
    """Преобразует строку с запятой в число с плавающей точкой"""
    if not value:
        return 0.0
    # Заменяем запятую на точку
    value = str(value).replace(',', '.')
    # Удаляем пробелы
    value = value.replace(' ', '')
    try:
        return float(value)
    except ValueError:
        return 0.0


def docs(request, section):

    if section == 'incom':
        title = 'Входящие документы'
        data = Doc.objects.filter(oper=2).select_related('postav').order_by('-datadoc')

    elif section == 'move':
        title = 'Документы по передаче ТМЦ'
        data = Doc.objects.filter(oper=3).select_related('fio', 'obct', 'obct__idpodraz', 'postav').order_by('-datadoc')
    elif section == 'ret':
        title = 'Документы на возврат ТМЦ'
        data = Doc.objects.filter(oper=4).select_related('fio', 'obct', 'obct__idpodraz', 'postav').order_by('-datadoc')
    else:
        title ='Документы по списанию ТМЦ'
        data = Doc.objects.filter(oper=4).select_related('fio', 'obct', 'obct__idpodraz', 'postav').order_by('-datadoc')

    context={'title':title,
             'data': data,
             'section': section}
    return render(request, 'inventory/doc_journal.html',context)


def create_doc_inc(request):
    """Создание нового приходного документа"""
    from datetime import date

    context = {
        'today': date.today(),
        'postav_list': Postav.objects.all().order_by('title'),
        'nom_list': Nom.objects.select_related('izm').all().order_by('title'),
        'izm_list': Izm.objects.all().order_by('title'),
        'category_list': Category.objects.all().order_by('title'),
        'is_edit': False,  # ← флаг для нового документа
    }
    return render(request, 'inventory/incom_doc_form.html', context)

def save_incom_doc(request):
    """Сохранение приходного документа"""

    manage = Manage.objects.first()
    if not manage:
        return JsonResponse({'error': 'Не настроены параметры склада (Manage)'}, status=400)

    if request.method != 'POST':
        return JsonResponse({'error': 'Метод не поддерживается'}, status=405)

    try:
        data = json.loads(request.body)

        with transaction.atomic():
            doc = Doc.objects.create(
                nomer=data['doc']['nomer'],
                datadoc=data['doc']['datadoc'],
                postav_id=data['doc']['postav_id'],
                fio=manage.fio,
                obct=manage.obkt,
                oper=2,
                total=0
            )

            total = 0
            for item in data['items']:
                # Преобразуем значения с запятой в числа
                kolvo = parse_decimal(item['kolvo'])
                price = parse_decimal(item['price'])
                vat_rate = parse_decimal(item['vat_rate'])
                cost_without_vat = parse_decimal(item['cost_without_vat'])
                vat_amount = parse_decimal(item['vat_amount'])
                total_with_vat = parse_decimal(item['total_with_vat'])

                detail = Detail.objects.create(
                    id_doc=doc,
                    id_nom_id=item['nom_id'],
                    kolvo=kolvo,
                    price=price,
                    cost=cost_without_vat,
                    vat_rate=vat_rate,
                    vat_amount=vat_amount,
                    total_with_vat=total_with_vat,
                    oper=2
                )

                total += total_with_vat

            doc.total = total
            doc.save()

        return JsonResponse({'status': 'ok'})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


def edit_incom_doc(request, doc_id):
    """Редактирование приходного документа"""
    from datetime import date

    # Получаем документ
    doc = get_object_or_404(Doc, id=doc_id, oper=2)

    # Получаем строки документа
    details = Detail.objects.filter(id_doc=doc).select_related('id_nom', 'id_nom__izm')

    context = {
        'doc': doc,
        'details': details,
        'today': date.today(),
        'postav_list': Postav.objects.all().order_by('title'),
        'nom_list': Nom.objects.select_related('izm').all().order_by('title'),
        'izm_list': Izm.objects.all().order_by('title'),
        'category_list': Category.objects.all().order_by('title'),
        'is_edit': True,  # флаг для шаблона, что это редактирование
    }
    return render(request, 'inventory/incom_doc_form.html', context)


def update_incom_doc(request, pk):
    """Обновление приходного документа"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Метод не поддерживается'}, status=405)

    try:
        data = json.loads(request.body)

        with transaction.atomic():
            # Получаем существующий документ
            doc = Doc.objects.get(id=pk, oper=2)

            # Обновляем шапку
            doc.nomer = data['doc']['nomer']
            doc.datadoc = data['doc']['datadoc']
            doc.postav_id = data['doc']['postav_id']

            # Удаляем старые строки
            doc.details.all().delete()

            # Создаем новые строки
            total = 0
            for item in data['items']:
                kolvo = parse_decimal(item['kolvo'])
                price = parse_decimal(item['price'])
                vat_rate = parse_decimal(item['vat_rate'])
                cost_without_vat = parse_decimal(item['cost_without_vat'])
                vat_amount = parse_decimal(item['vat_amount'])
                total_with_vat = parse_decimal(item['total_with_vat'])

                Detail.objects.create(
                    id_doc=doc,
                    id_nom_id=item['nom_id'],
                    kolvo=kolvo,
                    price=price,
                    cost=cost_without_vat,
                    vat_rate=vat_rate,
                    vat_amount=vat_amount,
                    total_with_vat=total_with_vat,
                    oper=2
                )
                total += total_with_vat

            doc.total = total
            doc.save()

        return JsonResponse({'status': 'ok'})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)





@require_POST
def delete_incom_doc(request, doc_id):
    """Удаление приходного документа"""
    try:
        doc = get_object_or_404(Doc, id=doc_id, oper=2)

        # Проверяем, есть ли строки
        if doc.details.exists():
            return JsonResponse({
                'error': f'❌ Нельзя удалить документ №{doc.nomer} — есть строки!'
            }, status=400)

        doc.delete()
        return JsonResponse({'status': 'ok'})

    except ProtectedError:
        return JsonResponse({
            'error': f'❌ Нельзя удалить документ — есть связанные записи!'
        }, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)