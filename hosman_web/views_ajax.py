from django.http import JsonResponse
from .search import q_suggest
from .models import User

def validate_username(request):
    username = request.GET.get('username', None)
    data = {
        'is_taken': User.objects.filter(username__iexact=username).exists()
    }
    return JsonResponse(data)

def query_search(request):
    data = {
        'queryset': [q.string for q in q_suggest(request)]
    }
    return JsonResponse(data)
