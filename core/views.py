from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Avg, Q
from django.utils import timezone
from datetime import timedelta
from django.http import JsonResponse
from django.core.exceptions import PermissionDenied
from .models import Customer, Transaction, RiskAssessment, VerificationDocument

@login_required
def dashboard(request):
    """Main dashboard view showing AML compliance metrics and recent activity."""
    now = timezone.now()
    thirty_days_ago = now - timedelta(days=30)
    
    # Risk metrics
    high_risk_count = Customer.objects.filter(risk_score__gte=0.7).count()
    suspicious_transactions = Transaction.objects.filter(
        timestamp__gte=thirty_days_ago,
        is_suspicious=True
    ).count()
    pending_verifications = VerificationDocument.objects.filter(
        verification_status='pending'
    ).count()
    
    # Risk distribution
    total_customers = Customer.objects.count()
    risk_distribution = {
        'low': Customer.objects.filter(risk_score__lt=0.3).count(),
        'medium': Customer.objects.filter(risk_score__gte=0.3, risk_score__lt=0.7).count(),
        'high': high_risk_count
    }
    
    # Transaction trend data (last 7 days)
    transaction_data = Transaction.objects.filter(
        timestamp__gte=now - timedelta(days=7)
    ).values('timestamp__date').annotate(
        volume=Count('id')
    ).order_by('timestamp__date')
    
    transaction_dates = [str(data['timestamp__date']) for data in transaction_data]
    transaction_volumes = [data['volume'] for data in transaction_data]
    
    # Recent activity
    recent_activities = []
    
    # Add recent transactions
    recent_transactions = Transaction.objects.filter(
        timestamp__gte=thirty_days_ago
    ).order_by('-timestamp')[:5]
    for trans in recent_transactions:
        status = 'flagged' if trans.is_suspicious else 'cleared'
        recent_activities.append({
            'timestamp': trans.timestamp,
            'type': 'Transaction',
            'details': f'{trans.transaction_type} of £{trans.amount}',
            'status': status
        })
    
    # Add recent verifications
    recent_verifications = VerificationDocument.objects.filter(
        upload_date__gte=thirty_days_ago
    ).order_by('-upload_date')[:5]
    for doc in recent_verifications:
        recent_activities.append({
            'timestamp': doc.upload_date,
            'type': 'Document Verification',
            'details': f'{doc.document_type} for {doc.customer.user.username}',
            'status': doc.verification_status
        })
    
    # Add recent risk assessments
    recent_assessments = RiskAssessment.objects.filter(
        assessment_date__gte=thirty_days_ago
    ).order_by('-assessment_date')[:5]
    for assessment in recent_assessments:
        status = 'high' if assessment.overall_score >= 0.7 else 'medium' if assessment.overall_score >= 0.3 else 'low'
        recent_activities.append({
            'timestamp': assessment.assessment_date,
            'type': 'Risk Assessment',
            'details': f'Score: {assessment.overall_score:.2f}',
            'status': status
        })
    
    # Sort all activities by timestamp
    recent_activities.sort(key=lambda x: x['timestamp'], reverse=True)
    recent_activities = recent_activities[:10]
    
    context = {
        'high_risk_count': high_risk_count,
        'suspicious_transactions_count': suspicious_transactions,
        'pending_verifications_count': pending_verifications,
        'risk_distribution': risk_distribution,
        'transaction_dates': transaction_dates,
        'transaction_volumes': transaction_volumes,
        'recent_activities': recent_activities,
        'last_update': now
    }
    
    return render(request, 'dashboard.html', context)

@login_required
def customer_list(request):
    """View for listing all customers with their risk profiles."""
    customers = Customer.objects.all().order_by('-risk_score')
    return render(request, 'customers.html', {'customers': customers})

@login_required
def transaction_list(request):
    """View for listing all transactions with ML-based risk analysis."""
    transactions = Transaction.objects.all().order_by('-timestamp')
    return render(request, 'transactions.html', {'transactions': transactions})

@login_required
def document_list(request):
    """View for listing all verification documents."""
    documents = VerificationDocument.objects.all().order_by('-upload_date')
    return render(request, 'documents.html', {
        'documents': documents,
        'now': timezone.now()
    })

@login_required
def risk_assessment_list(request):
    """View for listing all risk assessments."""
    assessments = RiskAssessment.objects.all().order_by('-assessment_date')
    return render(request, 'risk_assessments.html', {
        'assessments': assessments,
        'now': timezone.now()
    })
