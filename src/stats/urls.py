"""
URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  re_path(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  re_path(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  re_path(r'^blog/', include(blog_urls))
"""
from django.urls import include, re_path
from django.views.generic import RedirectView

from . import views


app_name = 'stats'
urlpatterns = [
    re_path(r'^pilots/$', views.pilot_rankings, name='pilots'),
    re_path(r'^tankmans/$', views.tankman_rankings, name='tankmans'),
    re_path(r'^squads/$', views.squad_rankings, name='squads'),
    re_path(r'^sorties/(?P<profile_id>\d+)/(?P<nickname>\S+)/$', views.pilot_sorties, name='pilot_sorties'),
    re_path(r'^tankman_sorties/(?P<profile_id>\d+)/(?P<nickname>\S+)/$', views.tankman_sorties, name='tankman_sorties'),
    re_path(r'^vlifes/(?P<profile_id>\d+)/(?P<nickname>\S+)/$', views.pilot_vlifes, name='pilot_vlifes'),
    re_path(r'^awards/(?P<profile_id>\d+)/(?P<nickname>\S+)/$', views.pilot_awards, name='pilot_awards'),
    re_path(r'^killboard/(?P<profile_id>\d+)/(?P<nickname>\S+)/$', views.pilot_killboard, name='pilot_killboard'),
    re_path(r'^tankman_vlifes/(?P<profile_id>\d+)/(?P<nickname>\S+)/$', views.tankman_vlifes, name='tankman_vlifes'),
    re_path(r'^tankman_awards/(?P<profile_id>\d+)/(?P<nickname>\S+)/$', views.tankman_awards, name='tankman_awards'),
    re_path(r'^tankman_killboard/(?P<profile_id>\d+)/(?P<nickname>\S+)/$', views.tankman_killboard, name='tankman_killboard'),
    re_path(r'^missions/$', views.missions_list, name='missions_list'),

    re_path(r'^squad/(?P<squad_id>\d+)/(?P<squad_tag>\S+)/$', views.squad, name='squad'),
    re_path(r'^pilots/(?P<squad_id>\d+)/(?P<squad_tag>\S+)/$', views.squad_pilots, name='squad_pilots'),
    re_path(r'^tankmans/(?P<squad_id>\d+)/(?P<squad_tag>\S+)/$', views.squad_tankmans, name='squad_tankmans'),

    re_path(r'^pilot/(?P<profile_id>\d+)/(?P<nickname>\S+)/$', views.pilot, name='pilot'),
    re_path(r'^sortie/(?P<sortie_id>\d+)/$', views.pilot_sortie, name='pilot_sortie'),
    re_path(r'^sortie/log/(?P<sortie_id>\d+)/$', views.pilot_sortie_log, name='pilot_sortie_log'),
    re_path(r'^mission/(?P<mission_id>\d+)/$', views.mission, name='mission'),
    re_path(r'^vlife/(?P<vlife_id>\d+)/$', views.pilot_vlife, name='pilot_vlife'),
    re_path(r'^tankman/(?P<profile_id>\d+)/(?P<nickname>\S+)/$', views.tankman, name='tankman'),
    re_path(r'^tankman_sortie/(?P<sortie_id>\d+)/$', views.tankman_sortie, name='tankman_sortie'),
    re_path(r'^tankman_sortie/log/(?P<sortie_id>\d+)/$', views.tankman_sortie_log, name='tankman_sortie_log'),
    re_path(r'^tankman_vlife/(?P<vlife_id>\d+)/$', views.tankman_vlife, name='tankman_vlife'),

    re_path(r'^overall/$', views.overall, name='overall'),

    re_path(r'^online/$', views.online, name='online'),
    re_path(r'^$', views.main, name='main'),

    # нужно чтобы работали url без имени
    re_path(r'^pilot/(?P<profile_id>\d+)/$', views.pilot),
    re_path(r'^sorties/(?P<profile_id>\d+)/$', views.pilot_sorties),
    re_path(r'^vlifes/(?P<profile_id>\d+)/$', views.pilot_vlifes),
    re_path(r'^tankman/(?P<profile_id>\d+)/$', views.tankman),
    re_path(r'^tankman_sorties/(?P<profile_id>\d+)/$', views.tankman_sorties),
    re_path(r'^tankman_vlifes/(?P<profile_id>\d+)/$', views.tankman_vlifes),
]
