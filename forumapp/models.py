import datetime
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class Channel(models.Model):
    channel_name = models.SlugField(max_length=30, primary_key=True)

    owner = models.ForeignKey(User, to_field="username", null=False)
    pub_date = models.DateTimeField('date published')

    def __str__(self):
        return self.channel_name

# Store thread_id as primary key
class Thread(models.Model):
    thread_id = models.IntegerField(default=0)
    channel = models.ForeignKey(Channel)

    thread_name = models.CharField(max_length=90)
    description = models.CharField(max_length=150)

    owner = models.ForeignKey(User, to_field="username", null=False)
    pub_date = models.DateTimeField('date published')

    class Meta:
        unique_together = (('channel', 'thread_id'))

    def __str__(self):
        return self.thread_name

    def validate_unique(self, exclude=None):
        threads = Thread.objects.filter(channel__channel_name=self.channel.channel_name)
        if self._state.adding and threads.filter(thread_id=self.thread_id).exists():
            raise ValidationError('Name must be unique per site')

    def save(self, *args, **kwargs):

        if self._state.adding:
            last_id = Thread.objects.filter(channel__channel_name=self.channel.channel_name).aggregate(largest=models.Max('thread_id'))['largest']

            if last_id is not None:
                self.thread_id = last_id + 1


        super(Thread, self).save(*args, **kwargs)

# Primary keys are thread_name and comment_id where comment_id starts at 1 for every new thread
class Comment(models.Model):
    comment_id = models.IntegerField(default=0)
    thread = models.ForeignKey(Thread)

    text = models.CharField(max_length=250)

    pub_date = models.DateTimeField('date published')
    owner = models.ForeignKey(User, to_field="username", null=False)

    class Meta:
        unique_together = (('thread', 'comment_id'))

    def __str__(self):
        return self.text

    def validate_unique(self, exclude=None):
        channel_comments = Comment.objects.filter(thread__channel__channel_name=self.thread.channel.channel_name)
        comments = channel_comments.filter(thread__thread_id=self.thread_id)
        if comments.filter(comment_id=self.comment_id).exists():
            raise ValidationError('Name must be unique per site')

    def save(self, *args, **kwargs):

        if self._state.adding:
            comments = Comment.objects.filter(thread__channel__channel_name=kwargs.get('channel'), thread__thread_id=kwargs.get('thread'))

            last_id = comments.aggregate(largest=models.Max('comment_id'))['largest']

            if last_id is not None:
                self.comment_id = last_id + 1

        super(Comment, self).save(*args, **kwargs)

    def is_recent(self):
        now = timezone.now()
        return timezone.now() - datetime.timedelta(days=1) <= self.pub_date <= now

    is_recent.admin_order_field = 'pub_date'
    is_recent.boolean = True
    is_recent.short_description = 'Published recently?'
