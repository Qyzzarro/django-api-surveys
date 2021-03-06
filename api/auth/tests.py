from django.test.testcases import TestCase
from django.contrib.auth.models import User


def create_test_user(username="user", password="user"):
    user = User(username=username)
    user.set_password(password)
    user.save()
    return user, username, password


class AuthTestCase(TestCase):
    def test_login(self):
        _, username, password = create_test_user()
        response = self.client.post(
            "/api/v1/auth/",
            data={
                "username": username,
                "password": password, },
            content_type="json")
        self.assertEqual(response.status_code, 200)

    def test_logout(self):
        _, username, password = create_test_user()
        response = self.client.post(
            "/api/v1/auth/",
            data={
                "username": username,
                "password": password, },
            content_type="json")
        self.assertEqual(response.status_code, 200)

        response = self.client.get("/api/v1/auth/")
        self.assertEqual(response.status_code, 200)

    # def test_create_user(self):
    #     response = self.client.post(
    #         "/api/v1/auth/create_user/"
    #         )
    #     self.assertEqual(response.status_code, 200)
