from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter
from rest_framework.urlpatterns import format_suffix_patterns
from . import views

users_router = DefaultRouter()
users_router.register(r'users', views.UsersViewSet)
users_router.include_format_suffixes = False

lambda_instances_router = DefaultRouter()
lambda_instances_router.register(r'lambda_instances', views.LambdaInstanceView, base_name='lambda_instances')
lambda_instances_router.include_format_suffixes = False

lambda_applications_router = DefaultRouter()
lambda_applications_router.register(r'lambda_applications', views.LambdaApplicationView, base_name='lambda_applications')
lambda_applications_router.include_format_suffixes = False

urlpatterns = [
    url(r'^', include(users_router.urls)),
    url(r'^users/count/?$', views.LambdaUsersCounterView.as_view()),
    url(r'^lambda_instances/count/?$', views.LambdaInstanceCounterView.as_view(),
        name='count_lambda_instances'),
    url(r'^lambda_applications/count/?$', views.LambdaApplicationCounterView.as_view(),
        name='count_lambda_applications'),
    url(r'^', include(lambda_instances_router.urls)),
    url(r'^', include(lambda_applications_router.urls)),
]

urlpatterns = format_suffix_patterns(urlpatterns)