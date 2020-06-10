import json
from django import template
from forumapp.models import Channel, Thread, Comment

register = template.Library()

#Custom filter for threads to return the channel they belong to's description
@register.filter
def description(channel_name):
    channel = Channel.objects.filter(channel_name=channel_name)

    if channel.exists():
        return channel.get().description
    else:
        return ''
