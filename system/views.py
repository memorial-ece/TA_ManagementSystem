from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt

from .models import Teacher, TA, DepartmentHead, TADuty, Course, RankTA, RankCourse, MatchResult
from .forms import DutyCreateForm
from django.shortcuts import redirect
from django.db.models import Q
import json
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from math import ceil
from django.core.files.storage import FileSystemStorage
from django.contrib import messages
import xlwt
import heapq


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
            request.session['role'] = role
            print(request.session['role'])
            return render(request, 'home.html', {'user': user})

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


# ta duty for each course
# id: course id
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
        ranking = RankTA.objects.filter(curriculum_id=id).order_by("ranking")
        user = User.objects.get(username=request.session['username'])
        user_id = user.id
        return render(request, "ta_ranking.html", {'user_id': user_id, 'id': id, 'ranking': ranking})

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
                RankTA.objects.create(curriculum=course, TA=ta, ranking=rank_value)
                rank_value = rank_value + 1
            ranking = RankTA.objects.filter(curriculum_id=id).order_by("ranking")
            user = User.objects.get(username=request.session['username'])
            user_id = user.id
            return render(request, "ta_ranking.html", {'user_id': user_id, 'id': id, 'ranking': ranking})
    return redirect('ta_list', id=id)


# ======= TA PART =======
# select courses and rank them
def select_course_list(request):
    if request.session.has_key('username'):
        username = request.session['username']
        result = RankCourse.objects.filter(TA__user__username=username)
        if result.exists():
            ta = TA.objects.get(user__username=username)
            ranking = RankCourse.objects.filter(TA_id=ta.id).order_by('ranking')
            return render(request, "course_ranking.html", {'ranking': ranking})

    courses = Course.objects.all()
    return render(request, 'course_list.html', {"courses": courses})


# TA candidates rank referred course
def rank_course(request):
    ta = TA.objects.get(user__username=request.session['username'])
    if ta.cv is None:
        messages.info(request, 'please upload cv first!')  # alert for TA to upload cv first
        return HttpResponseRedirect('/upload/')
    else:
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
                        RankCourse.objects.create(TA=ta, curriculum=course, ranking=rank_value)
                        rank_value = rank_value + 1
                    ranking = RankCourse.objects.filter(TA_id=ta.id).order_by('ranking')
                    return render(request, "course_ranking.html", {'ranking': ranking})
        return redirect('select_course_list')


# upload cv to server
# name: TA' username
def upload(request):
    if request.method == 'POST':
        file = request.FILES['myfile']
        if file is not None:
            ta = TA.objects.get(user__username=request.session["username"])
            ta.cv = file
            ta.save()
            return render(request, 'pageJump.html')
    return render(request, 'upload.html')


# ===============department head==============
# TA and course matching algorithm result
def recommended_allocation(request):
    # result = MatchResult.objects.filter(curriculum__semester=request.session['semester'])
    # if result.exists():
    #     return render(request, 'recommended_allocation.html',
    #                   {'matchingResult': MatchResult.objects.all().order_by('curriculum__courseName'),
    #                    'count': MatchResult.objects.all().count()})
    #
    # else:
    #     applicants = RankCourse.objects.all()
    #     for item in applicants:
    #         try:
    #             rank = RankTA.objects.get(curriculum_id=item.curriculum_id, TA_id=item.TA_id)
    #             duty = TADuty.objects.get(curriculum_id=item.curriculum_id)
    #             MatchResult.objects.create(TA=item.TA, curriculum=rank.curriculum, courseRanking=rank.ranking,
    #                                        TARanking=item.ranking, positions=duty.recommendedTANumber, status=False)
    #         except RankTA.DoesNotExist:
    #             continue

    applicants = TA.objects.all()
    for applicant in applicants:
        matching = MatchResult.objects.filter(TA=applicant).order_by('TARanking')
        for m in matching:
            print(m.curriculum)
            print(MatchResult.objects.filter(curriculum=m.curriculum, status=True).count())
            if MatchResult.objects.filter(curriculum=m.curriculum, status=True).count() < m.positions:
                print('----')
                m.status = True
                m.save()
                break
            elif MatchResult.objects.filter(curriculum=m.curriculum, status=True).count() is m.positions:
                for result in MatchResult.objects.filter(curriculum=m.curriculum, status=True).order_by(
                        '-courseRanking'):
                    if m.courseRanking < result.courseRanking:
                        result.status = False
                        break
                    else:
                        continue
    courses = Course.objects.filter(semester=request.session['semester'])
    for course in courses:
        if MatchResult.objects.filter(curriculum=course, status__exact=False).count() is MatchResult.objects.filter(
                curriculum=course).count():
            position = MatchResult.objects.filter(curriculum=course)[0].positions
            for result in MatchResult.objects.filter(curriculum=course).order_by('courseRanking') and position:
                result.status = True
                position = position - 1

    return render(request, 'recommended_allocation.html',
                  {'matchingResult': MatchResult.objects.filter(status=True).order_by('curriculum__courseName'),
                   'count': MatchResult.objects.filter(status=True).count()})


