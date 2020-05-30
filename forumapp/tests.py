import datetime
from django.test import TestCase, Client
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Channel, Thread, Comment


## Helper functions
def create_channel(name, owner, days):
    time = timezone.now() + datetime.timedelta(days=days)
    try:
        return Channel.objects.get(channel_name=name, owner=owner, pub_date=time)
    except:
        return Channel.objects.create(channel_name=name, owner=owner, pub_date=time)

def create_thread(channel, owner, name, desc, days):
    time = timezone.now() + datetime.timedelta(days=days)
    return Thread(channel=channel, owner=owner, thread_name=name, description=desc, pub_date=time)

def create_comment(thread, text, owner, days):
    time = timezone.now() + datetime.timedelta(days=days)
    return Comment.objects.create(thread=thread, text=text, owner=owner, pub_date=time)

##TODO: create_reply

## Channel tests
class ChannelModelTests(TestCase):
    channel_name = "Test-channel-123456789"
    owner_name = 'owner'

    def testNoChannel(self):
        response = self.client.get(reverse('forumapp:channel'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No channels are available.")
        self.assertQuerysetEqual(response.context['channel_list'], [])

    def testChannelCreateDelete(self):
        owner = User.objects.create(username=self.owner_name)

        c = create_channel(self.channel_name, owner, -1)

        self.assertIn(c.channel_name, self.channel_name)
        self.assertEqual(len(c.channel_name), len(self.channel_name))

        response = self.client.get(reverse('forumapp:channel'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.channel_name)

        c.delete()

        self.testNoChannel()

    def testChannelsAreDisplayed(self):
        owner = User.objects.create(username=self.owner_name)

        channel_name_2 = "testchannel2"
        c = create_channel(self.channel_name, owner, -1)
        c = create_channel(channel_name_2, owner, -1)

        response = self.client.get(reverse('forumapp:channel'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.channel_name)
        self.assertContains(response, channel_name_2)

## Thread tests
class ThreadModelTests(TestCase):
    channel_name = "channelforthreadtest"
    owner_name = 'owner'
    thread_name = "threadtest"
    thread_desc = "descriptionforthreadtest"

    def testNoThread(self):
        owner = User.objects.create(username=self.owner_name)
        c = create_channel(self.channel_name, owner, -1)
        response = self.client.get(reverse('forumapp:thread', kwargs={'channel': self.channel_name}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No threads are available.")
        #self.assertQuerysetEqual(response.context['thread_list'], [])

    def testThreadCreateDelete(self):
        owner = User.objects.create(username=self.owner_name+'2')
        c = create_channel(self.channel_name, owner, -1)
        t = create_thread(c, owner, self.thread_name, self.thread_desc, 0)

        self.assertIn(t.thread_name, self.thread_name)
        self.assertEqual(len(t.thread_name), len(self.thread_name))

        c.delete()

        self.testNoThread()

## Comment tests
class CommentModelTests(TestCase):
    owner_name = "testuser3"
    owner_name2 = "testuser4"
    owner_name3 = "testuser5"
    channel_name = "aaatestchannel"
    thread_name = "stupid topic"
    thread_desc = "stupid description"

    def testNoComment(self):
        owner = User.objects.create(username=self.owner_name)
        channel = create_channel(self.channel_name, owner, -2)
        owner2 = User.objects.create(username=self.owner_name2)
        thread = create_thread(channel, owner2, self.thread_name, self.thread_desc, -1)
        thread.save()

        response = self.client.get(reverse('forumapp:comment'), kwargs={'channel': channel.channel_name, 'thread': thread.thread_id})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No comments are available.")
        #self.assertQuerysetEqual(response.context['comment_list'], [])

    def testCommentCreateDelete(self):
        owner = User.objects.create(username=self.owner_name)
        channel = create_channel(self.channel_name, owner, -2)
        owner2 = User.objects.create(username=self.owner_name2)
        thread = create_thread(channel, owner2, self.thread_name, self.thread_desc, -1)
        text = "test text :)"
        owner3 = User.objects.create(username=self.owner_name3)

        c = create_comment(thread, text, owner3, -1)

        response = self.client.get(reverse('forumapp:comment'), kwargs={'channel': self.channel_name, 'thread': thread.thread_id})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, text)
        self.assertContains(response, self.owner_name3)

        c.delete()

        #self.testNoComment()

    def testCommentsAreDisplayed(self):
        name2 = "testchannel2"
        owner = User.objects.create(username=self.owner_name)
        channel = create_channel(self.channel_name, owner, -2)
        owner2 = User.objects.create(username=self.owner_name2)
        thread = create_thread(channel, owner2, self.thread_name, self.thread_desc, -1)
        text = "test text :)"
        owner3 = User.objects.create(username=self.owner_name3)

        c = create_comment(thread, text, owner3, 0)
        c = create_comment(thread, text[::-1], owner2, -1)

        response = self.client.get(reverse('forumapp:comment'), kwargs={'channel': self.channel_name, 'thread': thread.thread_id})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, text)
        self.assertContains(response, text[::-1])
