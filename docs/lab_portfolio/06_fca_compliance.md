# Lab Portfolio - FCA License Application Requirements

## Exercise 6: Implementing FCA Compliance Features

This exercise demonstrates the implementation of specific features required for FCA license applications in the AML service, focusing on regulatory compliance and reporting.

### 1. Compliance Reporting System

```python
from django.db import models
from django.utils import timezone
from datetime import timedelta

class ComplianceReport(models.Model):
    """
    Compliance reporting system for FCA requirements.
    Generates and manages regulatory reports.
    """
    class ReportType(models.TextChoices):
        SAR = 'sar', 'Suspicious Activity Report'
        AML = 'aml', 'AML Compliance Report'
        KYC = 'kyc', 'KYC Verification Report'
        RISK = 'risk', 'Risk Assessment Report'
        
    report_type = models.CharField(
        max_length=20,
        choices=ReportType.choices
    )
    
    generated_date = models.DateTimeField(auto_now_add=True)
    reporting_period_start = models.DateTimeField()
    reporting_period_end = models.DateTimeField()
    
    # Report content
    content = models.JSONField()
    
    # Submission status
    class SubmissionStatus(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        PENDING = 'pending', 'Pending Review'
        SUBMITTED = 'submitted', 'Submitted to FCA'
        ACCEPTED = 'accepted', 'Accepted by FCA'
        REJECTED = 'rejected', 'Rejected by FCA'
        
    status = models.CharField(
        max_length=20,
        choices=SubmissionStatus.choices,
        default=SubmissionStatus.DRAFT
    )
    
    # Approval tracking
    approved_by = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='approved_reports'
    )
    approval_date = models.DateTimeField(null=True)
    
    def generate_report_content(self):
        """Generate report content based on type."""
        if self.report_type == self.ReportType.SAR:
            return self._generate_sar_report()
        elif self.report_type == self.ReportType.AML:
            return self._generate_aml_report()
        elif self.report_type == self.ReportType.KYC:
            return self._generate_kyc_report()
        elif self.report_type == self.ReportType.RISK:
            return self._generate_risk_report()
            
    def _generate_sar_report(self):
        """Generate Suspicious Activity Report."""
        suspicious_transactions = Transaction.objects.filter(
            timestamp__range=(
                self.reporting_period_start,
                self.reporting_period_end
            ),
            is_suspicious=True
        )
        
        return {
            'report_type': 'SAR',
            'total_suspicious_transactions': suspicious_transactions.count(),
            'total_value': float(
                suspicious_transactions.aggregate(
                    Sum('amount')
                )['amount__sum'] or 0
            ),
            'transactions': [
                {
                    'id': t.id,
                    'amount': float(t.amount),
                    'date': t.timestamp.isoformat(),
                    'risk_score': t.risk_score,
                    'flags': t.get_risk_flags()
                }
                for t in suspicious_transactions
            ]
        }
```

### 2. FCA Compliance Monitoring

```python
class ComplianceMonitor:
    """
    Real-time compliance monitoring system.
    Ensures adherence to FCA requirements.
    """
    def __init__(self):
        self.requirements = self._load_fca_requirements()
        
    def _load_fca_requirements(self):
        """Load FCA compliance requirements."""
        return {
            'customer_due_diligence': {
                'required_documents': [
                    'identity_proof',
                    'address_proof',
                    'source_of_funds'
                ],
                'verification_frequency': 365,  # days
                'risk_assessment_frequency': 180  # days
            },
            'transaction_monitoring': {
                'screening_threshold': 10000,  # GBP
                'reporting_threshold': 15000,  # GBP
                'high_risk_threshold': 50000   # GBP
            },
            'reporting_requirements': {
                'sar_deadline': 30,  # days
                'compliance_report_frequency': 90,  # days
                'risk_assessment_update': 180  # days
            }
        }
        
    def check_customer_compliance(self, customer):
        """Check customer compliance status."""
        requirements = self.requirements['customer_due_diligence']
        
        # Check document completeness
        documents = VerificationDocument.objects.filter(customer=customer)
        missing_docs = set(requirements['required_documents']) - set(
            documents.values_list('document_type', flat=True)
        )
        
        # Check document validity
        expired_docs = documents.filter(
            expiry_date__lt=timezone.now()
        )
        
        # Check risk assessment
        latest_assessment = customer.riskassessment_set.latest('assessment_date')
        assessment_age = (
            timezone.now() - latest_assessment.assessment_date
        ).days
        
        return {
            'is_compliant': not missing_docs and not expired_docs.exists(),
            'missing_documents': list(missing_docs),
            'expired_documents': list(expired_docs),
            'risk_assessment_status': 'expired' if assessment_age > \
                requirements['risk_assessment_frequency'] else 'valid',
            'next_review_date': timezone.now() + timedelta(
                days=requirements['verification_frequency']
            )
        }
```

