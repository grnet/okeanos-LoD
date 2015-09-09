from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter
from rest_framework.urlpatterns import format_suffix_patterns
from . import views


# Create a router for lambda instances. This router will generate all the needed urls based on
# LambdaInstancesViewSet. Format suffixes are explicitly removed from the router. They will be
# added later to all urls.
lambda_instances_router = DefaultRouter()
lambda_instances_router.register(r'lambda-instances', views.LambdaInstanceViewSet)
lambda_instances_router.include_format_suffixes = False

urlpatterns = [
    url(r'^authenticate/?$', views.authenticate),
    url(r'^apps/?$', views.Applications.as_view()),
    url(r'^create_lambda_instance/?$', views.CreateLambdaInstance.as_view(),
        name='create_lambda_instance'),
    url(r'^', include(lambda_instances_router.urls))
]

urlpatterns = format_suffix_patterns(urlpatterns)
