"""mycompetition URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path
from index import views

urlpatterns = (
    path('admin/', admin.site.urls),
    path('addplace/', views.add_place),
    path('login/', views.login),
    path('logout/', views.logout),
    path('register/', views.register),
    path('', views.index),
    path('app_map/', views.app_map),
    path('app_place/', views.app_place),
    path('app_addplace/', views.app_addplace),
    path('index/', views.index),
    re_path('user/(?P<id>\d+)/$', views.user),
    re_path('app_history/(?P<start>.+)/(?P<end>.+)/(?P<_type>.+)/(?P<id>\d+)/$', views.app_history),
    re_path('app_manager/(?P<id>\d+)/$', views.app_manager),
    re_path('flash/(?P<id>\d+)/$', views.flash),
    re_path('app_admin/', views.app_admin),
    re_path('delete_place/(?P<id>\d+)/$', views.delete_place),
    re_path('set_max/(?P<id>\d+)/(?P<num>\d+)/$', views.set_max),
)
