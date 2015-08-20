from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from backend.models import *
from backend.queries import *
from django.template import Context, loader


def index(request):
    return HttpResponse("Hello, lambda-user. You're at the lambda-service index.There should be some authentication here but who cares...")


def list_lambda_instances(request):
    #TODO
    # Make sure user passed authentication.

    # Display the lambda clusters
    clusters = get_Clusters()
    i = 1
    templates = list()
    for cluster in clusters:
        # Get the servers of each cluster.
        servers = get_Servers_by_Cluster(cluster.id)
        template = loader.get_template('display-servers.html')
        # Context is a normal Python dictionary whose keys can be accessed in the template index.html
        context = Context({
            'cluster' : cluster,
            'servers_list': servers
        })
        templates.append(template.render(context))
    template = ''
    for t in templates:
        template = template + t
    return HttpResponse(template)
