from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from backend.models import *
from backend.queries import *


def index(request):
    return HttpResponse("Hello, lambda-user. You're at the lambda-service index.There should be some authentication here but who cares...")


def list_lambda_instances(request):
    #TODO
    # Make sure user passed authentication.

    # Display the lambda clusters
    clusters = get_Clusters()
    c = 'clusters :'
    for cluster in clusters:
        # Get the servers of each cluster.
        c = c + str(cluster)
    return HttpResponse(c)
