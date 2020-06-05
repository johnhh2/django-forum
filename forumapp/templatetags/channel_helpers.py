import json
from forumapp.models import Channel
from django import template

register = template.Library()

#Create filter for Channels to make sure the current user isn't banned
@register.filter
def minus_bans(channel_list, username):
    channels = [c.channel_name for c in channel_list if username not in json.loads(c.banned_users)]
    return Channel.objects.filter(channel_name__in=channels)
