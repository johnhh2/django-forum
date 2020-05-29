from django.db import models
from django.contrib.auth.models import User

class Channel(models.Model):
    channel_name = models.CharField(max_length=30, primary_key=True)

    owner = models.ForeignKey(User, to_field="username", on_delete=models.CASCADE)
    pub_date = models.DateTimeField('date published')

    def __str__(self):
        return self.channel_name

# Store thread_id as primary key
class Thread(models.Model):
    thread_id = models.AutoField(primary_key=True)
    channel_name = models.ForeignKey(Channel, to_field="channel_name", on_delete=models.CASCADE)

    thread_name = models.CharField(max_length=90)
    pub_date = models.DateTimeField('date published')

    def __str__(self):
        return self.thread_name

# Primary keys are thread_name and comment_id where comment_id starts at 1 for every new thread
class Comment(models.Model):
    comment_id = models.AutoField(primary_key=True)
    thread_id = models.ForeignKey(Thread, to_field="thread_id")
    text = models.CharField(max_length=250, default="none")

    pub_date = models.DateTimeField('date published')

    class Meta:
        unique_together = [["thread_id", "comment_id"]] # 2 primary keys

    def __str__(self):
        return self.text
