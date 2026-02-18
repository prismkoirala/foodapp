# Generated migration for PromoPhoneNumber model

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('menu', '0006_restaurant_view_menu_count'),
        ('profiles', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PromoPhoneNumber',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone_number', models.CharField(help_text='Phone number for promo notifications', max_length=15)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('restaurant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='promo_phone_numbers', to='menu.restaurant')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddConstraint(
            model_name='promophonenumber',
            constraint=models.UniqueConstraint(fields=['phone_number', 'restaurant'], name='unique_promo_phone_per_restaurant'),
        ),
    ]
