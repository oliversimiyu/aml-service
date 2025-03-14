"""API views for regulatory compliance and reporting."""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from core.compliance import (
    RegulatoryReporting, ComplianceRules, PSRCompliance,
    ReportType, ComplianceAlert
)
from core.models import Customer, Transaction
from django.shortcuts import get_object_or_404
from datetime import datetime, timedelta
from typing import List, Dict
import json

class ComplianceViewSet(viewsets.ViewSet):
    """ViewSet for handling regulatory compliance and reporting."""
    
    permission_classes = [IsAuthenticated]
    regulatory_reporting = RegulatoryReporting()
    psr_compliance = PSRCompliance()
    
    @action(detail=False, methods=['post'])
    def evaluate_transaction(self, request):
        """Evaluate a transaction for regulatory reporting requirements."""
        transaction_id = request.data.get('transaction_id')
        transaction = get_object_or_404(Transaction, id=transaction_id)
        
        alerts = self.regulatory_reporting.evaluate_transaction(transaction)
        return Response({
            'transaction_id': transaction_id,
            'alerts': [vars(alert) for alert in alerts],
            'timestamp': datetime.now().isoformat()
        })
    
    @action(detail=True, methods=['get'])
    def customer_risk_assessment(self, request, pk=None):
        """Get comprehensive risk assessment for a customer."""
        customer = get_object_or_404(Customer, id=pk)
        risk_factors = ComplianceRules.evaluate_customer_risk(customer)
        
        # Get customer's country warnings
        customer_data = {
            'country_code': customer.country_code,
            'customer_type': customer.customer_type
        }
        country_warnings = ComplianceRules.check_high_risk_countries(customer_data)
        
        return Response({
            'customer_id': customer.id,
            'risk_factors': risk_factors,
            'country_warnings': country_warnings,
            'overall_risk_score': sum(risk_factors.values()) / len(risk_factors),
            'timestamp': datetime.now().isoformat()
        })
    
    @action(detail=True, methods=['post'])
    def verify_license_requirements(self, request, pk=None):
        """Verify if customer meets PSR license requirements."""
        customer = get_object_or_404(Customer, id=pk)
        customer_type = request.data.get('customer_type', 'personal')
        documents = request.data.get('documents', [])
        
        verification_result = self.psr_compliance.verify_license_requirements(
            customer_type, documents
        )
        
        if verification_result['complete']:
            compliance_report = self.psr_compliance.generate_compliance_report(customer)
            return Response({
                'status': 'complete',
                'verification_result': verification_result,
                'compliance_report': compliance_report
            })
        else:
            return Response({
                'status': 'incomplete',
                'verification_result': verification_result,
                'message': 'Missing required documents for PSR license application'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def generate_regulatory_reports(self, request):
        """Generate regulatory reports for specified time period."""
        start_date = request.query_params.get(
            'start_date',
            (datetime.now() - timedelta(days=30)).isoformat()
        )
        end_date = request.query_params.get(
            'end_date',
            datetime.now().isoformat()
        )
        
        # Get all suspicious transactions in the period
        suspicious_transactions = Transaction.objects.filter(
            is_suspicious=True,
            timestamp__range=(start_date, end_date)
        )
        
        reports = []
        for transaction in suspicious_transactions:
            alerts = self.regulatory_reporting.evaluate_transaction(transaction)
            if alerts:
                reports.append({
                    'transaction_id': transaction.id,
                    'customer_id': transaction.customer.id,
                    'amount': str(transaction.amount),
                    'alerts': [vars(alert) for alert in alerts],
                    'timestamp': transaction.timestamp.isoformat()
                })
        
        return Response({
            'period': {
                'start_date': start_date,
                'end_date': end_date
            },
            'total_reports': len(reports),
            'reports': reports
        })
