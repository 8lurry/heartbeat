from django.conf import settings
from django_hosts import patterns, host
host_patterns = patterns(
    '',
    #host(r'www', 'subdomains_tutorial.frontend_urls', name='www'),
    host(r'default', settings.ROOT_URLCONF, name='default'),
    #host(r'api', 'subdomains_tutorial.api_urls', name='api'),
)