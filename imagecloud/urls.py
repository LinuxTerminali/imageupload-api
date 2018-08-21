from django.conf.urls import url
from . import views
from django.contrib.auth import views as auth_views
from django.conf.urls import include
from rest_framework_jwt.views import refresh_jwt_token
from imagecloud.views import TwitterLogin, TwitterConnect
from rest_auth.registration.views import (
    SocialAccountListView, SocialAccountDisconnectView
)
from rest_framework import routers
from rest_framework.schemas import get_schema_view
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions


schema_view = get_schema_view(
    openapi.Info(
        title="Snippets API",
        default_version='v1',
        description="Test description",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@snippets.local"),
        license=openapi.License(name="BSD License"),
    ),
    validators=['flex', 'ssv'],
    public=True,
    permission_classes=(permissions.AllowAny,),
)


router = routers.DefaultRouter()
router.register('get-all-images', views.GetUserImages,
                base_name='get-all-images')
router.register('get-shared-images', views.GetSharedImages,
                base_name='get-shared-images')
urlpatterns = [
    url(r'^', include('django.contrib.auth.urls')),
    url(r'^rest-auth/', include('rest_auth.urls')),
    url(r'^registration/', include('rest_auth.registration.urls')),
    url(r'^refresh-token/', refresh_jwt_token),
    url(r'^rest-auth/twitter/$', views.TwitterLogin.as_view(), name='fb_login'),
    url(r'^rest-auth/twitter/connect/$',
        TwitterConnect.as_view(), name='twitter_connect'),
    url(
        r'^socialaccounts/$',
        SocialAccountListView.as_view(),
        name='social_account_list'
    ),
    url(
        r'^socialaccounts/(?P<pk>\d+)/disconnect/$',
        SocialAccountDisconnectView.as_view(),
        name='social_account_disconnect'
    ),
    url(r'^upload/$', views.FileView.as_view(), name='file-upload'),
    url(r'^upload/url$', views.URLFileView.as_view(), name='url-upload'),
    url(r'^multi-upload/$', views.MultiImageUpload.as_view(), name='multi-upload'),
    url(r'^csv-upload/$', views.CsvUpload.as_view(), name='csv-upload'),
    url(r'^update-images/(?P<pk>[0-9]+)/$',
        views.UpdateUserImages.as_view(), name='image-update'),
    url('', include(router.urls)),
    url(r'^swagger(?P<format>\.json|\.yaml)$',
        schema_view.without_ui(cache_timeout=0), name='schema-json'),
    url(r'^swagger/$', schema_view.with_ui('swagger',
                                           cache_timeout=0), name='schema-swagger-ui'),
    url(r'^docs/$', schema_view.with_ui('redoc',
                                        cache_timeout=0), name='schema-redoc'),
]
