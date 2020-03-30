from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.loginpage, name='login'),
    path('logout/', views.logout, name='logout'),
    path('course/<id>/', views.course_list, name='course_list'),
    path('duty/<id>/', views.duty_detail, name='duty_detail'),
    path('course_list/ta_duty/<id>/', views.ta_duty, name="ta_duty"),
    path('duty/<id>/edit', views.duty_edit, name='duty_edit'),
    path('ta_list/<id>/', views.ta_list, name="ta_list"),
    path('ta/rank/<id>/', views.rank_ta, name="rank_ta"),
    path('course_list/', views.select_course_list, name="select_course_list"),
    path('ranked_course/', views.rank_course, name="rank_course"),
    path('semester/', views.select_semester, name="select_semester"),
    path('recommended_allocation/', views.recommended_allocation, name="recommended_allocation"),
    path('upload/<name>/', views.upload, name="upload"),
]
