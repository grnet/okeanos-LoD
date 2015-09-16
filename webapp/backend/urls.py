from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter
from rest_framework.urlpatterns import format_suffix_patterns
from . import views


lambda_instances_list = views.LambdaInstanceViewSet.as_view({
    'get': 'list'
})

lambda_instances_interact = views.LambdaInstanceViewSet.as_view({
    'get': 'retrieve',
    'post': 'action',
    'delete': 'destroy'
})

# Create a router for applications. This router will generate all the needed urls based on
# ApplicationViewSet. Format suffixes is explicitly removed from the router. It will be added
# later to all urls.
application_router = DefaultRouter()
application_router.register(r'apps', views.ApplicationViewSet)
application_router.include_format_suffixes = False

urlpatterns = [
    url(r'^authenticate/?$', views.authenticate),
    url(r'^lambda-instance/?$', views.CreateLambdaInstance.as_view(),
        name='create lambda instance'),
    url(r'^lambda-instances/?$', lambda_instances_list, name="lambda instances list"),
    url(r'^lambda-instances/(?P<uuid>[^/.]+)/?$', lambda_instances_interact,
        name="lambda instances interact"),
    url(r'^', include(application_router.urls))
]

urlpatterns = format_suffix_patterns(urlpatterns)
