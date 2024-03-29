from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from authentication.utils import create_token
from user.models import CustomUser


class AuthenticationTests(APITestCase):
    def setUp(self) -> None:
        super().setUp()
        u = CustomUser.objects.create(username='username1',
                                      password='password',
                                      email='email@mail.com',
                                      first_name='first_name',
                                      last_name='last_name')

        u.refresh_token = create_token({'id': u.id,
                                        'username': u.username,
                                        'email': u.email}, 'refresh')
        self.test_user = u
        self.test_user.save()

    def test_registration_valid(self):
        old_users_count = CustomUser.objects.count()
        url = reverse('registration')
        data = {'username': 'test_user_1',
                'password': 'password',
                'email': 'test_email@mail.com',
                'first_name': 'test_first_name',
                'last_name': 'test_last_name'}
        self.client.credentials()
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(CustomUser.objects.count(), old_users_count + 1)

    def test_registration_invalid(self):
        url = reverse('registration')
        data = {'username': 'test_user_1',
                'password': 'password',
                'first_name': 'test_first_name',
                'last_name': 'test_last_name'}
        self.client.credentials()
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        data = {'username': 'test_user_1',
                'password': 'password',
                'email': 'broken_email',
                'first_name': 'test_first_name',
                'last_name': 'test_last_name'}
        self.client.credentials()
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_valid(self):
        url = reverse('login')
        data = {'username': 'username1',
                'password': 'password',
                'email': 'email@mail.com',
                'first_name': 'first_name',
                'last_name': 'last_name'}
        self.client.credentials()
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_login_invalid(self):
        url = reverse('login')
        data = {'username': 'username',
                'password': 'password1',
                'email': 'email@mail.com',
                'first_name': 'first_name',
                'last_name': 'last_name'}
        self.client.credentials()
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def _refresh(self, data, status):
        url = reverse('refresh')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status)

    def test_refresh(self):
        collections = [
            {
                "data": {
                    'refresh_token': 'token'
                },
                "status": status.HTTP_401_UNAUTHORIZED
            },
            {
                "data": {
                    'refresh': 'token'
                },
                "status": status.HTTP_401_UNAUTHORIZED
            },
            {
                "data": {
                    'refresh_token': self.test_user.refresh_token
                },
                "status": status.HTTP_200_OK
            }
        ]
        self.client.credentials()
        for elem in collections:
            self._refresh(elem.get('data'), elem.get('status'))

    def test_backend_1(self):
        id_ = self.test_user.id
        url = reverse('users-list')
        access_token = create_token({'id': id_,
                                     'email': 'email@mail.com'}, 'access')
        self.client.credentials(HTTP_AUTHORIZATION='jwt ' + access_token)
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_backend_2(self):
        url = reverse('users-list')
        access_token = create_token({'id': -1,
                                     'email': 'email@mail.com'}, 'access')
        self.client.credentials(HTTP_AUTHORIZATION='jwt ' + access_token)
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # def test_expire_time(self):
    #     url = reverse('users-list')
    #     response = self.client.post(url, format='json')
    #     access_token = create_token({'id': self.id_,
    #                                  'email': 'email@mail.com'}, 'access')
    #     time.sleep(11)
    #     self.client.credentials(HTTP_AUTHORIZATION='jwt ' + access_token)
    #     self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
