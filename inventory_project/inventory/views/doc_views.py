from datetime import datetime, date
import json
from django.http import JsonResponse
from django.db import transaction
from django.shortcuts import render, get_object_or_404
from ..models import Izm, Podraz, Fio, Category, Postav, Spis, Obct, Nom,Doc,Detail,Manage

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
    postav_list=Postav.objects.all().order_by('title')
    nom_list=Nom.objects.select_related('izm').order_by('title')
    izm_list=Izm.objects.all()
    category_list=Category.objects.all()
    content={
        'postav_list':postav_list,
        'nom_list':nom_list,
        'category_list':category_list,
        'izm_list':izm_list
    }
    return render(request,'inventory/create_doc_inc.html',context=content)


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