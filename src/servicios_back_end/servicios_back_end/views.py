from django.http import JsonResponse

def cursos_temporal(request):
    responseData = {
        'id': 4,
        'name': 'Test Response',
        'roles' : ['Admin','User']
    }
    return JsonResponse(responseData)
