import collections
import datetime
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now
import re
from website.models import Employee
from website.decorators import roles_required
from .forms import (
    ActivityForm,
    ActivityType,
    ActivityTypeForm,
    MVPFilterForm,
    MVPForm,
    ShortUpdateFilterForm,
    ShortUpdateForm,
)
from .models import MVP, Activity, ShortUpdate
from django.core.paginator import Paginator
from django.contrib import messages
from django.db.models import Q


@login_required
def short_update_form(request):
    if request.method == "POST":
        form = ShortUpdateForm(request.POST)
        if form.is_valid():
            short_update = form.save(commit=False)
            employee = Employee.objects.get(employee_email=request.user.username)
            short_update.team = employee.team
            short_update.save()
            return redirect("short_update_list")
    else:
        form = ShortUpdateForm()
    return render(request, "short_update_form.html", {"form": form})


@login_required
def mvp_form(request, phase):
    if request.method == "POST":
        form = MVPForm(request.POST, request=request)
        if form.is_valid():
            mvp = form.save(commit=False)
            employee = Employee.objects.get(employee_email=request.user.username)
            mvp.team_name = employee.team
            mvp.created_by = employee
            mvp.save()
            form.save_m2m()
            return redirect("mvp_list")
    else:
        form = MVPForm(initial={"current_phase": phase.capitalize()}, request=request)
    return render(request, "mvp_form.html", {"form": form, "phase": phase})


@login_required
def product_form(request, phase):
    if request.method == "POST":
        form = MVPForm(request.POST, request=request)
        if form.is_valid():
            product = form.save(commit=False)
            employee = Employee.objects.get(employee_email=request.user.username)
            product.team_name = employee.team
            product.updated_by = employee
            product.save()
            form.save_m2m()
            return redirect("product_list")
    else:
        form = MVPForm(initial={"current_phase": phase.capitalize()}, request=request)
    return render(request, "product_form.html", {"form": form, "phase": phase})


@login_required
def failed_form(request, phase):
    if request.method == "POST":
        form = MVPForm(request.POST, request=request)
        if form.is_valid():
            failed = form.save(commit=False)
            employee = Employee.objects.get(employee_email=request.user.username)
            failed.team_name = employee.team
            failed.updated_by = employee
            failed.save()
            form.save_m2m()
            return redirect("failed_mvp_list")
    else:
        form = MVPForm(initial={"current_phase": phase.capitalize()}, request=request)
    return render(request, "failed_form.html", {"form": form, "phase": phase})


