from django import forms

class ChannelForm(forms.Form):
    channel_name = forms.SlugField(label='Channel name', max_length=30)

class ThreadForm(forms.Form):
    thread_name = forms.CharField(label='Thread name', max_length=90)
    description = forms.CharField(label='Thread body', max_length=150)

class CommentForm(forms.Form):
    text = forms.CharField(label='Message', max_length=250)
