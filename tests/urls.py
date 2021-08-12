from django.urls import path
from rest_framework.routers import DefaultRouter

from drf_util.utils import get_custom_schema_view
from tests.view import ThingViewSet

schema_view = get_custom_schema_view(
    title='Api Documentation'
)

router = DefaultRouter()
router.register('things', ThingViewSet, basename='things')

urlpatterns = [
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    *router.urls
]
