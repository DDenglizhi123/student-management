from urllib.parse import urlencode
from django import template
from django.http import QueryDict


register = template.Library()

@register.simple_tag
def search_url(request, **kwargs):
    query_params = QueryDict(request.META['QUERY_STRING'], mutable = True)
    for k,v in kwargs.items():
        if v is None:
            query_params.pop(k, None)
        else:
            query_params.setlist(k, [v])
    return  urlencode(query_params, doseq=True)