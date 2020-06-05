import json
from django.contrib.auth.models import User
from forumapp.models import Channel, Thread, Comment
from django import template

register = template.Library()

#Custom filter for users to get a queryset of their channels, except for ones the current user is banned from
@register.filter
def get_owned_channels_minus_banned(owner, check):
    channels = []
    for c in Channel.objects.filter(owner=owner):
        if check.get_username() not in c.banned_users:
            channels.append(c.channel_name)
    return Channel.objects.filter(channel_name__in=channels)

#Custom filter for users to get a queryset of their channels, but only ones the current user is banned from
@register.filter
def get_owned_channels_only_banned(owner, check):
    channels = []
    for c in Channel.objects.filter(owner=owner):
        if check.get_username() in json.loads(c.banned_users):
            channels.append(c.channel_name)
    return Channel.objects.filter(channel_name__in=channels)

#Create filter for users to get a queryset of all the channels they moderate
@register.filter
def get_moderated_channels_minus_banned(moderator, check):
    channels = []
    for c in Channel.objects.filter(moderators__contains=moderator.get_username):
        if check.get_username not in json.loads(c.banned_users):
            channels.append(c.channel_name)
    return Channel.objects.filter(channel_name__in=channels)
