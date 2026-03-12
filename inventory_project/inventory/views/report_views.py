from django.http import HttpResponse


def reports(request, section):
    """Временная заглушка для отчетов"""
    return HttpResponse(f"Страница отчетов: {section} (в разработке)")