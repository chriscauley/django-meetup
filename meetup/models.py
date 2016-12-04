from __future__ import unicode_literals

from django.conf import settings
from django.db import models
from django.utils import timezone
import json, requests, jsonfield, pytz

BASE_URL = "https://api.meetup.com/{url}?sign=true&{urlparams}&{extra}&key="+settings.MEETUP_KEY

class Group(models.Model):
  name = models.CharField(max_length=255)
  url = models.CharField(max_length=255,unique=True)
  data = jsonfield.JSONField(default=dict)
  @classmethod
  def get_or_create(cls,url,force=False):
    try:
      if not force:
        return cls.objects.get(url=url),False
    except cls.DoesNotExist:
      pass
    kwargs = {
      'url': url,
      'urlparams': "",
      'extra': ''
    }
    r = requests.get(BASE_URL.format(**kwargs))
    data = json.loads(r.text)
    obj,new = cls.objects.get_or_create(name=data['name'],url=url)
    obj.data = data
    obj.save()
    obj.update()
    return obj,new
  def update(self):
    kwargs = {
      'url': '2/events',
      'urlparams': 'group_urlname=%s&status=%s'%(self.url,'upcoming%2Cpast')
    }
    page = 100
    for i in range(10):
      kwargs['extra'] = "offset=%s&page=%s"%(i,page)
      r = requests.get(BASE_URL.format(**kwargs))
      data = json.loads(r.text)
      tz = pytz.timezone(self.data['timezone'])
      for e in data['results']:
        dt = timezone.datetime.fromtimestamp(e['time']/1000,tz)
        defaults = {'datetime': dt, 'data': e, 'name': e['name']}
        event,new = Event.objects.get_or_create(meetup_id=e['id'],group=self,defaults=defaults)
        event.datetime = dt
        event.data = e
        event.save()

class Event(models.Model):
  meetup_id = models.CharField(max_length=32,unique=True)
  name = models.CharField(max_length=255)
  group = models.ForeignKey(Group)
  data = jsonfield.JSONField(default=dict)
  datetime = models.DateTimeField()
  class Meta:
    ordering = ("-datetime",)
