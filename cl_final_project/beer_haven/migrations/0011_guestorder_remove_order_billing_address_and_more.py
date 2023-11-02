# Generated by Django 4.2.6 on 2023-11-01 18:31

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('beer_haven', '0010_order_alter_useraddress_options_orderitem_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='GuestOrder',
            fields=[
                ('order_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='beer_haven.order')),
                ('guest_first_name', models.CharField(max_length=64)),
                ('guest_last_name', models.CharField(max_length=64)),
                ('guest_email', models.EmailField(max_length=254, unique=True)),
                ('guest_billing_address', models.CharField(blank=True, max_length=255, null=True)),
                ('guest_shipping_address', models.CharField(max_length=255)),
                ('guest_postal_code', models.CharField(max_length=6)),
                ('guest_city', models.CharField(blank=True, max_length=128, null=True)),
            ],
            bases=('beer_haven.order',),
        ),
        migrations.RemoveField(
            model_name='order',
            name='billing_address',
        ),
        migrations.RemoveField(
            model_name='order',
            name='shipping_address',
        ),
        migrations.RemoveField(
            model_name='order',
            name='user',
        ),
        migrations.RemoveField(
            model_name='orderitem',
            name='order',
        ),
        migrations.CreateModel(
            name='UserOrder',
            fields=[
                ('order_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='beer_haven.order')),
                ('billing_address', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='order_billing_addr', to='beer_haven.useraddress')),
                ('shipping_address', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='order_shipping_addr', to='beer_haven.useraddress')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='order_user', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created'],
            },
            bases=('beer_haven.order',),
        ),
        migrations.CreateModel(
            name='UserOrderItem',
            fields=[
                ('orderitem_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='beer_haven.orderitem')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='beer_haven.userorder')),
            ],
            bases=('beer_haven.orderitem',),
        ),
        migrations.CreateModel(
            name='GuestOrderItem',
            fields=[
                ('orderitem_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='beer_haven.orderitem')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='beer_haven.guestorder')),
            ],
            bases=('beer_haven.orderitem',),
        ),
    ]
