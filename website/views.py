from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from website.models import Employee, EvaluationFormModel, AdminFeautures
from .forms import EvaluationForm, FileUploadForm
from django.shortcuts import get_object_or_404
import csv
from django.contrib.auth.decorators import login_required
from datetime import date, datetime, timedelta
from django.urls import reverse
from django.utils.timezone import now
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_http_methods
import re

# Create your views here.


@never_cache
@require_http_methods(["GET", "POST"])
def home(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "You have been logged in")
            return redirect("dashboard")
        else:
            messages.error(request, "There was a log in error")
            return redirect("home")
    else:
        return render(request, "home.html")


@login_required
def logout_user(request):
    logout(request)
    return redirect("home")


@login_required
def dashboard(request):

    logged_in_user = request.user
    emp = Employee.objects.get(employee_email=logged_in_user)
    emps = Employee.objects.filter(team_lead=emp).all()
    current_month = now().month
    current_year = now().year
    form_disabling_date = AdminFeautures.objects.first()
    show_evaluation = False
    submitted_employees = []

    for employee in emps:
        last_evaluation = EvaluationFormModel.objects.filter(
            employee=employee,
            evaluation_date__month=current_month,
            evaluation_date__year=current_year,
        ).first()
        if last_evaluation:
            submitted_employees.append(employee.employee_id)
        if datetime.now().day >= form_disabling_date.form_disabling_date:
            show_evaluation = True
    return render(
        request,
        "team_lead_dashboard.html",
        {
            "team_lead": emp,
            "employees": emps,
            "submitted_employees": submitted_employees,
            "show_evaluation": show_evaluation,
        },
    )


@login_required
def evaluation_view(request):
    employee_id = request.GET.get("employee_id")
    form_submitted = False
    disable_form = False
    is_editing = False
    form_disabling_date = AdminFeautures.objects.first()
    selected_month = request.GET.get("selected_month")

    today = date.today()
    first_day_of_current_month = today.replace(day=1)

    last_month_date = first_day_of_current_month - timedelta(days=1)
    second_last_month_date = last_month_date.replace(day=1) - timedelta(days=1)
    third_last_month_date = second_last_month_date.replace(day=1) - timedelta(days=1)

    last_month = last_month_date.strftime("%B")
    second_last_month = second_last_month_date.strftime("%B")
    third_last_month = third_last_month_date.strftime("%B")

    if request.method == "POST" and employee_id:
        employee = get_object_or_404(Employee, employee_id=employee_id)

        evaluation_instances = EvaluationFormModel.objects.filter(
            employee=employee
        ).order_by("-id")

        form_instance = evaluation_instances.first()

        if (
            form_instance
            and form_instance.evaluation_date.month != datetime.today().month
        ):
            form_instance = None

        form = EvaluationForm(request.POST, instance=form_instance)

        if form.is_valid():
            evaluation = form.save(commit=False)
            evaluation.employee = employee
            evaluation.evaluated_by = request.user
            evaluation.save()
            messages.success(
                request, f"Form submitted successfully for employee {employee}!"
            )
            form_submitted = True
            is_editing = True
            return redirect(reverse("dashboard"))
        else:
            if datetime.now().day >= form_disabling_date.form_disabling_date:
                form_submitted = False
            else:
                messages.error(request, "Please fill the form with relevant data.")
    else:
        form = EvaluationForm()

    if datetime.now().day >= form_disabling_date.form_disabling_date:
        disable_form = True

    if employee_id:
        employee = get_object_or_404(Employee, employee_id=employee_id)

        hb_exp_months = (today.year - employee.joining_date.year) * 12 + (
            today.month - employee.joining_date.month
        )

        if hb_exp_months < 12:
            hb_exp = f"{hb_exp_months} months"
        else:
            hb_exp_years = hb_exp_months // 12
            hb_exp_remaining_months = hb_exp_months % 12
            hb_exp = f"{hb_exp_years} years"
            if hb_exp_remaining_months > 0:
                hb_exp += f" {hb_exp_remaining_months} months"

        previous_exp_months = 0
        if employee.previous_experience:
            match = re.match(
                r"(\d+)(?:\.(\d+))? (months?|years?)",
                employee.previous_experience.lower(),
            )
            if match:
                value = int(match.group(1))
                if match.group(3).startswith("year"):
                    previous_exp_months = value * 12
                    if match.group(2):
                        previous_exp_months += int(match.group(2))
                else:
                    previous_exp_months = value

        total_exp_months = hb_exp_months + previous_exp_months

        if total_exp_months >= 12:
            total_exp_years = total_exp_months // 12
            total_exp_remaining_months = total_exp_months % 12
            total_exp = f"{total_exp_years} years"
            if total_exp_remaining_months > 0:
                total_exp += f" {total_exp_remaining_months} months"
        else:
            total_exp = f"{total_exp_months} months"
    else:
        hb_exp = None
        total_exp = None

    evaluations = []
    if selected_month and employee_id:
        evaluations = EvaluationFormModel.objects.filter(
            employee=employee,
            previous_month=selected_month,
        ).order_by("-id")

    previous_month_date = today - timedelta(days=today.day)
    previous_month = previous_month_date.strftime("%B")
    previous_year = previous_month_date.strftime("%Y")
    evaluation_for = f"{previous_month} {previous_year}"

    return render(
        request,
        "evaluation_form.html",
        {
            "form": form,
            "employee": employee if employee_id else None,
            "hb_exp": hb_exp,
            "total_exp": total_exp,
            "form_submitted": form_submitted,
            "disable_form": disable_form,
            "is_editing": is_editing,
            "last_month": last_month,
            "second_last_month": second_last_month,
            "third_last_month": third_last_month,
            "evaluations": evaluations,
            "evaluation_for": evaluation_for,
        },
    )


