from django.test import TestCase


class SessionBasedTestCase(TestCase):
    def setUp(self):
        self.session_id = self.client.session.session_key
