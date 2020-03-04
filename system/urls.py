from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.loginpage, name='login'),
    path('logout/', views.logout, name='logout'),
    path('course/<id>/', views.course_list, name='course_list'),
    path('duty/<id>/', views.duty_detail, name='duty_detail'),
    path('duty/<id>/edit', views.duty_edit, name='duty_edit'),
    path('ta/<id>/', views.ta_list, name="ta_list"),
    path('ta/rank/<id>/', views.rank_ta, name="rank_ta"),
    path('course_list/', views.select_course_list, name="select_course_list"),
    path('ranked_course/', views.rank_course, name="rank_course"),
]
