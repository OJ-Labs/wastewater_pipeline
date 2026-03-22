from .models import Topic

def topics(request):
    return {
        "all_topics": Topic.objects.all().order_by('name')
    }
