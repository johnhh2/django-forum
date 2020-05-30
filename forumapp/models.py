import datetime
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User

class Channel(models.Model):
    channel_name = models.SlugField(max_length=30, primary_key=True)

    owner = models.ForeignKey(User, to_field="username", null=False)
    pub_date = models.DateTimeField('date published')

    def __str__(self):
        return self.channel_name

# Store thread_id as primary key
class Thread(models.Model):
    thread_id = models.AutoField(primary_key=True)
    channel_name = models.ForeignKey(Channel, to_field="channel_name")
    owner = models.ForeignKey(User, to_field="username", null=False)
    thread_name = models.CharField(max_length=90)
    pub_date = models.DateTimeField('date published')
    description = models.CharField(max_length=150)

    def __str__(self):
        return self.thread_name

# Primary keys are thread_name and comment_id where comment_id starts at 1 for every new thread
class Comment(models.Model):
    comment_id = models.AutoField(primary_key=True)
    thread_id = models.ForeignKey(Thread, to_field="thread_id")
    pub_date = models.DateTimeField('date published')
    text = models.CharField(max_length=250)
    owner = models.ForeignKey(User, to_field="username", null=False)

    def __str__(self):
        return self.text

    def is_recent(self):
        now = timezone.now()
        return timezone.now() - datetime.timedelta(days=1) <= self.pub_date <= now

    is_recent.admin_order_field = 'pub_date'
    is_recent.boolean = True
    is_recent.short_description = 'Published recently?'
