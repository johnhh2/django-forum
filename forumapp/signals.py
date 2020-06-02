import shutil
from django.db.models.signals import pre_delete 
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Channel, Thread, Comment

@receiver(pre_delete)
def delete_repo(sender, instance, **kwargs):
    if sender == User:

        channels = Channel.objects.filter(owner__id=instance.id)
        threads = Thread.objects.filter(owner__id=instance.id)
        comments = Comment.objects.filter(owner__id=instance.id)

        for lsting in channels:
            if lsting.moderators != '[]':
                moderators = json.loads(lsting.moderators)
                for username in moderators:
                    if User.objects.filter(username=username).exists():

                        lsting.owner = User.objects.get(username=username)
                        lsting.save()
                        break

            lsting.save()


        for group in threads, comments:
            for lsting in group:
                lsting.owner = None
                lsting.save()
