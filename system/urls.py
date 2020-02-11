from django.urls import path
from . import views


urlpatterns = [
    path('course/<id>/', views.course_list, name='course_list'),
    path('duty/<id>/', views.duty_detail, name='duty_detail'),
    path('duty/<id>/edit', views.duty_edit, name='duty_edit'),
    path('rank/', views.rank_ta, name="rank_ta"),
]