@login_required
def short_update_list(request):
    form = ShortUpdateFilterForm(request.GET)
    user = request.user
    employee = Employee.objects.get(employee_email=user.username)
    user_team = employee.team
    if employee.mvp_role == "Super":
        short_updates = ShortUpdate.objects.all().order_by("-id")
    else:
        short_updates = ShortUpdate.objects.filter(team=user_team).order_by("-id")

    if form.is_valid():
        title = form.cleaned_data.get("title")
        status = form.cleaned_data.get("status")
        team_name = form.cleaned_data.get("team_name")
        start_date = form.cleaned_data.get("start_date")
        end_date = form.cleaned_data.get("end_date")
        if title:
            short_updates = short_updates.filter(title__icontains=title)
        if team_name:
            short_updates = short_updates.filter(team=team_name)
        if status:
            short_updates = short_updates.filter(status=status)
        if start_date and end_date:
            short_updates = short_updates.filter(
                start_date__gte=start_date, end_date__lte=end_date
            )
        elif start_date:
            short_updates = short_updates.filter(start_date__gte=start_date)
        elif end_date:
            short_updates = short_updates.filter(end_date__lte=end_date)

    paginator = Paginator(short_updates, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(
        request,
        "short_update_list.html",
        {"short_updates": page_obj, "employee": employee, "form": form},
    )


@login_required
def mvp_list(request):
    form = MVPFilterForm(request.GET)
    user = request.user
    employee = Employee.objects.get(employee_email=user.username)
    user_team = employee.team

    if employee.mvp_role == "Super":
        mvps = (
            MVP.objects.filter(current_phase="MVP", is_archived=False).order_by("-id")
            if user_team
            else MVP.objects.none()
        )
    elif employee.mvp_role == "Growth Manager" or employee.mvp_role == "Team Lead":
        mvps = (
            MVP.objects.filter(
                team_name=user_team, current_phase="MVP", is_archived=False
            ).order_by("-id")
            if user_team
            else MVP.objects.none()
        )
    elif employee.mvp_role == "Planner":
        mvps = MVP.objects.filter(
            planners=employee, current_phase="MVP", is_archived=False
        ).order_by("-id")

    if form.is_valid():
        name = form.cleaned_data.get("name")
        start_date = form.cleaned_data.get("start_date")
        end_date = form.cleaned_data.get("end_date")
        status = form.cleaned_data.get("status")
        team_name = form.cleaned_data.get("team_name")
        if name:
            mvps = mvps.filter(name__icontains=name)
        if team_name:
            mvps = mvps.filter(team_name=team_name)
        if start_date and end_date:
            mvps = mvps.filter(start_date__gte=start_date, end_date__lte=end_date)
        elif start_date:
            mvps = mvps.filter(start_date__gte=start_date)
        elif end_date:
            mvps = mvps.filter(end_date__lte=end_date)
        if status:
            mvps = mvps.filter(status=status)

    sort = request.GET.get("sort", "-id")
    mvps = mvps.order_by(sort)

    paginator = Paginator(mvps, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    mvp_details = []
    for mvp in page_obj:
        developers = mvp.developers.all()
        planners = mvp.planners.all()
        associates = mvp.associates.all()
        sixty_days_passed = False
        if mvp.first_completion_date:
            if now().date() >= mvp.first_completion_date + datetime.timedelta(days=60):
                sixty_days_passed = True

        mvp_details.append(
            {
                "mvp": mvp,
                "developers": developers,
                "associates": associates,
                "planners": planners,
                "sixty_days_passed": sixty_days_passed,
            }
        )

    return render(
        request,
        "mvp_list.html",
        {
            "mvps": page_obj,
            "form": form,
            "employee": employee,
            "mvp_details": mvp_details,
        },
    )


@login_required
def product_list(request):
    form = MVPFilterForm(request.GET)
    user = request.user

    employee = Employee.objects.get(employee_email=user.username)
    user_team = employee.team

    if employee.mvp_role == "Super":
        mvps = (
            MVP.objects.filter(current_phase="Product", is_archived=False).order_by(
                "-id"
            )
            if user_team
            else MVP.objects.none()
        )
    elif employee.mvp_role == "Growth Manager" or employee.mvp_role == "Team Lead":
        mvps = (
            MVP.objects.filter(
                team_name=user_team, current_phase="Product", is_archived=False
            ).order_by("-id")
            if user_team
            else MVP.objects.none()
        )
    elif employee.mvp_role == "Planner":
        mvps = MVP.objects.filter(
            planners=employee, current_phase="Product", is_archived=False
        ).order_by("-id")

    if form.is_valid():
        name = form.cleaned_data.get("name")
        start_date = form.cleaned_data.get("start_date")
        end_date = form.cleaned_data.get("end_date")
        status = form.cleaned_data.get("status")
        team_name = form.cleaned_data.get("team_name")
        if name:
            mvps = mvps.filter(name__icontains=name)
        if team_name:
            mvps = mvps.filter(team_name=team_name)
        if start_date and end_date:
            mvps = mvps.filter(start_date__gte=start_date, end_date__lte=end_date)
        elif start_date:
            mvps = mvps.filter(start_date__gte=start_date)
        elif end_date:
            mvps = mvps.filter(end_date__lte=end_date)
        if status:
            mvps = mvps.filter(status=status)

    sort = request.GET.get("sort", "-id")
    mvps = mvps.order_by(sort)

    paginator = Paginator(mvps, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    mvp_details = []
    for mvp in page_obj:
        developers = mvp.developers.all()
        planners = mvp.planners.all()
        sixty_days_passed = False
        if mvp.first_completion_date:
            if now().date() >= mvp.first_completion_date + datetime.timedelta(days=60):
                sixty_days_passed = True

        mvp_details.append(
            {
                "mvp": mvp,
                "developers": developers,
                "planners": planners,
                "sixty_days_passed": sixty_days_passed,
            }
        )

    return render(
        request,
        "product_list.html",
        {
            "mvps": page_obj,
            "form": form,
            "employee": employee,
            "mvp_details": mvp_details,
        },
    )


@login_required
def archive_mvp(request, pk):
    user = request.user
    employee = Employee.objects.get(employee_email=user.username)
    mvp = get_object_or_404(MVP, pk=pk)
    mvp.updated_by = employee
    mvp.is_archived = True
    mvp.save()
    return redirect("mvp_list")


@login_required
def unarchive_mvp(request, pk):
    mvp = get_object_or_404(MVP, pk=pk)
    mvp.is_archived = False

    mvp.save()
    return redirect("archive_list")


@login_required
def archive_list(request):
    form = MVPFilterForm(request.GET)
    user = request.user
    employee = Employee.objects.get(employee_email=user.username)
    user_team = employee.team

    if employee.mvp_role == "Super":
        mvps = (
            MVP.objects.filter(current_phase="Archive").order_by("-id")
            if user_team
            else MVP.objects.none()
        )
    else:
        mvps = (
            MVP.objects.filter(team_name=user_team, is_archived=True).order_by("-id")
            if user_team
            else MVP.objects.none()
        )

    if form.is_valid():
        name = form.cleaned_data.get("name")
        start_date = form.cleaned_data.get("start_date")
        end_date = form.cleaned_data.get("end_date")
        status = form.cleaned_data.get("status")
        team_name = form.cleaned_data.get("team_name")
        if name:
            mvps = mvps.filter(name__icontains=name)
        if team_name:
            mvps = mvps.filter(team_name=team_name)
        if start_date and end_date:
            mvps = mvps.filter(start_date__gte=start_date, end_date__lte=end_date)
        elif start_date:
            mvps = mvps.filter(start_date__gte=start_date)
        elif end_date:
            mvps = mvps.filter(end_date__lte=end_date)
        if status:
            mvps = mvps.filter(status=status)

    sort = request.GET.get("sort", "-id")
    mvps = mvps.order_by(sort)

    paginator = Paginator(mvps, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    mvp_details = []
    for mvp in page_obj:
        developers = mvp.developers.all()
        planners = mvp.planners.all()
        sixty_days_passed = False
        if mvp.first_completion_date:
            if now().date() >= mvp.first_completion_date + datetime.timedelta(days=60):
                sixty_days_passed = True

        mvp_details.append(
            {
                "mvp": mvp,
                "developers": developers,
                "planners": planners,
                "sixty_days_passed": sixty_days_passed,
            }
        )

    return render(
        request,
        "archive_list.html",
        {
            "mvps": page_obj,
            "form": form,
            "employee": employee,
            "mvp_details": mvp_details,
        },
    )


# @login_required
# def edit_mvp(request, pk):
#     mvp = get_object_or_404(MVP, pk=pk)

#     if request.method == "POST":
#         form = MVPForm(request.POST, instance=mvp, request=request)
#         if form.is_valid():
#             form.save()
#             return redirect("mvp_list")
#     else:
#         form = MVPForm(instance=mvp, request=request)
#     return render(request, "edit_mvp.html", {"form": form, "mvp": mvp})


@login_required
def edit_short_update(request, pk):
    short_update = get_object_or_404(ShortUpdate, pk=pk)

    if request.method == "POST":
        form = ShortUpdateForm(request.POST, instance=short_update)
        if form.is_valid():
            short_update = form.save(commit=False)

            form.save()
            return redirect("short_update_list")
    else:
        form = ShortUpdateForm(instance=short_update)
    return render(request, "short_update_edit.html", {"form": form})


@login_required
def edit_mvp(request, pk):
    mvp = get_object_or_404(MVP, pk=pk)
    first_completion_date = mvp.first_completion_date
    user = request.user
    employee = Employee.objects.get(employee_email=user.username)
    if request.method == "POST":
        form = MVPForm(request.POST, instance=mvp, request=request)
        if form.is_valid():
            mvp_instance = form.save(commit=False)
            mvp_instance.updated_by = employee
            mvp_instance.save()
            form.save_m2m()
            return redirect("mvp_list")
    else:
        form = MVPForm(instance=mvp, request=request)

    return render(
        request,
        "edit_mvp.html",
        {"form": form, "mvp": mvp, "first_completion_date": first_completion_date},
    )


@login_required
def activity_form(request):
    if request.method == "POST":
        form = ActivityForm(request.POST, user=request.user)
        if form.is_valid():
            activity = form.save(commit=False)
            employee = Employee.objects.get(employee_email=request.user.username)
            activity.team_name = employee.team
            activity.created_by = employee
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
    elif employee.mvp_role == "Planner":
        mvp_ids = MVP.objects.filter(
            Q(planners=employee) | Q(developers=employee)
        ).values_list("id", flat=True)

        activities = Activity.objects.filter(mvp_id__in=mvp_ids).order_by("-id")
    else:
        activities = (
            Activity.objects.filter(team_name=user_team).order_by("-id")
            if user_team
            else Activity.objects.none()
        )

    if form.is_valid():
        name = form.cleaned_data.get("name")
        activity_type = form.cleaned_data.get("activity_type")
        team_name = form.cleaned_data.get("team_name")
        if name:
            activities = activities.filter(mvp__name__icontains=name)
        if team_name:
            activities = activities.filter(team_name=team_name)
        if activity_type:
            activities = activities.filter(activity_type=activity_type)

    sort = request.GET.get("sort", "-id")
    activities = activities.order_by(sort)

    paginator = Paginator(activities, 30)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "activity_list.html",
        {
            "activities": activities,
            "form": form,
            "employee": employee,
            "page_obj": page_obj,
        },
    )


@login_required
def failed_mvp_list(request):
    form = MVPFilterForm(request.GET)
    user = request.user

    employee = Employee.objects.get(employee_email=user.username)
    user_team = employee.team

    if employee.mvp_role == "Super":
        mvps = (
            MVP.objects.filter(current_phase="Failed", is_archived=False).order_by(
                "-id"
            )
            if user_team
            else MVP.objects.none()
        )
    elif employee.mvp_role == "Growth Manager" or employee.mvp_role == "Team Lead":
        mvps = (
            MVP.objects.filter(
                team_name=user_team, current_phase="Failed", is_archived=False
            ).order_by("-id")
            if user_team
            else MVP.objects.none()
        )
    elif employee.mvp_role == "Planner":
        mvps = MVP.objects.filter(
            planners=employee, current_phase="Failed", is_archived=False
        ).order_by("-id")

    if form.is_valid():
        name = form.cleaned_data.get("name")
        start_date = form.cleaned_data.get("start_date")
        end_date = form.cleaned_data.get("end_date")
        status = form.cleaned_data.get("status")
        team_name = form.cleaned_data.get("team_name")
        if name:
            mvps = mvps.filter(name__icontains=name)
        if team_name:
            mvps = mvps.filter(team_name=team_name)
        if start_date and end_date:
            mvps = mvps.filter(start_date__gte=start_date, end_date__lte=end_date)
        elif start_date:
            mvps = mvps.filter(start_date__gte=start_date)
        elif end_date:
            mvps = mvps.filter(end_date__lte=end_date)
        if status:
            mvps = mvps.filter(status=status)

    sort = request.GET.get("sort", "-id")
    mvps = mvps.order_by(sort)

    paginator = Paginator(mvps, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    mvp_details = []
    for mvp in page_obj:
        developers = mvp.developers.all()
        planners = mvp.planners.all()
        sixty_days_passed = False
        if mvp.first_completion_date:
            if now().date() >= mvp.first_completion_date + datetime.timedelta(days=60):
                sixty_days_passed = True

        mvp_details.append(
            {
                "mvp": mvp,
                "developers": developers,
                "planners": planners,
                "sixty_days_passed": sixty_days_passed,
            }
        )
    return render(
        request,
        "failed_mvp_list.html",
        {
            "mvps": page_obj,
            "form": form,
            "employee": employee,
            "mvp_details": mvp_details,
        },
    )


@login_required
def activity_types_list(request):
    activities = ActivityType.objects.all()
    return render(request, "activity_type_list.html", {"activities": activities})


@login_required
def edit_activity_type(request, pk):
    mvp = get_object_or_404(MVP, pk=pk)
    activity = get_object_or_404(ActivityType, id=pk)
    if request.method == "POST":
        form = ActivityTypeForm(request.POST, instance=activity)
        if form.is_valid():
            if mvp.first_completion_date:
                form.instance.first_completion_date = mvp.first_completion_date
            form.save()

            return redirect("activity_type_list")
    else:
        form = ActivityTypeForm(instance=activity)
    return render(request, "activity_type_edit.html", {"form": form})


@login_required
def add_activity_type(request):
    if request.method == "POST":
        form = ActivityTypeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("activity_type_list")
    else:
        form = ActivityTypeForm()
    return render(request, "add_activity_type.html", {"form": form})
