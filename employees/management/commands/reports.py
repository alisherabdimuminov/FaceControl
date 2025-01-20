from datetime import datetime, timedelta
from django.core.management.base import BaseCommand, CommandError
from employees.models import Employee
from collections import defaultdict
from employees.serializers import AttendancesSerializer


class Command(BaseCommand):
    help = "Print reports as PDF"

    def add_arguments(self, parser):
        parser.add_argument("start_day", type=str)
        parser.add_argument("start_month", type=str)
        parser.add_argument("start_year", type=str)
        parser.add_argument("end_day", type=str)
        parser.add_argument("end_month", type=str)
        parser.add_argument("end_year", type=str)

    def handle(self, *args, **options):
        html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Document</title>
</head>
<style>
    table {
        border: 1px solid black;
        border-collapse: collapse;
    }
    th, td {
        border: 1px solid black;
    }
</style>
<body>
    <table>
        <thead>
            <th>Xodim</th>
            %s
        </thead>
        <tbody>
            %s
        </tbody>
    </table>
</body>
</html>"""
        start_day = options.get("start_day")
        start_month = options.get("start_month")
        start_year = options.get("start_year")
        end_day = options.get("end_day")
        end_month = options.get("end_month")
        end_year = options.get("end_year")

        start_date = datetime.strptime(f"{start_day}-{start_month}-{start_year}", "%d-%m-%Y")
        end_date = datetime.strptime(f"{end_day}-{end_month}-{end_year}", "%d-%m-%Y")

        date_range = [(start_date + timedelta(days=i)).strftime("%d-%m-%Y") 
                    for i in range((end_date - start_date).days + 1)]

        response = {}

        employees_obj = Employee.objects.filter(active=True)

        for date in date_range:
            day, month, year = date.split("-")
            report = AttendancesSerializer(employees_obj, many=True, context={ "date": { "day": day, "month": month, "year": year } })
            response[date] = report.data
        
        
        days = ""

        
        for report in response:
            days += f"<th>{report}</th>\n"
            
        result = defaultdict(list)

        for date, entires in response.items():
            for entry in entires:
                result[entry["full_name"]].append(entry["attendance_access_time"])

        output = [{"name": full_name, "times": access} for full_name, access in result.items()]


        ghtml = ""

        for out in output:
            name = out.get("name")
            times = out.get("times")
            trhtml = "<tr>"
            tdhtml = ""
            for time in times:
                if time == "x":
                    tdhtml += f"<td style=\"background-color: red;\"></td>"
                else:
                    tdhtml += f"<td>{time}</td>"
            trhtml += f"<td>{name}</td>"
            trhtml += tdhtml
            trhtml += "</tr>"
            ghtml += trhtml

        
        html = html % (days, ghtml)

        print(html)