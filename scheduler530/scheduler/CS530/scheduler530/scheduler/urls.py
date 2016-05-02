from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^$', views.index, name='index'),
 #   url(r'^$', views.test2, name='test2'),


]
