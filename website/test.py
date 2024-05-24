import csv
from datetime import datetime
from .models import Employee

def update_joining_dates_from_csv(csv_file_path):
    with open(csv_file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            try:
                employee = Employee.objects.get(employee_id=row['employee_id'])
                employee.joining_date = datetime.strptime(row['JOD'], '%Y-%m-%d').date()
                employee.save()
            except Employee.DoesNotExist:
                print(f"Employee with ID {row['employee_id']} does not exist.")

# Call the function with the path to your CSV file
update_joining_dates_from_csv(r"C:\Users\ADMIN\Downloads\Employee Information New.csv")