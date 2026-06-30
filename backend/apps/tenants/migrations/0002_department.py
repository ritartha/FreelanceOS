# Generated manually to match Department + Membership.department addition

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tenants', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Department',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('tenant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='departments', to='tenants.tenant')),
            ],
            options={
                'db_table': 'tenants_department',
            },
        ),
        migrations.AddField(
            model_name='department',
            name='lead',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='led_departments', to='tenants.membership'),
        ),
        migrations.AddConstraint(
            model_name='department',
            constraint=models.UniqueConstraint(fields=('tenant', 'name'), name='uniq_tenant_department_name'),
        ),
        migrations.AddField(
            model_name='membership',
            name='department',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='memberships', to='tenants.department'),
        ),
    ]
