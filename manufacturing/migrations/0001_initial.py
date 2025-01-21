

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('order', '0001_initial'),
        ('product', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductionLine',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('line_name', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('location', models.CharField(max_length=100)),
                ('capacity', models.PositiveIntegerField()),
                ('start_date', models.DateTimeField(blank=True, null=True)),
                ('end_date', models.DateTimeField(blank=True, null=True)),
                ('status', models.CharField(blank=True, default='Pending', max_length=100, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ProductionLine_item',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('capacity', models.PositiveIntegerField()),
                ('start_date', models.DateTimeField(blank=True, null=True)),
                ('end_date', models.DateTimeField(blank=True, null=True)),
                ('status', models.CharField(choices=[('Pending', 'Pending'), ('Working', 'Working'), ('Testing', 'Testing'), ('Complete', 'Complete')], max_length=100, null=True)),
                ('ProductionLine', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='manufacturing.productionline')),
            ],
        ),
        migrations.CreateModel(
            name='WorkOrder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_name', models.CharField(blank=True, max_length=255, null=True)),
                ('order_number', models.CharField(blank=True, max_length=255, null=True)),
                ('start_date', models.DateTimeField(blank=True, null=True)),
                ('end_date', models.DateTimeField(blank=True, null=True)),
                ('quantity_needed', models.IntegerField(blank=True, null=True)),
                ('total_cost', models.DecimalField(decimal_places=2, max_digits=10, null=True)),
                ('status', models.CharField(blank=True, default='Pending', max_length=100, null=True)),
                ('Product', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='product.productdetails')),
                ('draft_cost_sheet', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='order.draftcostsheet')),
            ],
        ),
        migrations.CreateModel(
            name='Workstation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('workstation_name', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('status', models.CharField(blank=True, default='Pending', max_length=100, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='WorkstationStatus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('task_name', models.CharField(max_length=100)),
                ('status', models.CharField(choices=[('New', 'New'), ('Proposed', 'Proposed'), ('Confirm', 'Confirm'), ('Solved', 'Solved')], max_length=100, null=True)),
                ('workstation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='manufacturing.workstation')),
            ],
        ),
        migrations.CreateModel(
            name='WorkstationItems',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ProductionLine', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='manufacturing.productionline')),
                ('Workstation', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='manufacturing.workstation')),
            ],
        ),
        migrations.CreateModel(
            name='WorkOrderItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity_needed', models.IntegerField(default=0)),
                ('Attributes', models.ManyToManyField(blank=True, related_name='AttributeTerm', related_query_name='AttributeTerm', to='product.attributeterm')),
                ('Workorder', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='manufacturing.workorder')),
            ],
        ),
        migrations.CreateModel(
            name='QualityTestStatus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('Block', 'Block'), ('Quality', 'Quality'), ('Scrap', 'Scrap'), ('Maintenance', 'Maintenance')], max_length=100, null=True)),
                ('ProductionLine_item', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='manufacturing.productionline_item')),
                ('order', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='manufacturing.workorder')),
            ],
        ),
        migrations.CreateModel(
            name='QualityTest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('test_date', models.DateField()),
                ('pass_fail_status', models.BooleanField()),
                ('notes', models.TextField()),
                ('test_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='manufacturing.qualityteststatus')),
            ],
        ),
        migrations.AddField(
            model_name='productionline_item',
            name='WorkOrderItem',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='manufacturing.workorderitem'),
        ),
        migrations.AddField(
            model_name='productionline_item',
            name='Workorder',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='manufacturing.workorder'),
        ),
        migrations.CreateModel(
            name='ManufacturingRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('notes', models.TextField()),
                ('line', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='manufacturing.productionline')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='manufacturing.workorder')),
                ('workstation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='manufacturing.workstation')),
            ],
        ),
        migrations.CreateModel(
            name='Manufacture_Cost',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('Fabrics', 'Fabrics'), ('Trims/Accessories', 'Trims/Accessories'), ('Labor Cost', 'Labor Cost')], max_length=100, null=True)),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True, null=True)),
                ('unit_name', models.CharField(blank=True, max_length=10, null=True)),
                ('quantity', models.PositiveIntegerField()),
                ('cost_per_unit', models.DecimalField(decimal_places=2, max_digits=10, null=True)),
                ('total_cost', models.DecimalField(decimal_places=2, max_digits=10, null=True)),
                ('Product', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='product.productdetails')),
                ('ProductLocation', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='product.productlocation')),
                ('ProductionLine', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='manufacturing.productionline')),
                ('ProductionLine_item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='manufacturing.productionline_item')),
            ],
        ),
    ]
