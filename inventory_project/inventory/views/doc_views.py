from datetime import datetime, date


from django.shortcuts import render, get_object_or_404





from ..models import Izm, Podraz, Fio, Category, Postav, Spis, Obct, Nom,Doc

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
    postav_list=Postav.objects.all()
    content={
        'postav_list':postav_list
    }
    return render(request,'inventory/create_doc_inc.html',context=content)