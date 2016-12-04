from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse

from .models import Group

def view_group(request,url):
  group,new = Group.get_or_create(url=url,force=request.GET.get('force',False))
  search_kwargs = {}
  if 'q' in request.GET:
    search_kwargs['name__icontains'] = request.GET['q']
  events = group.event_set.filter(**search_kwargs)
  values = {'group': group,'events': events}
  return TemplateResponse(request,"view_group.html",values)
