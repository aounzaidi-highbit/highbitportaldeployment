import datetime
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
import django.utils
from website.models import Employee
from .forms import MVPFilterForm, MVPForm, ActivityForm
from .models import MVP, Activity
from django.core.paginator import Paginator


@login_required
def mvp_form(request):
    if request.method == "POST":
        form = MVPForm(request.POST, request=request)
        if form.is_valid():
            mvp = form.save(commit=False)
            employee = Employee.objects.get(employee_email=request.user.username)
            mvp.team_name = employee.team
            mvp.save()
            form.save_m2m()
            return redirect("mvp_list")
    else:
        form = MVPForm(request=request)
    return render(request, "mvp_form.html", {"form": form})


@login_required
def mvp_list(request):
    form = MVPFilterForm(request.GET)
    user = request.user

    employee = Employee.objects.get(employee_email=user.username)
    user_team = employee.team

    if employee.mvp_role == "Super":
        mvps = (
            MVP.objects.filter(current_phase="MVP").order_by("-id")
            if user_team
            else MVP.objects.none()
        )
    else:
        mvps = (
            MVP.objects.filter(team_name=user_team, current_phase="MVP").order_by("-id")
            if user_team
            else MVP.objects.none()
        )

    if form.is_valid():
        name = form.cleaned_data.get("name")
        start_date = form.cleaned_data.get("start_date")
        current_phase = form.cleaned_data.get("current_phase")
        is_active = form.cleaned_data.get("is_active")
        team_name = form.cleaned_data.get("team_name")
        if name:
            mvps = mvps.filter(name__icontains=name)
        if team_name:
            mvps = mvps.filter(team_name=team_name)
        if start_date:
            mvps = mvps.filter(start_date=start_date)

        if is_active == "true":
            mvps = mvps.filter(is_active=True)
        elif is_active == "false":
            mvps = mvps.filter(is_active=False)

    sort = request.GET.get("sort", "-id")
    mvps = mvps.order_by(sort)

    paginator = Paginator(mvps, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    mvp_details = []
    for mvp in page_obj:
        developers = mvp.developers.all()
        planners = mvp.planners.all()
        mvp_details.append({
            "mvp": mvp,
            "developers": developers,
            "planners": planners,
        })

    return render(
        request, 
        "mvp_list.html", 
        {
            "mvps": page_obj, 
            "form": form, 
            "employee": employee,
            "mvp_details": mvp_details,
        }
    )



@login_required
def product_list(request):
    form = MVPFilterForm(request.GET)
    user = request.user
    employee = Employee.objects.get(employee_email=user.username)
    user_team = employee.team

    if employee.mvp_role == "Super":
        mvps = (
            MVP.objects.filter(current_phase="Product").order_by("-id")
            if user_team
            else MVP.objects.none()
        )
    else:
        mvps = (
            MVP.objects.filter(team_name=user_team, current_phase="Product").order_by("-id")
            if user_team
            else MVP.objects.none()
        )

    if form.is_valid():
        name = form.cleaned_data.get("name")
        start_date = form.cleaned_data.get("start_date")
        current_phase = form.cleaned_data.get("current_phase")
        is_active = form.cleaned_data.get("is_active")
        team_name = form.cleaned_data.get("team_name")
        if name:
            mvps = mvps.filter(name__icontains=name)
        if team_name:
            mvps = mvps.filter(team_name=team_name)
        if start_date:
            mvps = mvps.filter(start_date=start_date)
        if current_phase:
            mvps = mvps.filter(current_phase__icontains=current_phase)

        if is_active == "true":
            mvps = mvps.filter(is_active=True)
        elif is_active == "false":
            mvps = mvps.filter(is_active=False)

    
    sort = request.GET.get("sort", "-id")
    mvps = mvps.order_by(sort)

    paginator = Paginator(mvps, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    mvp_details = []
    for mvp in page_obj:
        developers = mvp.developers.all()
        planners = mvp.planners.all()
        mvp_details.append({
            "mvp": mvp,
            "developers": developers,
            "planners": planners,
        })

    return render(
        request, 
        "product_list.html", 
        {
            "mvps": page_obj, 
            "form": form, 
            "employee": employee,
            "mvp_details": mvp_details,
        }
    )


@login_required
def edit_mvp(request, pk):
    mvp = get_object_or_404(MVP, pk=pk)

    if request.method == "POST":
        form = MVPForm(request.POST, instance=mvp, request=request)
        if form.is_valid():
            form.save()
            return redirect("mvp_list")
    else:
        form = MVPForm(instance=mvp, request=request)
    return render(request, "edit_mvp.html", {"form": form, "mvp": mvp})


# @login_required
# def edit_mvp(request, pk):
#     mvp = get_object_or_404(MVP, pk=pk)
#     user = request.user
#     employee = Employee.objects.get(employee_email=user.username)
#     if request.method == "POST":
#         form = MVPForm(request.POST, instance=mvp, request=request)
#         if form.is_valid():
#             mvp_instance = form.save(commit=False)
#             mvp_instance.updated_by =employee.employee_name
#             mvp_instance.save()
#             form.save_m2m()
#             return redirect("mvp_list",mvp_id=mvp.id)
#     else:
#         form = MVPForm(instance=mvp, request=request)

#     return render(request, "edit_mvp.html", {"form": form, "mvp": mvp})


@login_required
def activity_form(request):
    if request.method == "POST":
        form = ActivityForm(request.POST, user=request.user)
        if form.is_valid():
            activity = form.save(commit=False)
            employee = Employee.objects.get(employee_email=request.user.username)
            activity.team_name = employee.team
            activity.save()
            form.save_m2m()
            return redirect("activity_list")
    else:
        form = ActivityForm(user=request.user)

    return render(request, "activity_form.html", {"form": form})

@login_required
def activity_list(request):
    form = MVPFilterForm(request.GET)
    user = request.user
    try:
        employee = Employee.objects.get(employee_email=user.username)
        user_team = employee.team
    except Employee.DoesNotExist:
        user_team = None

    if employee.mvp_role == "Super":
        activities = Activity.objects.order_by("-id")
    else:
        activities = (
            Activity.objects.filter(team_name=user_team).order_by("-id")
            if user_team
            else Activity.objects.none()
        )

    if form.is_valid():
        name = form.cleaned_data.get("name")
        team_name = form.cleaned_data.get("team_name")
        if name:
            activities = activities.filter(mvp__name__icontains=name)
        if team_name:
            activities = activities.filter(team_name=team_name)

    sort = request.GET.get("sort", "-id")
    activities = activities.order_by(sort)

    paginator = Paginator(activities, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    
    return render(request, "activity_list.html", {
        "activities": activities,
        "form": form,
        "employee": employee,
        "page_obj": page_obj
    })