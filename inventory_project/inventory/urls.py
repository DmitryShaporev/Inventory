from django.urls import path
from django.contrib.auth import views as auth_views
from .views import base_views, spr_views, doc_views, report_views, qr_views

urlpatterns = [
    path('', base_views.index, name='index'),  # Главная страница с картинкой:)

    path('menu/<str:section>/', base_views.menu, name='menu'),  # Страница меню
    path('menu/spr/<str:section>/', spr_views.spr, name='spr'),
    path('menu/docs/<str:section>/', doc_views.docs, name='docs'),  # Добавь
    path('menu/reports/<str:section>/', report_views.reports, name='reports'),  #

    path('spr/<str:section>/edit/<int:pk>', spr_views.edit_spr_row, name='edit_spr_row'),
    # Вызывает модальное окно для редактирования
    path('spr/<str:section>/<int:pk>/update/', spr_views.update_spr_row, name='update_spr_row'),
    # Сохраняет изменения в строке справочника
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
    path('docs/incom/update/<int:pk>/', doc_views.update_incom_doc, name='update_incom_doc'),
    path('docs/incom/edit/<int:doc_id>/', doc_views.edit_incom_doc, name='edit_incom_doc'),
    path('docs/incom/delete/<int:doc_id>/', doc_views.delete_incom_doc, name='delete_incom_doc'),

    # Документы перемещения
    path('create_doc_move/', doc_views.create_move_doc, name='create_doc_move'),
    path('docs/move/save/', doc_views.save_move_doc, name='save_move_doc'),
    path('docs/move/update/<int:doc_id>/', doc_views.update_move_doc, name='update_move_doc'),
    path('docs/move/edit/<int:doc_id>/', doc_views.edit_move_doc, name='edit_move_doc'),

    # API для остатков
    path('api/remains/', doc_views.api_remains, name='api_remains'),
    path('docs/move/delete/<int:doc_id>/', doc_views.delete_move_doc, name='delete_move_doc'),
    path('qr/print-from-doc/', qr_views.print_qr_from_doc, name='print_qr_from_doc'),
path('qr-selector/', qr_views.qr_selector, name='qr_selector'),
path('api/qr-items/', qr_views.api_qr_items, name='api_qr_items'),
path('qr/print-selected/', qr_views.print_selected_qr, name='print_selected_qr'),
path('api/nom-by-id/<int:nom_id>/', spr_views.get_nom_by_id, name='get_nom_by_id'),
    # ========== ОТЧЕТЫ ==========
    # Сначала конкретные отчеты (более специфичные)
    path('reports/incom/', report_views.incom_report, name='reports_incom'),
    path('reports/incom/excel/', report_views.incom_report_excel, name='reports_incom_excel'),
    path('reports/move/', report_views.move_report, name='reports_move'),
    path('reports/move/excel/', report_views.move_report_excel, name='reports_move_excel'),
    path('reports/remain/', report_views.remain_report, name='reports_remain'),
    path('reports/remain/excel/', report_views.remain_report_excel, name='reports_remain_excel'),
# Карточка товара
    path('reports/nom-card/<int:nom_id>/', report_views.nom_card, name='nom_card'),

    path('docs/incom/view/<int:doc_id>/', doc_views.view_incom_doc, name='view_incom_doc'),
    path('docs/move/view/<int:doc_id>/', doc_views.view_move_doc, name='view_move_doc'),

# Отчет по поставщикам
    path('reports/suppliers/', report_views.suppliers_report, name='reports_suppliers'),
    path('reports/suppliers/<int:supplier_id>/', report_views.supplier_details, name='supplier_details'),
    path('reports/suppliers/excel/', report_views.suppliers_report_excel, name='reports_suppliers_excel'),


# Отчет по объектам
path('reports/objects/', report_views.objects_report, name='reports_objects'),
path('reports/objects/excel/', report_views.objects_report_excel, name='reports_objects_excel'),
path('reports/objects/<int:object_id>/', report_views.object_details, name='object_details'),
path('reports/objects/<int:object_id>/excel/', report_views.object_details_excel, name='object_details_excel'),

# Отчет по подразделениям
path('reports/departments/', report_views.departments_report, name='reports_departments'),
path('reports/departments/excel/', report_views.departments_report_excel, name='reports_departments_excel'),
path('reports/departments/<int:department_id>/', report_views.department_details, name='department_details'),
path('reports/departments/<int:department_id>/excel/', report_views.department_details_excel, name='department_details_excel'),


# Отчет по подотчетным лицам
path('reports/fio/', report_views.fio_report, name='reports_fio'),
path('reports/fio/excel/', report_views.fio_report_excel, name='reports_fio_excel'),
path('reports/fio/<int:fio_id>/', report_views.fio_details, name='fio_details'),
path('reports/fio/<int:fio_id>/excel/', report_views.fio_details_excel, name='fio_details_excel'),

# Отчет по категориям
path('reports/categories/', report_views.categories_report, name='reports_categories'),
path('reports/categories/excel/', report_views.categories_report_excel, name='reports_categories_excel'),
path('reports/categories/income/<int:category_id>/', report_views.category_income_details, name='category_income_details'),
path('reports/categories/income/<int:category_id>/excel/', report_views.category_income_details_excel, name='category_income_details_excel'),
path('reports/categories/outcome/<int:category_id>/', report_views.category_outcome_details, name='category_outcome_details'),
path('reports/categories/outcome/<int:category_id>/excel/', report_views.category_outcome_details_excel, name='category_outcome_details_excel'),

path('reports/top10/', report_views.top10_report, name='reports_top10'),
path('reports/top10/data/', report_views.top10_report_data, name='reports_top10_data'),

    # Потом общее меню отчетов (должно быть последним!)
    path('reports/<str:section>/', report_views.reports_menu, name='reports'),


path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),

]