# download TA allocation result file as excel file
def download_excel_data(request):
    if request.method == "POST":
        # content-type of response
        response = HttpResponse(content_type='application/ms-excel')
        # decide file name
        response['Content-Disposition'] = 'attachment; filename="TAAllocationResult.xls"'
        # creating workbook
        wb = xlwt.Workbook(encoding='utf-8')
        # adding sheet
        ws = wb.add_sheet("sheet1")
        # sheet header, first row
        row_num = 0

        font_style = xlwt.XFStyle()
        # headers are bold
        font_style.font.bold = True

        style_cell = xlwt.XFStyle()
        pattern = xlwt.Pattern()
        pattern.pattern = xlwt.Pattern.SOLID_PATTERN
        pattern.pattern_fore_colour = xlwt.Style.colour_map['yellow']  # 设置单元格背景色为黄色
        style_cell.pattern = pattern

        # column header names
        columns = ['term', 'course subject', 'course name', 'instructor', 'TA position(s)', 'student(s)',
                   'student e-mail', 'status']
        # write column header in sheet
        for col_num in range(len(columns)):
            ws.write(row_num, col_num, columns[col_num], font_style)

        # sheet body, remaining rows
        font_style = xlwt.XFStyle()

        # get your data, from database or from a text file...
        data = MatchResult.objects.filter(status=True).order_by('curriculum__courseName')
        # get status
        state = request.POST['status']
        rejected_matching = state.split(',')
        rejected_matching.pop()
        for my_row in data:
            row_num = row_num + 1
            ws.write(row_num, 0, my_row.curriculum.semester, font_style)
            ws.write(row_num, 1, my_row.curriculum.subject + my_row.curriculum.courseName, font_style)
            ws.write(row_num, 2, my_row.curriculum.title, font_style)
            ws.write(row_num, 3,
                     my_row.curriculum.instructor.user.first_name + ' ' + my_row.curriculum.instructor.user.last_name,
                     font_style)
            ws.write(row_num, 4, my_row.positions, font_style)
            ws.write(row_num, 5, my_row.TA.user.first_name + ' ' + my_row.TA.user.last_name, font_style)
            ws.write(row_num, 6, my_row.TA.user.email, font_style)
            if str(my_row.id) in rejected_matching:
                ws.write(row_num, 7, 'rejected', style_cell)
            else:
                ws.write(row_num, 7, 'accepted', font_style)
        wb.save(response)
        return response
    else:
        return redirect('recommended_allocation')


# department head can customize the TA number
def ta_request_list(request):
    semester = request.session['semester']
    duty = TADuty.objects.filter(curriculum__semester=semester).order_by('curriculum__courseName')
    if duty.exists():
        return render(request, 'ta_request_list.html', {'taduty': duty})
    else:
        return HttpResponse('there is no course')


# get ta duty
# id: course id
def duty_all(request, id):
    ta_duty = TADuty.objects.get(curriculum_id=id)
    if request.method == 'GET':
        context = {
            'labNumber': ta_duty.labNumber,
            'preparationHour': ta_duty.preparationHour,
            'labHour': ta_duty.labHour,
            'labWorkingHour': ta_duty.labWorkingHour,
            'assignmentNumber': ta_duty.assignmentNumber,
            'assignmentWorkingHour': ta_duty.assignmentWorkingHour,
            'contactHour': ta_duty.contactHour,
            'otherDutiesHour': ta_duty.otherDutiesHour,
            'totalHour': ta_duty.totalHour,
            'recommendedTANumber': ta_duty.recommendedTANumber,
        }
        return JsonResponse(context)


@csrf_exempt
def update_positions(request):
    if request.method == "POST" and request.is_ajax():
        position = request.POST['positions']
        print(position)
        duty_id = request.POST['id']
        try:
            duty = TADuty.objects.get(id=duty_id)
            duty.recommendedTANumber = position
            print(duty.recommendedTANumber)
            duty.save()
            return HttpResponse(status=204)
        except TADuty.DoesNotExist:
            return JsonResponse({'error': 'something bad'}, status=400)
