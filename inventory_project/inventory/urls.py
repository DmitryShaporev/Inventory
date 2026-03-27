from django.urls import path

from .views import base_views, spr_views, doc_views, report_views, qr_views

urlpatterns = [
    path('', base_views.index, name='index'),  # Главная страница с картинкой:)

    path('menu/<str:section>/', base_views.menu, name='menu'),  # Страница меню
    path('menu/spr/<str:section>/', spr_views.spr, name='spr'),
    path('menu/docs/<str:section>/', doc_views.docs, name='docs'),        # Добавь
    path('menu/reports/<str:section>/', report_views.reports, name='reports'), #


    path('spr/<str:section>/edit/<int:pk>', spr_views.edit_spr_row, name='edit_spr_row'), # Вызывает модальное окно для редактирования
    path('spr/<str:section>/<int:pk>/update/', spr_views.update_spr_row, name='update_spr_row'), # Сохраняет изменения в строке справочника
    path('spr/<str:section>/<int:pk>/delete/', spr_views.delete_spr_row, name='delete_spr_row'),
    path('spr/<str:section>/add/', spr_views.add_spr_row, name='add_spr_row'),
    path('obkt/add/', spr_views.add_obkt_row, name='add_obkt_row'),
    path('obkt/edit/<int:pk>/', spr_views.edit_obkt_row, name='edit_obkt_row'),
    path('obkt/update/', spr_views.update_obkt_row, name='update_obkt_row'),
    path('qr-simple/', qr_views.qr_simple, name='qr_simple'),
    path('nom/add/', spr_views.add_nom_row, name='add_nom_row'),
    path('nom/edit/<int:pk>', spr_views.edit_nom_row, name='edit_nom_row'),
    path('nom/update/', spr_views.update_nom_row, name='update_nom_row'),


    path('create_doc_inc/', doc_views.create_doc_inc, name='create_doc_inc'),
    path('nom/add-ajax/', spr_views.add_nom_ajax, name='add_nom_ajax'),
    path('postav/add-ajax/', spr_views.add_postav_ajax, name='add_postav_ajax'),

    path('docs/incom/save/', doc_views.save_incom_doc, name='save_incom_doc'),

]
