#!/usr/bin/env python
# -*- coding: utf-8 -*-

from kamaki.clients import astakos, pithos, cyclades, image
from kamaki.clients.utils import https

URL = "https://accounts.okeanos.grnet.gr/identity/v2.0"
TOKEN = "xgOHh5OgWf79BNyPZl0Fk0jb02twr8Bvl-UQzN9ABGE"

https.patch_with_certs('/etc/ssl/certs/ca-certificates.crt')

identity_client = astakos.AstakosClient(URL, TOKEN)

pithosURL = identity_client.get_endpoint_url(pithos.PithosClient.service_type)
storage_client = pithos.PithosClient(pithosURL, TOKEN)
storage_client.account = identity_client.user_info['id']
storage_client.container = 'pithos'

imageURL = identity_client.get_endpoint_url(image.ImageClient.service_type)
image_client = image.ImageClient(imageURL, TOKEN)

computeURL = identity_client.get_endpoint_url(
    cyclades.CycladesComputeClient.service_type)
compute_client = cyclades.CycladesComputeClient(computeURL, TOKEN)

networkURL = identity_client.get_endpoint_url(
    cyclades.CycladesNetworkClient.service_type)
network_client = cyclades.CycladesNetworkClient(networkURL, TOKEN)

volumeURL = identity_client.get_endpoint_url(
    cyclades.CycladesBlockStorageClient.service_type)
volume_client = cyclades.CycladesBlockStorageClient(volumeURL, TOKEN)


'''
Creates a virtual private network with that name
'''
def create_vpn(network_name):
    #create vpn with custom type and the name given as argument
    vpn = network_client.create_network(
        type=cyclades.CycladesNetworkClient.network_types[1],
        name=network_name)
    if vpn != None:
        return True
    return False


'''
Destroys the vpn with the given id
'''
def destroy_vpn(id):
    network_client.delete_network(id)
