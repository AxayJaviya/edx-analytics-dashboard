# pylint: disable=line-too-long,no-value-for-parameter

from django.conf.urls import patterns, include, url
from django.conf import settings
from django.contrib import admin
from django.core.urlresolvers import reverse_lazy
from django.views.generic import RedirectView

from analytics_dashboard import views

admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^status/$', views.status, name='status'),
    url(r'^health/$', views.health, name='health'),
    url(r'^courses/', include('courses.urls', namespace='courses')),
    url(r'^admin/', include(admin.site.urls)),
    url('', include('social.apps.django_app.urls', namespace='social')),
    url(r'^accounts/login/$', RedirectView.as_view(url=reverse_lazy('social:begin', args=['edx-oauth2']), query_string=True), name='login'),
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout_then_login', name='logout'),
    url(r'^test/auto_auth/$', views.AutoAuth.as_view(), name='auto_auth'),
    url(r'^auth/error/$', views.AuthError.as_view(), name='auth_error'),
)

if settings.DEBUG:  # pragma: no cover
    import debug_toolbar

    urlpatterns += patterns(
        '',
        url(r'^__debug__/', include(debug_toolbar.urls))
    )