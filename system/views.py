from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from .models import Teacher, TA, DepartmentHead, TADuty, Course, RankTA
from .forms import DutyCreateForm
from django.shortcuts import redirect
from django.db.models import Q
import json


# course list for each instructor
# id: user id
@login_required
def course_list(request, id):
    teacher = Teacher.objects.get(user_id=id)
    courses = teacher.course_set.all()
    return render(request, 'course.html', {'courses': courses})


# course corresponds TA duty
@login_required
def duty_detail(request, id):
    course = Course.objects.get(id=id)
    taDuty = TADuty.objects.get(curriculum_id=id)
    return render(request, 'duty_detail.html', {'taDuty': taDuty, 'course': course})


# edit TA duty
# id : course id
@login_required
def duty_edit(request, id):
    duty = get_object_or_404(TADuty, curriculum_id=id)
    if request.method == "POST":
        form = DutyCreateForm(request.POST, instance=duty)
        if form.is_valid():
            course = Course.objects.get(id=id)
            capacity = course.capacity
            # calculate the new total hours for each duty
            lab_number = form.cleaned_data['labNumber']
            preparation_hour = form.cleaned_data['labHour']
            lab_hour = form.cleaned_data['labHour']
            lab_working_hour = form.cleaned_data['labWorkingHour']
            assignment_number = form.cleaned_data['assignmentNumber']
            assignment_working_hour = form.cleaned_data['assignmentWorkingHour']
            contact_hour = form.cleaned_data['contactHour']
            other_duties_hour = form.cleaned_data['otherDutiesHour']
            # total lab hours
            total_lab = capacity * lab_number * (preparation_hour + lab_working_hour + lab_hour)
            # total assignment hours
            total_assignment = capacity * assignment_number * assignment_working_hour
            # total hours
            total = total_lab + total_assignment + contact_hour + other_duties_hour
            duty = form.save(commit=False)
            duty.totalHour = total
            duty.save()
            return redirect('duty_detail', id=id)
    else:
        form = DutyCreateForm(instance=duty)
    return render(request, 'duty_edit.html', {'form': form})


# instructors rank candidate TAs
# id: course id
@login_required
def ta_list(request, id):
    result = RankTA.objects.filter(curriculum_id=id)
    if result.exists():
        ranking = RankTA.objects.filter(curriculum_id=id).order_by("value")
        return render(request, "ta_ranking.html", {'course_id': id, 'ranking': ranking})
    elif request.is_ajax():
        q = request.GET.get('ta_contains')
        search_qs = TA.objects.filter(Q(user__first_name__icontains=q)
                                      | Q(user__last_name__icontains=q)
                                      ).distinct()
        results = []
        for r in search_qs:
            results.append(r.user.first_name + " " + r.user.last_name)
        data = json.dumps(results)
        mimetype = 'application/json'
        return HttpResponse(data, mimetype)
    else:
        tas = TA.objects.all()
        ta_contains_query = request.GET.get('ta_contains')
        if ta_contains_query != '' and ta_contains_query is not None:
            tas = tas.filter(Q(user__first_name__icontains=ta_contains_query)
                             | Q(user__last_name__icontains=ta_contains_query)
                             ).distinct()
        return render(request, 'ta_list.html', {'tas': tas, 'course_id': id})


# store ranking to db
# id : course id
@login_required
def rank_ta(request, id):
    if request.method == "POST":
        result = RankTA.objects.filter(curriculum_id=id)
        if result.exists():
            return redirect('ta_list', id=id)
        else:
            rank = request.POST["ranking"]
            ranking_id = rank.split(",")
            ranking_id.pop()  # delete last empty number
            rank_value = 1
            for i in ranking_id:
                ta = TA.objects.get(id=i)
                course = Course.objects.get(id=id)
                RankTA.objects.create(curriculum=course, TA=ta, value=rank_value)
                rank_value = rank_value + 1
            ranking = RankTA.objects.filter(curriculum_id=id).order_by("value")
            return render(request, "ta_ranking.html", {'course_id': id, 'ranking': ranking})
    return redirect('ta_list', id=id)
