from apps.fyle.helpers import get_fyle_orgs
from apps.users.helpers import get_cluster_domain_and_refresh_token


def get_fyle_orgs_view(user):
    cluster_domain, refresh_token = get_cluster_domain_and_refresh_token(user)
    fyle_orgs = get_fyle_orgs(refresh_token, cluster_domain)
    return fyle_orgs
