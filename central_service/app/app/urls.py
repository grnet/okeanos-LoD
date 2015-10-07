from django.conf.urls import include, url

# Base url for the central LoD Service.
# This means that every django application API will be nested under the '/api/'.
urlpatterns = [
    url(r'^api/', include('backend.urls')),
]
