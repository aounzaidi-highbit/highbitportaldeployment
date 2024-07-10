from datetime import datetime, timedelta
from .models import EvaluationFormModel, Employee

today = datetime.now().date()
first_day_of_current_month = today.replace(day=1)
first_day_of_previous_quarter = (first_day_of_current_month - timedelta(days=90)).replace(day=1)

# Replace 'Asaad Ramis' with the employee name you are checking
employee = Employee.objects.get(employee_name='Asaad Ramis')

evaluations = EvaluationFormModel.objects.filter(
    employee=employee,
    evaluation_date__gte=first_day_of_previous_quarter,
    evaluation_date__lt=first_day_of_current_month
)

print(f"Evaluations found: {evaluations.count()}")
for evaluation in evaluations:
    print(evaluation.evaluation_date, evaluation._weighted_average)