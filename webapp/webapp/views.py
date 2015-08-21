# Create your views here.
from django.http import HttpResponse
from backend.models import *
from backend.queries import *
from django.template import Context, loader


def index(request):
    return HttpResponse("There should be some authentication here.")


def list_lambda_instances(request):
    #TODO
    # Make sure user passed authentication.
    # Display the lambda clusters
    clusters = get_Clusters()
    templates = list()
    for cluster in clusters:
        # Get the servers of each cluster.
        servers = get_Servers_by_Cluster(cluster.id)
        private_net = get_PrivateNetwork_by_Cluster(cluster.id)[0]
        template = loader.get_template('display-servers.html')
        context = Context({
            'cluster': cluster,
            'servers_list': servers,
            'private_net': private_net
        })
        templates.append(template.render(context))
    template = ''
    for t in templates:
        template = template + t
    return HttpResponse(template)
