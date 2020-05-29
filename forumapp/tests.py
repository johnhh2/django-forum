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

def create_thread(channel, owner, name, days):
    time = timezone.now() + datetime.timedelta(days=days)
    return Thread(channel_name=channel, owner=owner, thread_name=name, pub_date=time)

## Channel tests
class ChannelModelTests(TestCase):
    channel_name = "Test channel 123456789"
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

        c.delete()

        self.testNoChannel()



class ThreadModelTests(TestCase):
    channel_name = "channelforthreadtest"
    owner_name = 'owner'
    thread_name = "threadtest"

    def testNoThread(self):
        owner = User.objects.create(username=self.owner_name)
        c = create_channel(self.channel_name, owner, -1)
        response = self.client.get(reverse('forumapp:thread', kwargs={'channel_name': self.channel_name}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No threads are available.")
        self.assertQuerysetEqual(response.context['thread_list'], [])

    def testThreadCreateDelete(self):
        owner = User.objects.create(username=self.owner_name)
        c = create_channel(self.channel_name, owner, -1)
        t = create_thread(c, owner, self.thread_name, 0)

        self.assertIn(t.thread_name, self.thread_name)
        self.assertEqual(len(t.thread_name), len(self.thread_name))

        c.delete()

        self.testNoThread()
