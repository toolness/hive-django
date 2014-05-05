import binascii
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth import authenticate, login
from django.conf import settings

def send_digest(request):
    html = request.POST.get('html')
    if not html:
        return HttpResponse(status=400, reason='Bad Request')
    
    return HttpResponse('thanks')

@csrf_exempt
@require_POST
def send(request):
    if (not hasattr(settings, 'MINIGROUP_DIGESTIF_USERPASS') or
        not settings.MINIGROUP_DIGESTIF_USERPASS):
        return HttpResponse(status=501, reason='Not Implemented')
    if request.META.has_key('HTTP_AUTHORIZATION'):
        try:
            authmeth, auth = request.META['HTTP_AUTHORIZATION'].split(' ', 1)
            if authmeth.lower() == 'basic':
                auth = auth.strip().decode('base64')
                if auth == settings.MINIGROUP_DIGESTIF_USERPASS:
                    return send_digest(request)
        except ValueError:
            pass
        except binascii.Error:
            pass

    response = HttpResponse()
    response.status_code = 401
    response['WWW-Authenticate'] = 'Basic realm="minigroup_digestif"'
    return response
