import datetime
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

# One-to-one with User
class UserSettings(models.Model):
    user = models.OneToOneField(User, primary_key=True)
    favorites = models.TextField(default='["General"]')
    bio = models.TextField(max_length=250, default='Hello world')

    def __str__(self):
        return user.get_username

# Store channel_name as primary_key
class Channel(models.Model):
    channel_name = models.SlugField(max_length=30, primary_key=True)
    moderators = models.TextField(default='[]')
    description = models.CharField(max_length=250, default='')
    owner = models.ForeignKey(User, to_field="username", null=True, on_delete=models.SET_NULL)
    pub_date = models.DateTimeField('date published', default=timezone.now)
    recent_date = models.DateTimeField('date used', default=timezone.now)
    banned_users = models.TextField(default='[]')

    class Meta:
        ordering = ['-recent_date']

    def __str__(self):
        return self.channel_name.replace('-', ' ')

    def is_recent(self):
        now = timezone.now()
        return timezone.now() - datetime.timedelta(days=1) <= self.pub_date <= now

    is_recent.admin_order_field = 'pub_date'
    is_recent.boolean = True
    is_recent.short_description = 'Published recently?'

# Store channel and thread_id as primary keys
class Thread(models.Model):
    thread_id = models.IntegerField(default=0)
    channel = models.ForeignKey(Channel)

    thread_name = models.CharField(max_length=90)
    description = models.CharField(max_length=150)

    owner = models.ForeignKey(User, to_field="username", null=True, on_delete=models.SET_NULL)
    pub_date = models.DateTimeField('date published', default=timezone.now)
    recent_date = models.DateTimeField('date used', default=timezone.now)

    class Meta:
        unique_together = (('channel', 'thread_id'))
        ordering = ['-recent_date']

    def __str__(self):
        return self.thread_name

    # validate uniqueness on channel and thread_id
    def validate_unique(self, exclude=None):
        threads = Thread.objects.filter(channel=self.channel)
        if self._state.adding and threads.filter(thread_id=self.thread_id).exists():
            raise ValidationError({field:'' for field in self._meta.unique_together[0]})

    # override to auto set thread_id
    def save(self, *args, **kwargs):

        if self._state.adding:
            threads = Thread.objects.filter(channel=self.channel)

            last_id = threads.aggregate(largest=models.Max('thread_id'))['largest']

            if last_id is not None:
                self.thread_id = last_id + 1

        super(Thread, self).save(*args, **kwargs)

    def is_recent(self):
        now = timezone.now()
        return timezone.now() - datetime.timedelta(days=1) <= self.pub_date <= now

    is_recent.admin_order_field = 'pub_date'
    is_recent.boolean = True
    is_recent.short_description = 'Published recently?'

# Primary keys are thread and comment_id
class Comment(models.Model):
    comment_id = models.IntegerField(default=0)
    thread = models.ForeignKey(Thread)

    text = models.CharField(max_length=250)

    pub_date = models.DateTimeField('date published', default=timezone.now)
    owner = models.ForeignKey(User, to_field="username", null=True, on_delete=models.SET_NULL)

    class Meta:
        unique_together = (('thread', 'comment_id'))
        ordering = ['-pub_date']

    def __str__(self):
        return self.text

    # validate uniqueness on thread and comment_id
    def validate_unique(self, exclude=None):
        not_unique = Comment.objects.filter(thread=self.thread, comment_id=self.comment_id).exists()
        if self._state.adding and not_unique:
            raise ValidationError({field:'' for field in self._meta.unique_together[0]})

    # override to auto set comment_id
    def save(self, *args, **kwargs):

        if self._state.adding:
            comments = Comment.objects.filter(thread=self.thread)

            last_id = comments.aggregate(largest=models.Max('comment_id'))['largest']
            
            if last_id is not None:
                self.comment_id = last_id + 1

        #self.validate_unique()

        super(Comment, self).save(*args, **kwargs)

    # see if a comment was posted in the last day
    def is_recent(self):
        now = timezone.now()
        return timezone.now() - datetime.timedelta(days=1) <= self.pub_date <= now

    is_recent.admin_order_field = 'pub_date'
    is_recent.boolean = True
    is_recent.short_description = 'Published recently?'
