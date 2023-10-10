from django.urls import path

from . import views

urlpatterns = [
    path('', views.QgisEntriesView.as_view(), name='all'),
    path('manage/', views.feeds_list, name='feeds_list'),
]