def upload_file(request):
    if request.method == "POST":
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES["file"]
            handle_uploaded_file(csv_file)
            return render(request, "upload_success.html")
    else:
        form = FileUploadForm()
    context = {"form": form}
    return render(request, "upload_form.html", context)


def handle_uploaded_file(csv_file):
    reader = csv.DictReader(csv_file.read().decode("utf-8").splitlines())

    for row in reader:
        employee_id = row["employee_id"]
        joining_date_str = row.get("DOJ", "")
        if joining_date_str:
            try:
                joining_date = datetime.strptime(joining_date_str, "%d-%b-%y").date()
            except ValueError:
                print(
                    f"Invalid date format for employee {employee_id}: {joining_date_str}"
                )
                continue

            try:

                employee = Employee.objects.get(employee_id=employee_id)
                employee.joining_date = joining_date
                employee.save()
            except Employee.DoesNotExist:
                print(f"Employee with ID {employee_id} does not exist.")


# def handle_uploaded_file(csv_file):
#     reader = csv.DictReader(csv_file.read().decode("utf-8").splitlines())

#     for row in reader:
#         team_name = row["team"]
#         team_lead_name = row["team_lead"]

#         team_instance, _ = Teams.objects.get_or_create(team_name=team_name)

#         is_team_lead = row.get("is_team_lead", "").lower() == "true"
#         team_lead_instance = None
#         if team_lead_name:
#             team_lead_instance, _ = Employee.objects.get_or_create(
#                 employee_name=team_lead_name,
#                 defaults={"employee_email": "", "role": "", "is_team_lead": True},
#             )

#         username = row.get("username", "default_username")

#         employee, created = Employee.objects.update_or_create(
#             employee_id=row["employee_id"],
#             defaults={
#                 "username": username,
#                 "password": row["password"],
#                 "employee_name": row["employee_name"],
#                 "employee_email": row["employee_email"],
#                 "previous_experience": row["previous_experience"],
#                 "highbit_experience": row["highbit_experience"],
#                 "team": team_instance,
#                 "team_lead": team_lead_instance,
#                 "role": row["role"],
#                 "is_team_lead": is_team_lead,
#             },
#         )