from django.conf.urls import url, include
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    url(r'^webhook/', include('webhook.urls')),
]


urlpatterns = format_suffix_patterns(urlpatterns, allowed=['json', 'html'])
