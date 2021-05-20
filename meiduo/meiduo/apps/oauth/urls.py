from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^qq/authorization/$', views.QQUrlView.as_view()),
    url(r'^qq/user/$', views.QQLoginView.as_view()),
]