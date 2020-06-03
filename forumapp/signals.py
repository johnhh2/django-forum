import json
from django.dispatch import receiver
from django.db.models.signals import post_delete 
from django.contrib.auth.models import User
from .models import Channel, Thread, Comment

#When we delete a user, reassign or delete channels without owners
@receiver(post_delete, sender=User)
def delete_repo(sender, instance, **kwargs):

    # Reassign owner of channel, otherwise delete it and anything in it
    channels = Channel.objects.filter(owner=None)

    for chan in channels:
        moderators = json.loads(chan.moderators)
        for username in moderators:
            if User.objects.filter(username=username).exists():

                chan.owner = User.objects.get(username=username)
                chan.save()
                print(username)
                break
        else:
            chan.delete()
