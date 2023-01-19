from config.tests import HamgramAPITestCase
from django.urls import reverse
from rest_framework import status
from user_auth.models import User


class UserTest(HamgramAPITestCase):

    fixtures = [
        "user_auth/fixtures/user_fixtures.yaml",
    ]

    def setUp(self):
        super(UserTest, self).setUp()
        return

    #be careful of this test
    def test_rud_user(self):
        user_data = {
            "phone": "09930731973",
            "verifyCode": 3213
        }
        first_user = User.objects.first()
        response = self.client.put(reverse("user_auth:rud_user", args=[str(first_user.id)]), data=user_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual("09930731973", first_user.phone)