### 3. Regulatory Reporting API

```python
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

class RegulatoryReportingViewSet(viewsets.ModelViewSet):
    """
    API endpoints for regulatory reporting.
    """
    queryset = ComplianceReport.objects.all()
    serializer_class = ComplianceReportSerializer
    
    @action(detail=False, methods=['post'])
    def generate_sar(self, request):
        """Generate Suspicious Activity Report."""
        transaction_id = request.data.get('transaction_id')
        try:
            transaction = Transaction.objects.get(id=transaction_id)
            report = ComplianceReport.objects.create(
                report_type=ComplianceReport.ReportType.SAR,
                reporting_period_start=transaction.timestamp,
                reporting_period_end=transaction.timestamp
            )
            report.content = report.generate_report_content()
            report.save()
            return Response({
                'status': 'success',
                'report_id': report.id
            })
        except Transaction.DoesNotExist:
            return Response({
                'status': 'error',
                'message': 'Transaction not found'
            }, status=404)
            
    @action(detail=True, methods=['post'])
    def submit_to_fca(self, request, pk=None):
        """Submit report to FCA."""
        report = self.get_object()
        try:
            # Simulate FCA submission
            submission_result = self._submit_to_fca_api(report)
            if submission_result['success']:
                report.status = ComplianceReport.SubmissionStatus.SUBMITTED
                report.save()
                return Response({
                    'status': 'success',
                    'message': 'Report submitted to FCA'
                })
            else:
                return Response({
                    'status': 'error',
                    'message': submission_result['error']
                }, status=400)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=500)
```

### 4. FCA Compliance Dashboard

```python
class ComplianceDashboard:
    """
    Dashboard for monitoring FCA compliance status.
    """
    def __init__(self):
        self.monitor = ComplianceMonitor()
        
    def get_compliance_metrics(self):
        """Get overall compliance metrics."""
        return {
            'customer_compliance': self._get_customer_compliance_metrics(),
            'transaction_monitoring': self._get_transaction_metrics(),
            'reporting_status': self._get_reporting_metrics(),
            'risk_assessment': self._get_risk_assessment_metrics()
        }
        
    def _get_customer_compliance_metrics(self):
        """Get customer compliance metrics."""
        customers = Customer.objects.all()
        total = customers.count()
        compliant = sum(
            1 for c in customers
            if self.monitor.check_customer_compliance(c)['is_compliant']
        )
        
        return {
            'total_customers': total,
            'compliant_customers': compliant,
            'compliance_rate': (compliant / total * 100) if total > 0 else 0,
            'pending_reviews': customers.filter(
                last_review__lt=timezone.now() - timedelta(days=365)
            ).count()
        }
        
    def _get_transaction_metrics(self):
        """Get transaction monitoring metrics."""
        recent_transactions = Transaction.objects.filter(
            timestamp__gte=timezone.now() - timedelta(days=30)
        )
        
        return {
            'total_transactions': recent_transactions.count(),
            'suspicious_transactions': recent_transactions.filter(
                is_suspicious=True
            ).count(),
            'high_value_transactions': recent_transactions.filter(
                amount__gt=50000
            ).count(),
            'pending_reviews': recent_transactions.filter(
                screening_status='pending'
            ).count()
        }
        
    def _get_reporting_metrics(self):
        """Get regulatory reporting metrics."""
        reports = ComplianceReport.objects.filter(
            generated_date__gte=timezone.now() - timedelta(days=90)
        )
        
        return {
            'total_reports': reports.count(),
            'submitted_reports': reports.filter(
                status=ComplianceReport.SubmissionStatus.SUBMITTED
            ).count(),
            'pending_reports': reports.filter(
                status=ComplianceReport.SubmissionStatus.PENDING
            ).count(),
            'rejected_reports': reports.filter(
                status=ComplianceReport.SubmissionStatus.REJECTED
            ).count()
        }
```

### Learning Outcomes

1. **FCA Requirements**
   - Compliance reporting
   - Regulatory submissions
   - Monitoring systems
   - Documentation standards

2. **Compliance Implementation**
   - Report generation
   - Status monitoring
   - Submission handling
   - Metrics tracking

3. **Regulatory Integration**
   - FCA submission process
   - Compliance validation
   - Status tracking
   - Error handling

### Next Steps

1. Enhance reporting capabilities
2. Implement additional FCA requirements
3. Improve compliance monitoring
4. Develop automated reporting
