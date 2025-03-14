from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from datetime import datetime

class CustomerType(models.TextChoices):
    PERSONAL = 'personal', _('Personal')
    BUSINESS = 'business', _('Business')

class DocumentType(models.TextChoices):
    PASSPORT = 'passport', _('Passport')
    DRIVING_LICENSE = 'driving_license', _('Driving License')
    NATIONAL_ID = 'national_id', _('National ID')
    BUSINESS_REG = 'business_reg', _('Business Registration')
    AML_POLICY = 'aml_policy', _('AML Policy')
    FINANCIAL_STATEMENT = 'financial_statement', _('Financial Statement')

class Customer(models.Model):
    """Customer model for AML service.
    
    Stores customer information and compliance status for both personal
    and business customers as required by AML regulations.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    customer_type = models.CharField(
        max_length=20,
        choices=CustomerType.choices,
        default=CustomerType.PERSONAL
    )
    risk_score = models.FloatField(default=0.0)
    last_verification_date = models.DateTimeField(null=True)
    is_verified = models.BooleanField(default=False)
    country_code = models.CharField(max_length=2, default='GB')
    business_type = models.CharField(max_length=100, null=True, blank=True)
    annual_revenue = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True
    )
    compliance_status = models.CharField(
        max_length=20,
        default='pending',
        choices=[
            ('pending', _('Pending')),
            ('compliant', _('Compliant')),
            ('non_compliant', _('Non-Compliant')),
            ('review_required', _('Review Required'))
        ]
    )
    
    def __str__(self):
        return f"{self.user.username} ({self.customer_type})"

class Transaction(models.Model):
    """Transaction model for monitoring financial activities.
    
    Implements comprehensive transaction monitoring with risk scoring
    and suspicious activity detection as per AML guidelines.
    """
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)
    transaction_type = models.CharField(
        max_length=50,
        choices=[
            ('deposit', _('Deposit')),
            ('withdrawal', _('Withdrawal')),
            ('transfer', _('Transfer')),
            ('payment', _('Payment'))
        ]
    )
    risk_score = models.FloatField(default=0.0)
    is_suspicious = models.BooleanField(default=False)
    source_country = models.CharField(max_length=2, default='GB')
    destination_country = models.CharField(max_length=2, default='GB')
    reference = models.CharField(max_length=100, null=True, blank=True)
    screening_status = models.CharField(
        max_length=20,
        default='pending',
        choices=[
            ('pending', _('Pending')),
            ('cleared', _('Cleared')),
            ('flagged', _('Flagged')),
            ('blocked', _('Blocked'))
        ]
    )
    
    def __str__(self):
        return f"{self.transaction_type} of {self.amount} by {self.customer.user.username}"

class RiskAssessment(models.Model):
    """Risk Assessment model for customer risk profiling.
    
    Implements comprehensive risk assessment framework including
    initial, periodic, and triggered reviews as required by AML regulations.
    """
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    assessment_date = models.DateTimeField(auto_now_add=True)
    risk_factors = models.JSONField()
    overall_score = models.FloatField()
    recommendations = models.TextField()
    assessment_type = models.CharField(
        max_length=20,
        choices=[
            ('initial', _('Initial Assessment')),
            ('periodic', _('Periodic Review')),
            ('triggered', _('Triggered Review'))
        ]
    )
    next_review_date = models.DateTimeField(null=True)
    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='risk_assessments'
    )
    
    def __str__(self):
        return f"Risk Assessment for {self.customer.user.username} on {self.assessment_date.date()}"

class VerificationDocument(models.Model):
    """Document verification model for KYC process.
    
    Handles various types of identity and business documents
    required for customer verification as per AML guidelines.
    """
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    document_type = models.CharField(
        max_length=50,
        choices=DocumentType.choices
    )
    upload_date = models.DateTimeField(auto_now_add=True)
    expiry_date = models.DateTimeField(null=True, blank=True)
    verification_status = models.CharField(
        max_length=20,
        default='pending',
        choices=[
            ('pending', _('Pending')),
            ('verified', _('Verified')),
            ('rejected', _('Rejected')),
            ('expired', _('Expired'))
        ]
    )
    verification_notes = models.TextField(blank=True)
    document_number = models.CharField(max_length=100, null=True, blank=True)
    issuing_country = models.CharField(max_length=2, default='GB')
    
    def __str__(self):
        return f"{self.document_type} for {self.customer.user.username}"

# Create your models here.
