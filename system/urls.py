from django.urls import path
from . import views


urlpatterns = [
    path('course/<id>/', views.course_list, name='course_list'),
    path('taduty/<id>/', views.taDuty_list, name='taDuty_list'),
    path('rank/', views.rank_ta, name="rank_ta"),
]
