# Generated migration for currency update
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('billing', '0004_add_one_time_billing_support'),
    ]

    operations = [
        migrations.AlterField(
            model_name='billingrecord',
            name='currency',
            field=models.CharField(
                default='NPR',
                max_length=3,
                verbose_name='Currency'
            ),
        ),
    ]
