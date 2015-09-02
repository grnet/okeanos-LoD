"""webapp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from . import views


urlpatterns = [
    url(r'^authenticate/?$', views.authenticate),
    url(r'^user_files/?$', views.ProjectFileList.as_view()),
    url(r'^lambda-instances/?$', views.list_lambda_instances, name='list_lambda_instances'),
    url(r'^lambda-instances/(?P<instance_uuid>[0-9]+)/?$', views.lambda_instance_details,
        name='lambda_instance_details'),
    url(r'^lambda-instances/(?P<instance_uuid>[0-9]+)/status/?$', views.lambda_instance_status,
        name='lambda_instance_status'),
    url(r'^lambda-instances/(?P<instance_uuid>[0-9]+)/start/?$', views.lambda_instance_start,
        name='lambda_instance_start'),
    url(r'^lambda-instances/(?P<instance_uuid>[0-9]+)/stop/?$', views.lambda_instance_stop,
        name='lambda_instance_stop'),
    url(r'^lambda-instances/(?P<instance_uuid>[0-9]+)/destroy/?$', views.lambda_instance_destroy,
        name='lambda_instance_destroy'),
    url(r'^create_lambda_instance/?$', views.CreateLambdaInstance.as_view(),
        name='create_lambda_instance'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
