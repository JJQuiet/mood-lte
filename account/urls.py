from django.urls import path
from django.urls.resolvers import URLPattern

from account.views import *

urlpatterns = [
    path('', index, name='index'),
    path('manualLabel', manual_label, name='manual_label'),
    path('fileDownload/<int:docfile>', file_download, name='file_upload'),
    path('edit', edit),
    path('next', next_),
    path('previous', previous),
    path('nextSenti', next_senti),
]