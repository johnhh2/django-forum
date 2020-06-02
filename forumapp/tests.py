import datetime
from contextlib import contextmanager
from django.test import TestCase, Client
from django.core.exceptions import ValidationError

from django.utils import timezone
from django.urls import reverse

from django.contrib.auth.models import User
from .models import Channel, Thread, Comment

#Allow easy testing for validation errors
class ValidationErrorTestMixin(object):
    @contextmanager
    def assertValidationErrors(self, fields):
        try:
            yield
            raise AssertionError("ValidationError not raised")

        except ValidationError as e:
            self.assertEqual(set(fields), set(e.message_dict.keys()))

## Helper functions
def create_channel(name, owner, days):
    time = timezone.now() + datetime.timedelta(days=days)
    return Channel.objects.create(channel_name=name, owner=owner, pub_date=time)

def create_thread(channel, owner, name, desc, days):
    time = timezone.now() + datetime.timedelta(days=days)
    return Thread.objects.create(channel=channel, owner=owner, thread_name=name, description=desc, pub_date=time)

def create_comment(thread, owner, text, days):
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
        self.assertQuerysetEqual(response.context['thread_list'], [])

    def testThreadCreateDelete(self):
        owner = User.objects.create(username=self.owner_name)
        c = create_channel(self.channel_name, owner, -1)
        t = create_thread(c, owner, self.thread_name, self.thread_desc, 0)

        self.assertIn(t.thread_name, self.thread_name)
        self.assertEqual(len(t.thread_name), len(self.thread_name))

        response = self.client.get(reverse('forumapp:thread', kwargs={'channel': self.channel_name}))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.thread_name)

        c.delete()

        response = self.client.get(reverse('forumapp:thread', kwargs={'channel': self.channel_name}))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No threads are available.")
        self.assertQuerysetEqual(response.context['thread_list'], [])

    def testThreadsAreDisplayed(self):
        owner = User.objects.create(username=self.owner_name+'2')
        c = create_channel(self.channel_name, owner, -1)
        t = create_thread(c, owner, self.thread_name, self.thread_desc, 0)
        t2 = create_thread(c, owner, self.thread_name[::-1], self.thread_desc, 0)
        response = self.client.get(reverse('forumapp:thread', kwargs={'channel': self.channel_name}))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.thread_name)
        self.assertContains(response, self.thread_name[::-1])

## Comment tests
class CommentModelTests(TestCase):
    owner_name = "testuser3"
    owner_name2 = "testuser4"
    owner_name3 = "testuser5"
    channel_name = "aaatestchannel"
    thread_name = "stupid topic"
    thread_desc = "stupid description"
    text = "test text :)"

    def testNoComment(self):
        owner = User.objects.create(username=self.owner_name)

        channel = create_channel(self.channel_name, owner, -2)
        owner2 = User.objects.create(username=self.owner_name2)
        thread = create_thread(channel, owner2, self.thread_name, self.thread_desc, -1)

        response = self.client.get(reverse('forumapp:comment', kwargs={'channel': channel.channel_name, 'thread': thread.thread_id}))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No comments are available.")
        self.assertQuerysetEqual(response.context['comment_list'], [])

    def testCommentCreateDelete(self):
        owner = User.objects.create(username=self.owner_name)

        channel = create_channel(self.channel_name, owner, -2)
        owner2 = User.objects.create(username=self.owner_name2)
        thread = create_thread(channel, owner2, self.thread_name, self.thread_desc, -1)
        owner3 = User.objects.create(username=self.owner_name3)

        c = create_comment(thread, owner3, self.text, -1)

        response = self.client.get(reverse('forumapp:comment', kwargs={'channel': self.channel_name, 'thread': thread.thread_id}))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.text)
        self.assertContains(response, self.owner_name3)

        c.delete()

        response = self.client.get(reverse('forumapp:comment', kwargs={'channel': self.channel_name, 'thread': thread.thread_id}))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No comments are available.")
        self.assertQuerysetEqual(response.context['comment_list'], [])

    def testCommentsAreDisplayed(self):
        owner = User.objects.create(username=self.owner_name)
        channel = create_channel(self.channel_name, owner, -2)
        owner2 = User.objects.create(username=self.owner_name2)
        thread = create_thread(channel, owner2, self.thread_name, self.thread_desc, -1)
        owner3 = User.objects.create(username=self.owner_name3)


        c = create_comment(thread, owner3, self.text, 0)
        c = create_comment(thread, owner2, self.text[::-1], -1)

        response = self.client.get(reverse('forumapp:comment', kwargs={'channel': self.channel_name, 'thread': thread.thread_id}))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.text)
        self.assertContains(response, self.text[::-1])

