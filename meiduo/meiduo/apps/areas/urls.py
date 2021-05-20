from django.conf.urls import url
from rest_framework.routers import DefaultRouter

from areas.views import AreaViewSet
from . import views

urlpatterns = [
    # url(r'^areas/$', views.AreaListView.as_view()),
    # url(r'^areas/(?P<pk>\d+)/$', views.AreaRetrieveView.as_view()),
]

router = DefaultRouter()
router.register('areas', AreaViewSet, base_name='areas')
urlpatterns += router.urls
