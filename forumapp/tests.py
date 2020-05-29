import datetime
from django.test import TestCase, Client
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Channel, Thread, Comment


## Helper functions
def create_user(name):
    return User.objects.create(username=name)

def get_user(name):
    return User.objects.get(username=name)

def create_channel(name, owner, days):
    time = timezone.now() + datetime.timedelta(days=days)
    return Channel.objects.create(channel_name=name, owner=owner, pub_date=time)

## Channel tests
class ChannelModelTests(TestCase):
    name = "Test channel 123456789"
    owner = get_user("testuser2")

    def testNoChannel(self):
        response = self.client.get(reverse('forumapp:channel'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No channels are available.")
        self.assertQuerysetEqual(response.context['channel_list'], [])

    def testChannelCreateDelete(self):
        c = create_channel(self.name, self.owner, -1)
        
        self.assertIn(c.channel_name, self.name)
        self.assertEqual(len(c.channel_name), len(self.name))

        c.delete()

        self.testNoChannel()
