from django.http import HttpResponse


def docs(request, section):
    """Временная заглушка для документов"""
    return HttpResponse(f"Страница документов: {section} (в разработке)")
