from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from website.decorators import roles_required
from website.models import Employee, EvaluationFormModel, AdminFeautures, Teams

from .forms import EvaluationForm, FileUploadForm
from django.shortcuts import get_object_or_404
import csv
from django.contrib.auth.decorators import login_required
from datetime import date, datetime, time, timedelta
from django.urls import reverse
from django.utils.timezone import now
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_http_methods
import re
from django.db.models import Q
from django.utils.timezone import make_aware
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import send_mail
from MVP.models import MVP

# Create your views here.
@never_cache
@require_http_methods(["GET", "POST"])
def home(request):
    if request.user.is_authenticated:
        try:
            emp = Employee.objects.get(employee_email=request.user.email)
            if emp.mvp_role == "Super":
                return redirect("super_dashboard")
            elif emp.mvp_role == "Planner":
                return redirect("mvp_list")
            else:
                return redirect("evaluations")
        except Employee.DoesNotExist:
            messages.error(request, "Employee record not found.")
            logout(request)
            return redirect("home")

    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "You have been logged in")
            try:
                emp = Employee.objects.get(employee_email=email)
                if emp.mvp_role == "Planner":
                    return redirect("mvp_list")
                elif emp.mvp_role == "Super":
                    return redirect("super_dashboard")
                else:
                    return redirect("evaluations")
            except Employee.DoesNotExist:
                messages.error(request, "Employee record not found.")
                logout(request)
                return redirect("home")
        else:
            messages.error(request, "There was a login error")
            return redirect("home")
    else:
        return render(request, "home.html")


@login_required
def logout_user(request):
    logout(request)
    return redirect("home")


@roles_required("Super")
@login_required
def super_dashboard(request):
    emp = Employee.objects.get(employee_email=request.user)
    mvp= MVP.objects.filter(current_phase="MVP").all()
    products = MVP.objects.filter(current_phase="Product").all()
    failed= MVP.objects.filter(current_phase="Failed").all()
    mvp_count = mvp.count()
    product_count = products.count()
    failed_count = failed.count()
    
    employee_count = Employee.objects.filter(is_active=True).exclude(mvp_role='Super').count()
    permenant_employee_count = Employee.objects.filter(is_active=True, is_permanent=True).exclude(mvp_role='Super').count()
    probation_employee_count = Employee.objects.filter(is_active=True, is_permanent=False).exclude(mvp_role='Super').count()
    
    grade_a_count= Employee.objects.filter(grade='A').count()
    grade_b_count= Employee.objects.filter(grade='B').count()
    grade_c_count= Employee.objects.filter(grade='C').count()
    grade_x_count= Employee.objects.filter(grade='X').count()
    
    return render(request, "super_dashboard.html", {"emp": emp, "mvp": mvp, "products": products, "failed": failed, "mvp_count": mvp_count, "product_count": product_count, "failed_count": failed_count, "employee_count": employee_count, "permenant_employee_count": permenant_employee_count, "probation_employee_count": probation_employee_count, "grade_a_count": grade_a_count, "grade_b_count": grade_b_count, "grade_c_count": grade_c_count, "grade_x_count": grade_x_count})


