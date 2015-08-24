import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from kamaki.clients.utils import https
from kamaki.clients import ClientError
from kamaki import defaults
from kamaki.clients import astakos


def patch_certs(cert_path=None):
    if not defaults.CACERTS_DEFAULT_PATH:
        if cert_path:
            https.patch_with_certs(cert_path)
        else:
            try:
                from ssl import get_default_verify_paths
                cert_path = get_default_verify_paths().cafile or \
                    get_default_verify_paths().openssl_cafile
            except:
                pass

            if cert_path:
                https.patch_with_certs(cert_path)
            else:
                logger.warn("COULD NOT FIND ANY CERTIFICATES, PLEASE SET THEM IN YOUR "
                            ".kamakirc global section, option ca_certs")
                https.patch_ignore_ssl()


def check_auth_token(auth_token, auth_url=None):
    if not auth_url:
        auth_url = "https://accounts.okeanos.grnet.gr/identity/v2.0"
    patch_certs()
    cl = astakos.AstakosClient(auth_url, auth_token)
    try:
        user_info = cl.authenticate()
    except ClientError as ex:
        if ex.message == 'UNAUTHORIZED':
            return False, ex.details
        else:
            raise ex
    return True, user_info
