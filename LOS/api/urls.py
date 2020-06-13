from django.conf.urls import url
from django.urls import path
#from . import views
from api.views import FetchData,TestData
from api import views


urlpatterns = [
    url(r'^$', views.home, name='API-home'),
    url(r'/about', views.about, name='API-about'),
    url(r'train/', FetchData.as_view()),
    url(r'test/', TestData.as_view()),
    path('load/<branchname>/<from_date>/<to_date>/', views.location),
]
