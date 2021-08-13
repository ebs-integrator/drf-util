import random
from abc import ABC

from django.conf import settings
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from drf_util.utils import get_applications, Colors, gt

fixtures_path = gt(settings, 'FIXTURES_PATH', 'apps/fixtures')


class CustomClient(APIClient):
    default_status_codes = {
        'GET': status.HTTP_200_OK,
        'POST': status.HTTP_201_CREATED,
        'DELETE': status.HTTP_204_NO_CONTENT
    }

    def request(self, **request):
        assert_status_code = request.pop(
            'assert_status_code', self.default_status_codes.get(request.get('REQUEST_METHOD'), 200)
        )

        print(f"{Colors.BOLD}{Colors.WARNING} {request.get('REQUEST_METHOD')}:{Colors.END} {request.get('PATH_INFO')}")
        response = super().request(**request)
        assert response.status_code == assert_status_code, (
            response.json() if response.status_code != status.HTTP_500_INTERNAL_SERVER_ERROR else response.status_code
        )

        if assert_status_code != status.HTTP_204_NO_CONTENT:
            print(f"{Colors.WARNING} Response:{Colors.END} {response.json()}")

        return response


class BaseTestCase(ABC):
    client_class = CustomClient
    user = None
    client = None

    def _callTestMethod(self, method):
        class_name = self.__class__.__name__
        method_name = method.__name__
        print(
            f'{Colors.BOLD}{Colors.BLUE} {class_name}{Colors.END} -> {Colors.GREEN}{method_name}{Colors.END}'
        )
        super()._callTestMethod(method)

    def setUp(self) -> None:
        self.user = get_user_model().objects.first()
        self.client.force_authenticate(self.user)


class CRUDTestCase(BaseTestCase):
    base_view = None
    queryset = None
    fake_data = {}

    def test_list(self) -> None:
        self.client.get(reverse(f'{self.base_view}-list'))

    def test_create(self) -> None:
        json_response = self.client.post(reverse(f'{self.base_view}-list'), data=self.fake_data).json()
        self.assertEqual(self.queryset.filter(pk=json_response.get('id')).count(), 1)

    def test_update(self) -> None:
        test_instance = self.queryset.first()
        self.client.put(reverse(f'{self.base_view}-detail', args=(test_instance.id,)), data=self.fake_data).json()
        test_instance.refresh_from_db()

        for field, value in self.fake_data.items():
            self.assertEqual(str(getattr(test_instance, field)), str(value))

    def test_partial_update(self) -> None:
        test_instance = self.queryset.first()
        rand_index = random.randrange(0, len(self.fake_data))
        data = {
            **{key: value for key, value in list(self.fake_data.items())[:rand_index]}
        }
        self.client.patch(reverse(f'{self.base_view}-detail', args=(test_instance.id,)), data=data).json()
        test_instance.refresh_from_db()

        for field, value in data.items():
            self.assertEqual(str(getattr(test_instance, field)), str(value))

    def test_destroy(self) -> None:
        test_instance = self.queryset.first()
        self.client.delete(reverse(f'{self.base_view}-detail', args=(test_instance.id,)))
        self.assertEqual(self.queryset.filter(pk=test_instance.pk).count(), 0)
