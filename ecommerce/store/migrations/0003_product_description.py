# Generated by Django 3.0.7 on 2020-06-20 03:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0002_product_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='description',
            field=models.CharField(default=False, max_length=1000),
        ),
    ]