@login_required
def evaluations(request):
    today = date.today()
    previous_month_date = today - timedelta(days=today.day)
    previous_month = previous_month_date.strftime("%B")
    logged_in_user = request.user
    emp = Employee.objects.get(employee_email=logged_in_user)
    emps = Employee.objects.filter(team_lead=emp, is_active=True).all()
    emp_count = emps.count()

    current_month = now().month
    current_year = now().year
    form_disabling_date = AdminFeautures.objects.first()
    show_evaluation = False
    submitted_employees = []

    disabling_date_naive = datetime(
        current_year, current_month, form_disabling_date.form_disabling_date, 23, 59
    )

    disabling_date = make_aware(disabling_date_naive)

    for employee in emps:
        last_evaluation = EvaluationFormModel.objects.filter(
            employee=employee,
            evaluation_date__month=current_month,
            evaluation_date__year=current_year,
        ).first()
        if last_evaluation:
            submitted_employees.append(employee.employee_id)
        if now() >= disabling_date:
            show_evaluation = True

    submitted_count = len(submitted_employees)

    return render(
        request,
        "team_lead_dashboard.html",
        {
            "team_lead": emp,
            "employees": emps,
            "submitted_employees": submitted_employees,
            "show_evaluation": show_evaluation,
            "employee_count": emp_count,
            "submitted_count": submitted_count,
            "previous_month": previous_month,
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
    disabling_date_naive = datetime(
        today.year, today.month, form_disabling_date.form_disabling_date, 23, 59
    )
    disabling_date = make_aware(disabling_date_naive)

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
            return redirect(reverse("evaluations"))
        else:
            if now() >= disabling_date:
                form_submitted = False
            else:
                messages.error(request, "Please fill the form with relevant data.")
    else:
        form = EvaluationForm()

    if now() >= disabling_date:
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


@login_required
@roles_required("HR", "Super")
def view_quarterly_valuations(request):
    quarter = request.GET.get("quarter")
    year = request.GET.get("year")
    team_id = request.GET.get("team")
    grade = request.GET.get("grade")
    sort = request.GET.get("sort")
    order = request.GET.get("order")

    current_year = datetime.now().year
    current_month = datetime.now().month
    years = [current_year - i for i in range(5)]

    quarter_months = {
        "1": ["January", "February", "March"],
        "2": ["April", "May", "June"],
        "3": ["July", "August", "September"],
        "4": ["October", "November", "December"],
    }

    evaluation_data = []
    a_grade_count = 0
    b_grade_count = 0


    if current_month in [1, 2, 3]:
        current_quarter = 1
    elif current_month in [4, 5, 6]:
        current_quarter = 2
    elif current_month in [7, 8, 9]:
        current_quarter = 3
    else:
        current_quarter = 4


    show_button = int(quarter) == current_quarter - 1 if quarter else False

    if quarter in quarter_months and year:
        months = quarter_months[quarter]
        q_objects = Q()
        for month in months:
            q_objects |= Q(evaluation_for=f"{month} {year}")

        if team_id:
            q_objects &= Q(employee__team__id=team_id)

        evaluations = EvaluationFormModel.objects.filter(q_objects, employee__is_active=True)
        employee_data = {}
        for evaluation in evaluations:
            employee_id = evaluation.employee.employee_id
            employee_name = evaluation.employee.employee_name
            team_name = evaluation.employee.team.team_name
            role = evaluation.employee.role
            employee_grade = evaluation.employee.grade
            month = evaluation.evaluation_for.split(" ")[0]
            weighted_average = evaluation._weighted_average

            if employee_id not in employee_data:
                employee_data[employee_id] = {
                    "employee_grade": employee_grade,
                    "name": employee_name,
                    "team_name": team_name,
                    "months": {month: weighted_average},
                    "role": role,
                }
            else:
                employee_data[employee_id]["months"][month] = weighted_average

        for employee_id, employee_info in employee_data.items():
            monthly_averages = [
                employee_info["months"].get(month, "N/A") for month in months
            ]

            valid_averages = [avg for avg in monthly_averages if avg != "N/A"]

            if valid_averages:
                valid_averages = [avg for avg in valid_averages if avg is not None]
                if valid_averages:
                    quarterly_weighted_average = (
                        sum(valid_averages) / len(valid_averages)
                    ) * 10
                    quarterly_weighted_average = round(quarterly_weighted_average, 2)
                else:
                    quarterly_weighted_average = "N/A"
            else:
                quarterly_weighted_average = "N/A"

            bonus_calculations = "N/A" in monthly_averages

            data_entry = {
                "id": employee_id,
                "name": employee_info["name"],
                "team_name": employee_info["team_name"],
                "role": employee_info["role"],
                "months": monthly_averages,
                "quarterly_weighted_average": quarterly_weighted_average,
                "bonuscalculations": not bonus_calculations,
                "grade": employee_info["employee_grade"],  
            }
            evaluation_data.append(data_entry)

            if quarterly_weighted_average != "N/A":
                if quarterly_weighted_average >= 85.0:
                    a_grade_count += 1
                elif 75.0 <= quarterly_weighted_average < 85.00:
                    b_grade_count += 1

    if grade == "A":
        evaluation_data = [
            data
            for data in evaluation_data
            if data["quarterly_weighted_average"] != "N/A"
            and data["quarterly_weighted_average"] >= 85.0
            and data["months"].count("N/A") < 1
        ]
    elif grade == "B":
        evaluation_data = [
            data
            for data in evaluation_data
            if data["quarterly_weighted_average"] != "N/A"
            and 75.0 <= data["quarterly_weighted_average"] < 85.0
            and data["months"].count("N/A") < 1
        ]
    elif grade == "C":
        evaluation_data = [
            data
            for data in evaluation_data
            if data["quarterly_weighted_average"] != "N/A"
            and data["quarterly_weighted_average"] < 75.0
            and data["months"].count("N/A") < 1
        ]
    elif grade == "X":
        evaluation_data = [
            data for data in evaluation_data if data["months"].count("N/A") >= 1
        ]

    if sort == "quarterly_weighted_average":
        reverse_order = True if order == "desc" else False
        evaluation_data = sorted(
            evaluation_data,
            key=lambda x: (
                x["quarterly_weighted_average"]
                if x["quarterly_weighted_average"] != "N/A"
                else 0
            ),
            reverse=reverse_order,
        )

    month_name_list = quarter_months.get(quarter, [])
    if not quarter:
        message = f"Please select a quarter and year to view the evaluations."
    else:
        message = f"No evaluations found for Quarter {quarter} of {year}."

    teams = Teams.objects.all()

    return render(
        request,
        "quarterly_evaluation_page.html",
        {
            "evaluation_data": evaluation_data,
            "quarter": quarter,
            "year": year,
            "years": years,
            "teams": teams,
            "team": team_id,
            "month_names": month_name_list,
            "message": message,
            "a_grade_count": a_grade_count,
            "b_grade_count": b_grade_count,
            "grade": grade,
            "sort": sort,
            "order": order,
            "show_button": show_button,  
        },
    )

def export_csv(request):
    quarter = request.POST.get("quarter")
    year = request.POST.get("year")
    quarter_months = {
        "1": ["January", "February", "March"],
        "2": ["April", "May", "June"],
        "3": ["July", "August", "September"],
        "4": ["October", "November", "December"],
    }

    if quarter not in quarter_months or not year:
        return HttpResponse("Invalid quarter or year", status=400)

    months = quarter_months[quarter]
    q_objects = Q()
    for month in months:
        q_objects |= Q(evaluation_for=f"{month} {year}")

    evaluations = EvaluationFormModel.objects.filter(q_objects)

    employee_data = {}
    for evaluation in evaluations:
        employee_name = evaluation.employee.employee_name
        month = evaluation.evaluation_for.split(" ")[0]
        weighted_average = evaluation._weighted_average

        if employee_name not in employee_data:
            employee_data[employee_name] = {month: weighted_average}
        else:
            employee_data[employee_name][month] = weighted_average

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = (
        f'attachment; filename="evaluations_q{quarter}_{year}.csv"'
    )

    writer = csv.writer(response)
    writer.writerow(["Employee Name"] + months + ["Quarterly Weighted Average"])

    for employee_name, months_data in employee_data.items():
        monthly_averages = [months_data.get(month, "N/A") for month in months]
        numeric_averages = [
            value for value in monthly_averages if isinstance(value, (int, float))
        ]

        quarterly_weighted_average = (
            (sum(numeric_averages) / len(numeric_averages)) * 10
            if numeric_averages
            else "N/A"
        )

        writer.writerow(
            [employee_name] + monthly_averages + [quarterly_weighted_average]
        )

    return response


def send_emails(request):
    email_count = 0
    if request.method == "POST":
        quarter = request.POST.get("quarter")
        year = request.POST.get("year")
        bonus_a = request.POST.get("bonusA")
        bonus_b = request.POST.get("bonusB")

        if (
            not (bonus_a.isdigit() and bonus_b.isdigit())
            or int(bonus_a) <= 0
            or int(bonus_b) <= 0
        ):
            messages.error(request, "Invalid bonus amounts")
            return redirect("quarterly_evaluations")

        quarter_months = {
            "1": ["January", "February", "March"],
            "2": ["April", "May", "June"],
            "3": ["July", "August", "September"],
            "4": ["October", "November", "December"],
        }

        if quarter not in quarter_months or not year:
            return HttpResponse("Invalid quarter or year", status=400)

        months = quarter_months[quarter]
        q_objects = Q()
        for month in months:
            q_objects |= Q(evaluation_for=f"{month} {year}")

        evaluations = EvaluationFormModel.objects.filter(
            q_objects, employee__is_active=True
        )

        employee_data = {}
        for evaluation in evaluations:
            employee = evaluation.employee
            employee_name = employee.employee_name
            employee_email = employee.employee_email
            month = evaluation.evaluation_for.split(" ")[0]
            weighted_average = evaluation._weighted_average
            team_lead_name = (
                employee.team_lead.employee_name if employee.team_lead else "N/A"
            )
            team_name = employee.team.team_name if employee.team else "N/A"

            if employee_name not in employee_data:
                employee_data[employee_name] = {
                    "email": employee_email,
                    "months": {month: weighted_average},
                    "team_lead_name": team_lead_name,
                    "team_name": team_name,
                }
            else:
                employee_data[employee_name]["months"][month] = weighted_average

        for employee_name, data in employee_data.items():
            month_averages = data["months"]
            valid_months = [
                score for score in month_averages.values() if score != "N/A"
            ]

            if len(valid_months) != 3:
                grade = "X"
                bonus = None
                average_weighted_score = 0
            else:
                monthly_averages = [month_averages.get(month, 0) for month in months]
                average_weighted_score = (
                    (sum(monthly_averages) / len(monthly_averages)) * 10
                    if monthly_averages
                    else 0
                )
                grade = (
                    "A"
                    if average_weighted_score >= 85.0
                    else "B" if 75.0 <= average_weighted_score < 85.0 else "C"
                )
                bonus = bonus_a if grade == "A" else bonus_b if grade == "B" else None

            average_weighted_score = round(average_weighted_score, 2)

            context = {
                "employee_name": employee_name,
                "month_averages": month_averages,
                "average_weighted_score": average_weighted_score,
                "grade": grade,
                "team_lead_name": data["team_lead_name"],
                "team_name": data["team_name"],
                "bonus": bonus,
            }

            subject = f"Quarterly Performance Review - Q{quarter} {year}"
            html_message = render_to_string("quarterly_evaluation_email.html", context)
            plain_message = strip_tags(html_message)
            from_email = "noreply@example.com"
            to = data["email"]
            email_count += 1
            send_mail(
                subject, plain_message, from_email, [to], html_message=html_message
            )

        messages.success(
            request, f"Quarterly Emails sent successfully to {email_count} employees."
        )
        return redirect("quarterly_evaluations")

    messages.error(request, "Invalid request")
    return redirect("quarterly_evaluations")


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


@login_required
@roles_required("HR", "Super")
def update_grades(request):
    if request.method == "POST":
        quarter = request.POST.get("quarter")
        year = request.POST.get("year")
        team_id = request.POST.get("team")

        updated = update_employee_grades(quarter, year, team_id)

        if updated:
            messages.success(request, "Grades updated successfully.")
        else:
            messages.error(request, "Failed to update grades.")

    return redirect("quarterly_evaluations")


def update_employee_grades(quarter, year, team_id):

    quarter_months = {
        "1": ["January", "February", "March"],
        "2": ["April", "May", "June"],
        "3": ["July", "August", "September"],
        "4": ["October", "November", "December"],
    }

    if quarter not in quarter_months or not year:
        return False

    months = quarter_months[quarter]
    q_objects = Q()
    for month in months:
        q_objects |= Q(evaluation_for=f"{month} {year}")

    if team_id:
        q_objects &= Q(employee__team__id=team_id)

    evaluations = EvaluationFormModel.objects.filter(q_objects)
    if not evaluations.exists():
        return False  
    employee_data = {}

    for evaluation in evaluations:
        employee_id = evaluation.employee.employee_id
        month = evaluation.evaluation_for.split(" ")[0]
        weighted_average = evaluation._weighted_average

        if employee_id not in employee_data:
            employee_data[employee_id] = {
                "months": {month: weighted_average},
            }
        else:
            employee_data[employee_id]["months"][month] = weighted_average

    for employee_id, data in employee_data.items():
        monthly_averages = [data["months"].get(month, "N/A") for month in months]

        if "N/A" in monthly_averages:
            grade = "X"
        else:
            valid_averages = [avg for avg in monthly_averages if avg != "N/A"]
            if valid_averages:
                valid_averages = [avg for avg in valid_averages if avg is not None]
                if valid_averages:
                    quarterly_weighted_average = (
                        sum(valid_averages) / len(valid_averages)
                    ) * 10
                    quarterly_weighted_average = round(quarterly_weighted_average, 2)
                else:
                    quarterly_weighted_average = "N/A"
            else:
                quarterly_weighted_average = "N/A"

            if quarterly_weighted_average != "N/A":
                if quarterly_weighted_average >= 85.0:
                    grade = "A"
                elif 75.0 <= quarterly_weighted_average < 85.0:
                    grade = "B"
                else:
                    grade = "C"
            else:
                grade = "X"

        Employee.objects.filter(employee_id=employee_id).update(grade=grade)

    return True  



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
