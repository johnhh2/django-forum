import json
from forumapp.models import Channel, UserSettings
from django import template

register = template.Library()

#Cyustom filter for Channels to make sure the current user isn't banned
@register.filter
def minus_bans(channel_list, username):
    channels = [c.channel_name for c in channel_list if str(username) not in json.loads(c.banned_users)]
    return Channel.objects.filter(channel_name__in=channels)

@register.filter
def is_favorite(channel_name, user):
    u = UserSettings.objects.filter(user=user)
    if u.exists():
        favs = u.get().favorites
        return str(channel_name) in json.loads(favs)
    return False
