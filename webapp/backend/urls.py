from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter
from rest_framework.urlpatterns import format_suffix_patterns
from . import views


# Create a router for lambda instances. This router will generate all the needed urls based on
# LambdaInstanceViewSet. Format suffixes is explicitly removed from the router. It will be
# added later to all urls.
lambda_instances_router = DefaultRouter()
lambda_instances_router.register(r'lambda-instances', views.LambdaInstanceViewSet)
lambda_instances_router.include_format_suffixes = False

# Create a router for applications. This router will generate all the needed urls based on
# ApplicationViewSet. Format suffixes is explicitly removed from the router. It will be added
# later to all urls.
application_router = DefaultRouter()
application_router.register(r'apps', views.ApplicationViewSet)
application_router.include_format_suffixes = False

urlpatterns = [
    url(r'^authenticate/?$', views.authenticate),
    url(r'^create_lambda_instance/?$', views.CreateLambdaInstance.as_view(),
        name='create_lambda_instance'),
    url(r'^', include(application_router.urls)),
    url(r'^', include(lambda_instances_router.urls))
]

urlpatterns = format_suffix_patterns(urlpatterns)
