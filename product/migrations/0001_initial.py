

from django.db import migrations, models
import django.db.models.deletion
import product.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('hrm', '0001_initial'),
        ('contact', '0001_initial'),
        ('hrm', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Attribute',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('slug', models.CharField(blank=True, max_length=255, null=True)),
                ('context', models.CharField(blank=True, max_length=255, null=True)),
                ('data', models.JSONField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='AttributeTerm',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('slug', models.CharField(blank=True, max_length=255, null=True)),
                ('context', models.CharField(blank=True, max_length=255, null=True)),
                ('data', models.JSONField(blank=True, null=True)),
                ('Attribute', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='product.attribute')),
            ],
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('slug', models.CharField(blank=True, max_length=255, null=True, unique=True)),
                ('data', models.JSONField(blank=True, null=True)),
                ('Category_parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='product.category')),
            ],
        ),
        migrations.CreateModel(
            name='ProductDetails',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('slug', models.CharField(blank=True, max_length=255, null=True, unique=True)),
                ('Short_description', models.TextField(blank=True, null=True)),
                ('tags', models.CharField(blank=True, max_length=255, null=True)),
                ('stock_unit', models.CharField(blank=True, max_length=255, null=True)),
                ('stock_alart_amount', models.IntegerField(blank=True, null=True)),
                ('height', models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True)),
                ('width', models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True)),
                ('weight', models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True)),
                ('discount_type', models.CharField(blank=True, max_length=255, null=True)),
                ('discount', models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True)),
                ('tax', models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True)),
                ('is_active', models.BooleanField(blank=True, default=False, null=True)),
                ('product_code', models.CharField(blank=True, max_length=255, null=True)),
                ('quantity', models.IntegerField(default=0)),
                ('min_price', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=20)),
                ('max_price', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=20)),
                ('data', models.JSONField(blank=True, null=True)),
                ('Category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='Product_Category', related_query_name='Product_Category', to='product.category')),
                ('Merchandiser', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='contact.contact')),
                ('Sub_Category', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='Product_Sub_Category', related_query_name='Product_Sub_Category', to='product.category')),
            ],
        ),
        migrations.CreateModel(
            name='ProductLocation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(blank=True, max_length=2000, null=True)),
                ('Attribute_details', models.CharField(blank=True, max_length=2000, null=True)),
                ('quantity', models.IntegerField(default=0)),
                ('purchase_price', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=20)),
                ('selling_price', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=20)),
                ('price', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=20)),
                ('barcode', models.CharField(blank=True, max_length=255, null=True)),
                ('Attributes', models.ManyToManyField(blank=True, related_name='Attributes', related_query_name='Attributes', to='product.attributeterm')),
                ('ProductDetails', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='product.productdetails')),
                ('Warehouse', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hrm.office')),
            ],
        ),
        migrations.CreateModel(
            name='transfer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reference', models.CharField(blank=True, max_length=255, null=True)),
                ('tansfer_number', models.CharField(blank=True, max_length=255, null=True)),
                ('issue_date', models.DateField(auto_now_add=True)),
                ('status', models.CharField(blank=True, max_length=255)),
                ('deatils', models.CharField(blank=True, max_length=2550)),
                ('data', models.JSONField(blank=True, null=True)),
                ('destance', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='destance', related_query_name='destance', to='hrm.office')),
                ('source', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='source', related_query_name='source', to='hrm.office')),
            ],
        ),
        migrations.CreateModel(
            name='Warehouse',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('logo', models.ImageField(blank=True, null=True, upload_to='business/outlet/logo')),
                ('logoWidth', models.CharField(blank=True, max_length=500, null=True)),
                ('logoHeight', models.CharField(blank=True, max_length=500, null=True)),
                ('name', models.CharField(max_length=255)),
                ('address', models.CharField(blank=True, max_length=500, null=True)),
                ('contact', models.CharField(blank=True, max_length=500, null=True)),
                ('petty_cash', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=20)),
                ('cash', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=20)),
                ('is_outlet', models.BooleanField(blank=True, default=False, null=True)),
                ('is_office', models.BooleanField(blank=True, default=False, null=True)),
                ('data', models.JSONField(blank=True, null=True)),
                ('Warehouse_parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='product.warehouse')),
            ],
        ),
        migrations.CreateModel(
            name='transfer_item',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField(blank=True, default='1', null=True)),
                ('is_received', models.BooleanField(blank=True, default=False, null=True)),
                ('issue_date', models.DateField(auto_now_add=True)),
                ('data', models.JSONField(blank=True, null=True)),
                ('product', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='product.productlocation')),
                ('transfer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='product.transfer')),
            ],
        ),
        migrations.CreateModel(
            name='ProductImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('photo', models.ImageField(null=True, upload_to=product.models.product_image_file_path)),
                ('is_active', models.BooleanField(blank=True, default=True, null=True)),
                ('Color', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='product.attributeterm')),
                ('ProductDetails', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='product.productdetails')),
                ('ProductLocation', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='product.productlocation')),
            ],
        ),
    ]
