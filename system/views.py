from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import authenticate
from .models import Teacher, TA, DepartmentHead, TADuty, Course, RankTA, RankCourse, MatchResult
from .forms import DutyCreateForm
from django.shortcuts import redirect
from django.db.models import Q
import json
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from math import ceil


def loginpage(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            request.session['username'] = username
            return render(request, "semester.html")
        else:
            return render(request, 'registration/login.html')
    return render(request, 'registration/login.html')


def select_semester(request):
    if request.method == "POST":
        semester = request.POST['semester']
        if semester is not None:
            request.session['semester'] = semester
            username = request.session['username']
            user = User.objects.get(username=username)
            role = []
            if Teacher.objects.filter(user__username=username).exists():
                role.append("instructor")
            if TA.objects.filter(user__username=username).exists():
                role.append("TA")
            if DepartmentHead.objects.filter(user__username=username).exists():
                role.append("departmenthead")
            return render(request, 'home.html', {'user': user, 'role': role})
        else:
            return HttpResponse('please select semester')


def logout(request):
    try:
        del request.session['username']
    except KeyError:
        pass
    return render(request, 'registration/logout.html')


# course list for each instructor
# id: user id
def course_list(request, id):
    teacher = Teacher.objects.get(user_id=id)
    semester = request.session['semester']
    courses = teacher.course_set.filter(semester=semester)
    if courses.exists():
        return render(request, 'course.html', {'courses': courses})
    else:
        return HttpResponse('no course this semester')


# course corresponds TA duty
# id: course id
def duty_detail(request, id):
    course = Course.objects.get(id=id)
    taDuty = TADuty.objects.get(curriculum_id=id)
    return render(request, 'duty_detail.html', {'taDuty': taDuty, 'course': course})


def ta_duty(request, id):
    taDuty = TADuty.objects.get(curriculum_id=id)
    if request.method == 'GET':
        context = {
            'labNumber': taDuty.labNumber,
            'preparationHour': taDuty.preparationHour,
            'labHour': taDuty.labHour,
            'labWorkingHour': taDuty.labWorkingHour,
            'assignmentNumber': taDuty.assignmentNumber,
            'assignmentWorkingHour': taDuty.assignmentWorkingHour,
            'contactHour': taDuty.contactHour,
            'otherDutiesHour': taDuty.otherDutiesHour,
            'totalHour': taDuty.totalHour,
            'recommendedTANumber': taDuty.recommendedTANumber,
        }
        return JsonResponse(context)


# edit TA duty
# id : course id
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
            # recommended TA numbers
            recommended_ta_number = ceil(total / 180)

            duty = form.save(commit=False)
            duty.totalHour = total
            duty.recommendedTANumber = recommended_ta_number
            duty.save()
            return redirect('duty_detail', id=id)
    else:
        form = DutyCreateForm(instance=duty)
    return render(request, 'duty_edit.html', {'form': form})


# instructors rank candidate TAs
# id: course id
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


# ======= TA PART =======
def select_course_list(request):
    if request.session.has_key('username'):
        username = request.session['username']
        result = RankCourse.objects.filter(TA__user__username=username)
        if result.exists():
            ta = TA.objects.get(user__username=username)
            ranking = RankCourse.objects.filter(TA_id=ta.id).order_by('value')
            return render(request, "course_ranking.html", {'ranking': ranking})

    courses = Course.objects.all()
    return render(request, 'course_list.html', {"courses": courses})


def rank_course(request):
    if request.method == "POST":
        if request.session.has_key('username'):
            username = request.session['username']
            result = RankCourse.objects.filter(TA__user__username=username)
            if result.exists():
                return redirect('select_course_list')
            else:
                rank = request.POST["ranking"]
                ranking_id = rank.split(',')
                ranking_id.pop()
                rank_value = 1
                ta = TA.objects.get(user__username=username)
                for i in ranking_id:
                    course = Course.objects.get(id=i)
                    RankCourse.objects.create(TA=ta, curriculum=course, value=rank_value)
                    rank_value = rank_value + 1
                ranking = RankCourse.objects.filter(TA_id=ta.id).order_by('value')
                return render(request, "course_ranking.html", {'ranking': ranking})
    return redirect('select_course_list')


def recommended_allocation(request):
    applicants = RankCourse.objects.all()
    for item in applicants:
        try:
            rank = RankTA.objects.get(curriculum_id=item.curriculum_id, TA_id=item.TA_id)
            MatchResult.objects.create(TA=item.TA, curriculum=rank.curriculum, courseRanking=rank.ranking,
                                       TARanking=item.ranking)
        except RankTA.DoesNotExist:
            continue

    courses = Course.objects.filter(semester=request.session['semester'])
    if courses.exists():
        for course in courses:
            position = TADuty.objects.get(curriculum_id=course.id)
            matching = MatchResult.objects.filter(curriculum=course).order_by("courseRanking")
            if matching.exists():
                if position.recommendedTANumber < matching.count():
                    for note in matching[position.recommendedTANumber:]:
                        note.delete()
                else:
                    continue
            else:
                continue

    tas = TA.objects.all()
    for ta in tas:
        number = ta.expectedCourseNumber
        match = MatchResult.objects.filter(TA=ta).order_by("TARanking")
        if match.exists():
            if number < match.count():
                for note in match[number:]:
                    note.delete()
                else:
                    continue
        else:
            continue
