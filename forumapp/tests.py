import datetime
from django.test import TestCase, Client
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Channel, Thread, Comment


## Helper functions

def create_channel(name, owner, days):
    time = timezone.now() + datetime.timedelta(days=days)
    return Channel.objects.create(channel_name=name, owner=owner, pub_date=time)

def create_comment(thread, text, owner, days):
    time = timezone.now() + datetime.timedelta(days=days)
    return Comment.objects.create(thread_id=thread, text=text, owner=owner, pub_date=time)

## Channel tests
class ChannelModelTests(TestCase):
    name = "Test channel 123456789"

    def testNoChannel(self):
        response = self.client.get(reverse('forumapp:channel'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No channels are available.")
        self.assertQuerysetEqual(response.context['channel_list'], [])

    def testChannelCreateDelete(self):
        owner = User.objects.create(self.name)

        c = create_channel(self.name, owner, -1)

        response = self.client.get(reverse('forumapp:channel'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.name)
        
        c.delete()

        self.testNoChannel()

    def testChannelsAreDisplayed(self):
        owner = User.objects.create(self.name)

        name2 = "testchannel2"
        c = create_channel(self.name, owner, -1)
        c = create_channel(name2, owner, -1)

        response = self.client.get(reverse('forumapp:channel'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.name)
        self.assertContains(response, name2)


## Comment tests
class CommentModelTests(TestCase):
    owner_name = "testuser3"
    owner_name2 = "testuser4"
    channel_name = "aaatestchannel"
    thread_name = "stupid topic"

    def testNoComment(self):
        owner = User.objects.create(self.self.owner_name)
        channel = create_channel(self.channel_name, owner, -2)
        owner2 = User.objects.create(self.owner_name2)
        thread = create_thread(channel, self.thread_name, owner2, -1)

        response = self.client.get(reverse('forumapp:comment'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No comments are available.")
        self.assertQuerysetEqual(response.context['comment_list'], [])

    def testCommentCreateDelete(self):
        owner = User.objects.create(self.owner_name)
        channel = create_channel(self.channel_name, owner, -2)
        owner2 = User.objects.create(self.owner_name2)
        thread = create_thread(channel, self.thread_name, owner2, -1)
        text = "test text :)"
        owner3 = User.objects.create(self.owner_name3)

        c = create_comment(thread, text, owner3, -1)

        response = self.client.get(reverse('forumapp:comment'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, text)
        #self.assertContains(response, self.owner_name3)
        
        c.delete()

        self.testNoComment()

    def testCommentsAreDisplayed(self):
        name2 = "testchannel2"
        owner = User.objects.create(self.owner_name)
        channel = create_channel(self.channel_name, owner, -2)
        owner2 = User.objects.create(self.owner_name2)
        thread = create_thread(channel, self.thread_name, owner2, -1)
        text = "test text :)"
        owner3 = User.objects.create(self.owner_name3)

        c = create_comment(thread, text, owner3, 0)
        c = create_comment(thread, text[::-1], owner2, -1)

        response = self.client.get(reverse('forumapp:comment'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, text)
        self.assertContains(response, text[::-1])

