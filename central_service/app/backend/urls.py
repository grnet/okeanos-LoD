from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter
from rest_framework.urlpatterns import format_suffix_patterns
from . import views

users_router = DefaultRouter()
users_router.register(r'users', views.UsersViewSet)
users_router.include_format_suffixes = False

lambda_instances_router = DefaultRouter()
lambda_instances_router.register(r'lambda_instance', views.LambdaInstanceView)
lambda_instances_router.include_format_suffixes = False

urlpatterns = [
    url(r'^', include(users_router.urls)),
    url(r'^', include(lambda_instances_router.urls)),
]

urlpatterns = format_suffix_patterns(urlpatterns)