## Preserve data when a User is deleted
## Cascade-delete when channels/threads are removed (preserving users)
class CascadeDeleteTests(TestCase):
    username = "randomuser91387245"
    channel_name = "channel1981719"
    channel_name2 = "asfsga"
    channel_name3 = "nhjtgrew"
    thread_name = "aaa"
    thread_name2 = "bbb"
    text = "textt"
    def testUserCascadeDelete(self):
        owner = User.objects.create(username=self.username)
        otheruser = User.objects.create(username=self.username[::-1])
        
        # Create a channel
        channel = create_channel(self.channel_name, owner, -2)
        subthread = create_thread(channel, owner, self.thread_name, self.text, -1)
        thread_id1 = subthread.thread_id

        subcomment = create_comment(subthread, owner, self.text, 0)
        comment_id1 = subcomment.comment_id
        # Create a thread under another users channel
        otherchannel = create_channel(self.channel_name2, otheruser, -2)
        thread = create_thread(otherchannel, owner, self.thread_name, self.text, -1)

        thread_id2 = thread.thread_id

        # Create a comment under another users channel and thread
        otherthread = create_thread(otherchannel, otheruser, self.thread_name2, self.text, -1)

        otherthread_id = otherthread.thread_id
        comment = create_comment(otherthread, owner, self.text, 0)
        comment_id2 = comment.comment_id

        owner.delete()

        #Channel and its children should be removed
        self.assertEqual(Channel.objects.filter(channel_name=self.channel_name).exists(), False)
        self.assertEqual(Thread.objects.filter(channel__channel_name=self.channel_name, thread_id=thread_id1).exists(), False)
        self.assertEqual(Comment.objects.filter(thread__channel__channel_name=self.channel_name, thread__thread_id=thread_id1, comment_id=comment_id1).exists(), False)

        #the thread and comment under the other user's channel should still exist
        self.assertEqual(Thread.objects.filter(channel__channel_name=self.channel_name2, thread_id=thread_id2).exists(), True)
        self.assertEqual(Comment.objects.filter(thread__channel__channel_name=self.channel_name2, thread__thread_id=otherthread_id, comment_id=comment_id2).exists(), True)

    ## Tests whether a channel is correctly passed off to one of the channel moderators 
    ## if a channel moderator is specified when the owner is deleted
    def testChannelOwnerPassOff(self):
        pass


#Confirm primary keys work as expected (esp. since comment has 3 primary keys and thread has 2)
class UniqueValidationTests(ValidationErrorTestMixin, TestCase):
    username1 = "asdjghuetjw"
    username2 = username1[:7]
    channel_name1 = "channel1981719"
    channel_name2 = channel_name1[:10]
    def testUniqueUser(self):
        user1 = User.objects.create(username=self.username1)
        user2 = User.objects.create(username=self.username2)

        with self.assertValidationErrors(['username']):
            User(username=self.username1).validate_unique()


    def testUniqueChannel(self):
        user1 = User.objects.create(username=self.username1)
        user2 = User.objects.create(username=self.username2)
        c1 = create_channel(self.channel_name1, user1, 0)
        c2 = create_channel(self.channel_name2, user2, 0)
        c3 = Channel(channel_name=self.channel_name1, owner=user1, pub_date=timezone.now())
        c4 = Channel(channel_name=self.channel_name2, owner=user1, pub_date=timezone.now())

        with self.assertValidationErrors(['channel_name']):
            c3.validate_unique()
            
        with self.assertValidationErrors(['channel_name']):
            c4.validate_unique()

    def testUniqueThread(self):
        user1 = User.objects.create(username=self.username1)
        user2 = User.objects.create(username=self.username2)
        c1 = create_channel(self.channel_name1, user1, 0)
        c2 = create_channel(self.channel_name2, user2, 0)
        t1 = create_thread(c1, user1, "a", "b", 0)
        t2 = create_thread(c1, user1, "a", "b", 0)
        t3 = create_thread(c2, user2, "c", "d", 0)
        t4 = create_thread(c2, user1, "c", "d", 0)

        self.assertEquals(t1.thread_id, t3.thread_id)
        self.assertEquals(t2.thread_id, t4.thread_id)
        
        t5 = Thread(thread_id=0, channel=c1, owner=user2, thread_name="aa", description="bb", pub_date=timezone.now())

        with self.assertValidationErrors(['channel', 'thread_id']):
            t5.validate_unique()

    def testUniqueComment(self):
        user1 = User.objects.create(username=self.username1)
        user2 = User.objects.create(username=self.username2)
        c1 = create_channel(self.channel_name1, user1, 0)
        c2 = create_channel(self.channel_name2, user2, 0)
        t1 = create_thread(c1, user1, "a", "b", 0)
        t2 = create_thread(c2, user2, "c", "d", 0)
        co1 = create_comment(t1, user1, "hi", 0)
        co3 = create_comment(t2, user2, "no", 0)
        co2 = create_comment(t1, user2, "pls", 0)
        co4 = create_comment(t2, user2, "help", 0)

        self.assertEquals(co1.thread_id, co3.thread_id)
        self.assertEquals(co2.thread_id, co4.thread_id)

        co5 = Comment(comment_id=0, thread=t1, owner=user2, text="", pub_date=timezone.now())
        co6 = Comment(comment_id=1, thread=t1, owner=user2, text="", pub_date=timezone.now())
        co7 = Comment(comment_id=1,thread=t2, owner=user1, text="", pub_date=timezone.now())
        
        with self.assertValidationErrors(['thread', 'comment_id']):
            co5.validate_unique()
      
        with self.assertValidationErrors(['thread', 'comment_id']):
            co6.validate_unique()

        with self.assertValidationErrors(['thread', 'comment_id']):
            co7.validate_unique()

    class RegistrationTests(TestCase):
        def setUp(self):
            self.credentials = {
                'username': 'testuser',
                'password': 'secret'}
            User.objects.create_user(**self.credentials)

        def testLogin(self):
            response = self.client.post('/login/', self.credentials, follow=True)

            self.assertTrue(response.context['user'].is_active)
