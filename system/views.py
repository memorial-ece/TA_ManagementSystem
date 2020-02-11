from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from .models import Teacher, TA, DepartmentHead, TADuty, Course
from .forms import DutyCreateForm
from django.shortcuts import redirect


# course list for each instructor
def course_list(request, id):
    teacher = Teacher.objects.get(user_id=id)
    courses = teacher.course_set.all()
    return render(request, 'course.html', {'courses': courses})


# course corresponds TA duty
def duty_detail(request, id):
    course = Course.objects.get(id=id)
    taDuty = TADuty.objects.get(curriculum_id=id)
    return render(request, 'duty_detail.html', {'taDuty': taDuty, 'course': course})


# edit TA duty
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
def rank_ta(request):
    tas = TA.objects.all()
    return render(request, 'rank_ta.html', {'tas': tas})
