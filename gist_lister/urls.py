from django.conf.urls import url
from django.urls import path
from gist_lister import views

app_name = 'gist_lister'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^list_gists_view/', views.list_gists_view, name='list_gists_view'),
    url(r'^file_content_view/', views.file_content_view, name='file_content_view'),
]
