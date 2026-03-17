from django.shortcuts import render
def qr_simple(request):
    """Простая страница для теста QR-кода"""
    return render(request, 'inventory/qr_simple.html')