from django.forms import ModelForm
from .models import UserSettings, Channel, Thread, Comment

class ChannelForm(ModelForm):
    class Meta:
        model = Channel
        fields = ['channel_name', 'description']

class ThreadForm(ModelForm):
    class Meta:
        model = Thread
        fields = ['thread_name', 'description']

class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['text']

class UserSettingsForm(ModelForm):
    class Meta:
        model = UserSettings
        fields = ['bio',]
