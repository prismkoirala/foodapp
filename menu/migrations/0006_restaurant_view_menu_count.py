# Generated migration for adding view_menu_count to Restaurant model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('menu', '0005_menucategory_is_disabled'),
    ]

    operations = [
        migrations.AddField(
            model_name='restaurant',
            name='view_menu_count',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
