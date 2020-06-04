from django.contrib.auth.models import User
from forumapp.models import Channel, Thread, Comment
from django import template

register = template.Library()

#Create filter for users to get a queryset of all the channels they own
@register.filter
def get_owned_channels(user):
    return Channel.objects.filter(owner=user)

#Create filter for users to get a queryset of all the channels they moderate
@register.filter
def get_moderated_channels(user):
    return Channel.objects.filter(moderators__contains="," + user.username + ",")
