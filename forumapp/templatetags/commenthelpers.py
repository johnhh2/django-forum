from django import template
from forumapp.models import Comment

register = template.Library()

#Create filter for comments to check if their publish date is within 24 hours before now.
@register.filter
def isrecent(comment):
    return comment.is_recent()
