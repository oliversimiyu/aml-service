from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from .models import Customer, Transaction, RiskAssessment, VerificationDocument

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('user', 'customer_type', 'risk_score_display', 'compliance_status', 'is_verified')
    list_filter = ('customer_type', 'compliance_status', 'is_verified', 'country_code')
    search_fields = ('user__username', 'user__email', 'business_type')
    readonly_fields = ('risk_score',)
    
    def risk_score_display(self, obj):
        score = obj.risk_score
        if score >= 0.7:
            color = 'red'
        elif score >= 0.3:
            color = 'orange'
        else:
            color = 'green'
        return format_html('<span style="color: {};"><b>{}%</b></span>', 
                         color, int(score * 100))
    risk_score_display.short_description = 'Risk Score'

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('customer', 'transaction_type', 'amount', 'timestamp', 
                   'is_suspicious', 'screening_status')
    list_filter = ('transaction_type', 'is_suspicious', 'screening_status', 
                  'source_country', 'destination_country')
    search_fields = ('customer__user__username', 'reference')
    readonly_fields = ('risk_score',)
    ordering = ('-timestamp',)
    
    fieldsets = (
        ('Transaction Details', {
            'fields': ('customer', 'amount', 'transaction_type', 'reference')
        }),
        ('Risk Information', {
            'fields': ('risk_score', 'is_suspicious', 'screening_status')
        }),
        ('Geographic Information', {
            'fields': ('source_country', 'destination_country')
        }),
    )

@admin.register(RiskAssessment)
class RiskAssessmentAdmin(admin.ModelAdmin):
    list_display = ('customer', 'assessment_date', 'overall_score_display', 
                   'assessment_type', 'next_review_date')
    list_filter = ('assessment_type', 'assessment_date')
    search_fields = ('customer__user__username',)
    readonly_fields = ('assessment_date',)
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if 'risk_factors' in form.base_fields:
            form.base_fields['risk_factors'].initial = {
                "pep_status": False,
                "high_risk_jurisdiction": False,
                "complex_ownership": False,
                "suspicious_activity": False,
                "high_risk_business": False,
                "sanctions_match": False,
                "transaction_monitoring": {
                    "high_value_transactions": False,
                    "unusual_patterns": False,
                    "high_risk_countries": []
                },
                "customer_profile": {
                    "business_type": "",
                    "jurisdiction": "GB",
                    "client_category": "standard"
                }
            }
            form.base_fields['risk_factors'].help_text = (
                'Enter risk factors as JSON. Example structure shown. '
                'Modify values but maintain the structure. '
                'Use true/false for boolean fields.'
            )
        return form
    
    def overall_score_display(self, obj):
        score = obj.overall_score
        if score >= 0.7:
            color = 'red'
            risk_level = 'High Risk'
        elif score >= 0.3:
            color = 'orange'
            risk_level = 'Medium Risk'
        else:
            color = 'green'
            risk_level = 'Low Risk'
        return format_html('<span style="color: {};"><b>{}%</b> ({})</span>', 
                         color, int(score * 100), risk_level)
    overall_score_display.short_description = 'Risk Level'

@admin.register(VerificationDocument)
class VerificationDocumentAdmin(admin.ModelAdmin):
    list_display = ('customer', 'document_type', 'upload_date', 
                   'verification_status', 'expiry_status')
    list_filter = ('document_type', 'verification_status', 'issuing_country')
    search_fields = ('customer__user__username', 'document_number')
    readonly_fields = ('upload_date',)
    
    def expiry_status(self, obj):
        if not obj.expiry_date:
            return '-'
        from django.utils import timezone
        if obj.expiry_date < timezone.now():
            return format_html('<span style="color: red;"><b>Expired</b></span>')
        elif (obj.expiry_date - timezone.now()).days <= 30:
            return format_html('<span style="color: orange;"><b>Expiring Soon</b></span>')
        return format_html('<span style="color: green;"><b>Valid</b></span>')
    expiry_status.short_description = 'Expiry Status'

# Customize admin site header and title
admin.site.site_header = 'AML Service Administration'
admin.site.site_title = 'AML Service Admin Portal'
admin.site.index_title = 'Anti-Money Laundering Service Management'
