from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from ninja.router import Router

router = Router()


@router.get("/csrf", auth=None)
@ensure_csrf_cookie
@csrf_exempt
def csrf(request):
    return HttpResponse()
