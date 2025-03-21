# Generated by Django 5.1.7 on 2025-03-14 11:07

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='annual_revenue',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True),
        ),
        migrations.AddField(
            model_name='customer',
            name='business_type',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='customer',
            name='compliance_status',
            field=models.CharField(choices=[('pending', 'Pending'), ('compliant', 'Compliant'), ('non_compliant', 'Non-Compliant'), ('review_required', 'Review Required')], default='pending', max_length=20),
        ),
        migrations.AddField(
            model_name='customer',
            name='country_code',
            field=models.CharField(default='GB', max_length=2),
        ),
        migrations.AddField(
            model_name='customer',
            name='customer_type',
            field=models.CharField(choices=[('personal', 'Personal'), ('business', 'Business')], default='personal', max_length=20),
        ),
        migrations.AddField(
            model_name='riskassessment',
            name='assessment_type',
            field=models.CharField(choices=[('initial', 'Initial Assessment'), ('periodic', 'Periodic Review'), ('triggered', 'Triggered Review')], default=1200, max_length=20),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='riskassessment',
            name='next_review_date',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='riskassessment',
            name='reviewed_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='risk_assessments', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='transaction',
            name='destination_country',
            field=models.CharField(default='GB', max_length=2),
        ),
        migrations.AddField(
            model_name='transaction',
            name='reference',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='transaction',
            name='screening_status',
            field=models.CharField(choices=[('pending', 'Pending'), ('cleared', 'Cleared'), ('flagged', 'Flagged'), ('blocked', 'Blocked')], default='pending', max_length=20),
        ),
        migrations.AddField(
            model_name='transaction',
            name='source_country',
            field=models.CharField(default='GB', max_length=2),
        ),
        migrations.AddField(
            model_name='verificationdocument',
            name='document_number',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='verificationdocument',
            name='expiry_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='verificationdocument',
            name='issuing_country',
            field=models.CharField(default='GB', max_length=2),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='transaction_type',
            field=models.CharField(choices=[('deposit', 'Deposit'), ('withdrawal', 'Withdrawal'), ('transfer', 'Transfer'), ('payment', 'Payment')], max_length=50),
        ),
        migrations.AlterField(
            model_name='verificationdocument',
            name='document_type',
            field=models.CharField(choices=[('passport', 'Passport'), ('driving_license', 'Driving License'), ('national_id', 'National ID'), ('business_reg', 'Business Registration'), ('aml_policy', 'AML Policy'), ('financial_statement', 'Financial Statement')], max_length=50),
        ),
        migrations.AlterField(
            model_name='verificationdocument',
            name='verification_notes',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='verificationdocument',
            name='verification_status',
            field=models.CharField(choices=[('pending', 'Pending'), ('verified', 'Verified'), ('rejected', 'Rejected'), ('expired', 'Expired')], default='pending', max_length=20),
        ),
    ]
