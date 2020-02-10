from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404
from django.contrib.auth.models import User
from django.shortcuts import redirect
from .models import Teacher, TA, DepartmentHead, TADuty, Course


# course list for each instructor
def course_list(request, id):
    teacher = Teacher.objects.get(user_id=id)
    courses = teacher.course_set.all()
    return render(request, 'course.html', {'courses': courses})


# course corresponds TA duty
def taDuty_list(request, id):
    course = Course.objects.get(id=id)
    taDuty = TADuty.objects.get(curriculum_id=id)
    return render(request, 'taDuty.html', {'taDuty': taDuty, 'course': course})


# instructors rank candidate TAs
def rank_ta(request):
    tas = TA.objects.all()
    return render(request, 'rank_ta.html', {'tas': tas})
