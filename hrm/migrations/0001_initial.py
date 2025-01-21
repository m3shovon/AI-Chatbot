

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import hrm.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('software_settings', '0001_initial'),
        ('accounting', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('software_settings', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('rank', models.IntegerField(blank=True, default=0, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Designation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('rank', models.IntegerField(blank=True, default=0, null=True)),
                ('responsibility', models.CharField(blank=True, max_length=550, null=True)),
                ('Department', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='hrm.department')),
            ],
        ),
        migrations.CreateModel(
            name='Employee',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('photo', models.ImageField(blank=True, null=True, upload_to='employee/photo')),
                ('phone', models.CharField(blank=True, max_length=255, null=True, unique=True)),
                ('emergency_phone', models.CharField(blank=True, max_length=255, null=True)),
                ('address', models.CharField(blank=True, max_length=500, null=True)),
                ('defaultShift', models.CharField(default='day', max_length=255)),
                ('defaultEntryTime', models.TimeField(blank=True, default='10:00:00', null=True)),
                ('defaultExitTime', models.TimeField(blank=True, default='20:00:00', null=True)),
                ('created', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('modified', models.DateTimeField(default=django.utils.timezone.now)),
                ('Designation', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='hrm.designation')),
            ],
        ),
        migrations.CreateModel(
            name='GroupOfCompany',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='LeaveType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Typename', models.CharField(max_length=255)),
                ('initialDays', models.IntegerField(blank=True, default=0, null=True)),
                ('created', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('modified', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='Loan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('loanAmount', models.FloatField(blank=True, default=0.0, null=True)),
                ('loanType', models.CharField(blank=True, max_length=255, null=True)),
                ('loanPayableMonths', models.IntegerField(blank=True, default=0, null=True)),
                ('loanPayableAmount', models.FloatField(blank=True, default=0.0, null=True)),
                ('loanStatus', models.CharField(default='pending', max_length=255)),
                ('loanPaymentStatus', models.CharField(default='pending', max_length=255)),
                ('note', models.CharField(blank=True, default='', max_length=255, null=True)),
                ('created', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('modified', models.DateTimeField(default=django.utils.timezone.now)),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='employee_loan', to='hrm.employee')),
                ('payment_method', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='loan_payment_method', to='accounting.account')),
            ],
        ),
        migrations.CreateModel(
            name='OfficeType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('rank', models.IntegerField(blank=True, default=0, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='SalaryPayment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('paidAmount', models.FloatField(blank=True, default=0.0, null=True)),
                ('salaryMonth', models.IntegerField(blank=True, default=0, null=True)),
                ('salaryYear', models.IntegerField(blank=True, default=0, null=True)),
                ('paymentDate', models.DateTimeField(default=django.utils.timezone.now)),
                ('created', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('modified', models.DateTimeField(default=django.utils.timezone.now)),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='employee_salary_payment', to='hrm.employee')),
            ],
        ),
        migrations.CreateModel(
            name='Salary',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('monthlySalary', models.FloatField(blank=True, default=0.0, null=True)),
                ('dailyAllowance', models.FloatField(blank=True, default=0.0, null=True)),
                ('incentive', models.FloatField(blank=True, default=0.0, null=True)),
                ('created', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('modified', models.DateTimeField(default=django.utils.timezone.now)),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='employee_salary', to='hrm.employee')),
            ],
        ),
        migrations.CreateModel(
            name='Permission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_create', models.BooleanField(default=False)),
                ('is_read', models.BooleanField(default=False)),
                ('is_update', models.BooleanField(default=False)),
                ('is_delete', models.BooleanField(default=False)),
                ('Designation', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='hrm.designation')),
                ('module', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='software_settings.module')),
                ('sub_module', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='software_settings.sub_module')),
            ],
        ),
        migrations.CreateModel(
            name='PaySlip',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('salaryMonth', models.IntegerField(blank=True, default=0, null=True)),
                ('salaryYear', models.IntegerField(blank=True, default=0, null=True)),
                ('publicHoliday', models.IntegerField(blank=True, default=0, null=True)),
                ('leave', models.IntegerField(blank=True, default=0, null=True)),
                ('present', models.IntegerField(blank=True, default=0, null=True)),
                ('absent', models.IntegerField(blank=True, default=0, null=True)),
                ('late', models.IntegerField(blank=True, default=0, null=True)),
                ('dayOverTime', models.IntegerField(blank=True, default=0, null=True)),
                ('nightOverTime', models.IntegerField(blank=True, default=0, null=True)),
                ('overtimeTotal', models.FloatField(blank=True, default=0.0, null=True)),
                ('incentiveTotal', models.FloatField(blank=True, default=0.0, null=True)),
                ('dailyAllowanceTotal', models.FloatField(blank=True, default=0.0, null=True)),
                ('fine', models.FloatField(blank=True, default=0.0, null=True)),
                ('loan_adjustment', models.FloatField(blank=True, default=0.0, null=True)),
                ('advance_adjustment', models.FloatField(blank=True, default=0.0, null=True)),
                ('net_salary', models.FloatField(blank=True, default=0.0, null=True)),
                ('payment', models.FloatField(blank=True, default=0.0, null=True)),
                ('due', models.FloatField(blank=True, default=0.0, null=True)),
                ('amount_1', models.FloatField(blank=True, default=0.0, null=True)),
                ('payment_method_info_1', models.CharField(blank=True, max_length=255, null=True)),
                ('amount_2', models.FloatField(blank=True, default=0.0, null=True)),
                ('payment_method_info_2', models.CharField(blank=True, max_length=255, null=True)),
                ('paymentDate', models.DateTimeField(default=django.utils.timezone.now)),
                ('created', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('modified', models.DateTimeField(default=django.utils.timezone.now)),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='employee_payslip', to='hrm.employee')),
                ('payment_method_1', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='employee_payment_account1', to='accounting.account')),
                ('payment_method_2', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='employee_payment_account2', to='accounting.account')),
                ('salary', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payslip_salary', to='hrm.salary')),
            ],
        ),
        migrations.CreateModel(
            name='OfficeLocation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('OfficeLocation_parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='hrm.officelocation')),
            ],
        ),
        migrations.CreateModel(
            name='Office',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('logo', models.ImageField(blank=True, null=True, upload_to='business/outlet/logo')),
                ('address', models.CharField(blank=True, max_length=500, null=True)),
                ('contact', models.CharField(blank=True, max_length=500, null=True)),
                ('petty_cash', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=20)),
                ('cash', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=20)),
                ('is_outlet', models.BooleanField(blank=True, default=False, null=True)),
                ('is_office', models.BooleanField(blank=True, default=False, null=True)),
                ('is_warehouse', models.BooleanField(blank=True, default=False, null=True)),
                ('Company', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='hrm.company')),
                ('Department', models.ManyToManyField(blank=True, to='hrm.department')),
                ('OfficeLocation', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='hrm.officelocation')),
                ('OfficeType', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='hrm.officetype')),
                ('Office_parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='hrm.office')),
            ],
        ),
        migrations.CreateModel(
            name='LoanPayment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('paidAmount', models.FloatField(blank=True, default=0.0, null=True)),
                ('paymentDate', models.DateTimeField(default=django.utils.timezone.now)),
                ('created', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('modified', models.DateTimeField(default=django.utils.timezone.now)),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='employee_loan_payment', to='hrm.employee')),
                ('loan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='loan_payment_loan', to='hrm.loan')),
            ],
        ),
        migrations.CreateModel(
            name='IncreamentPolicy',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('note', models.CharField(blank=True, max_length=255, null=True)),
                ('created', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('modified', models.DateTimeField(default=django.utils.timezone.now)),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hrm.employee')),
            ],
        ),
        migrations.CreateModel(
            name='EmployeeLeave',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('leaveStart', models.DateField(default=django.utils.timezone.now)),
                ('leaveEnd', models.DateField(default=django.utils.timezone.now)),
                ('leaveDays', models.IntegerField(blank=True, default=0, null=True)),
                ('leaveStatus', models.CharField(default='pending', max_length=255)),
                ('note', models.TextField(blank=True, null=True)),
                ('created', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('modified', models.DateTimeField(default=django.utils.timezone.now)),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='employee_leave', to='hrm.employee')),
                ('leaveType', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='employee_leave_type', to='hrm.leavetype')),
            ],
        ),
        migrations.CreateModel(
            name='EmployeeDocument',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(blank=True, null=True, upload_to=hrm.models.user_files_directory_path)),
                ('note', models.CharField(blank=True, max_length=255, null=True)),
                ('created', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('modified', models.DateTimeField(default=django.utils.timezone.now)),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='hrm_employee_document', to='hrm.employee')),
            ],
        ),
        migrations.AddField(
            model_name='employee',
            name='Office',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='hrm.office'),
        ),
        migrations.AddField(
            model_name='employee',
            name='employee',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='hrm_employee', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='company',
            name='GroupOfCompany',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='hrm.groupofcompany'),
        ),
        migrations.CreateModel(
            name='Attendance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('attendanceDate', models.DateField(default=datetime.date.today)),
                ('shift', models.CharField(default='day', max_length=255)),
                ('isAttended', models.BooleanField(default=False)),
                ('entryTime', models.TimeField(blank=True, null=True)),
                ('exitTime', models.TimeField(blank=True, null=True)),
                ('note', models.CharField(blank=True, default='', max_length=255, null=True)),
                ('overTime', models.FloatField(blank=True, default=0.0, null=True)),
                ('lateTime', models.FloatField(blank=True, default=0.0, null=True)),
                ('isLate', models.BooleanField(default=False)),
                ('created', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('modified', models.DateTimeField(default=django.utils.timezone.now)),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='employee_attendance', to='hrm.employee')),
            ],
        ),
    ]
