from django.shortcuts import redirect


class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Список путей, которые доступны без логина
        allowed_paths = ['/login/', '/admin/', '/static/', '/media/']

        # Если пользователь не авторизован
        if not request.user.is_authenticated:
            # Проверяем, не находится ли он на разрешённом пути
            for path in allowed_paths:
                if request.path.startswith(path):
                    break
            else:
                # Перенаправляем на логин
                return redirect('/login/')

        return self.get_response(request)