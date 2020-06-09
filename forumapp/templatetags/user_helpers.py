import json
from django.contrib.auth.models import User
from forumapp.models import UserSettings, Channel, Thread, Comment
from django import template
from django.db.models import Q
register = template.Library()

@register.filter
def get_owned_channels(user):
    return Channel.objects.filter(owner=user)

@register.filter
def get_owned_channels_moderated_by_user(owner, user):
    return Channel.objects.filter(owner=owner, moderators__contains='"'+user.get_username()+'"') 
    

@register.filter
def get_owned_channels_not_moderated_by_user(owner, user):
    channels = Channel.objects.filter(Q(owner=owner), ~Q(moderators__contains='"'+user.get_username()+'"'))
    
    # exclude banned users
    return channels.filter(~Q(banned_users__contains='"'+user.get_username()+'"'))
@register.filter
def is_banned_from(user, channel_name):
    channel = Channel.objects.filter(channel_name=channel_name)
    
    #see if user is in list of banned users
    if channel.exists():
        channel = channel.get()
        return user.get_username() in json.loads(channel.banned_users)
    
    else:
        return False

# get owned channels that user is not banned from assuming calling user has permissions
@register.filter
def get_moderated_channels_minus_banned(moderator, user):
    channels = Channel.objects.filter(moderators__contains='"'+moderator.get_username()+'"') | \
            Channel.objects.filter(owner=moderator)
    
    # exclude banned users
    return channels.filter(~Q(banned_users__contains='"'+user.get_username()+'"'))

# get owned channels that user is banned from assuming calling user has permissions
@register.filter
def get_moderated_channels_only_banned(moderator, user):
    channels = Channel.objects.filter(moderators__contains='"'+moderator.get_username()+'"') | \
            Channel.objects.filter(owner=moderator)

    # only include banned users
    return channels.filter(banned_users__contains='"'+user.get_username()+'"')

@register.filter
def get_bio(user):
    settings = UserSettings.objects.filter(user=user)

    if settings.exists():
        return settings.get().bio
    else:    
        return UserSettings.objects.create(user=user).bio
