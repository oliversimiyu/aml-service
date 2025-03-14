from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from core.models import Customer, Transaction, RiskAssessment, VerificationDocument
from core.ml_models import TransactionAnomalyDetector, RiskScorer
from core.validators import TransactionData, DocumentVerification, RiskAssessmentRules
from .serializers import (CustomerSerializer, TransactionSerializer,
                         RiskAssessmentSerializer, VerificationDocumentSerializer)
from django.shortcuts import get_object_or_404
from datetime import datetime, timedelta
import numpy as np
import pandas as pd

class CustomerViewSet(viewsets.ModelViewSet):
    """ViewSet for managing customer data and risk assessments.
    
    Provides endpoints for customer management, identity verification,
    and risk profiling as part of AML compliance.
    """
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated]
    risk_scorer = RiskScorer()
    
    @action(detail=True, methods=['post'])
    def verify_identity(self, request, pk=None):
        customer = self.get_object()
        doc_type = request.data.get('document_type')
        issue_date = request.data.get('issue_date')
        expiry_date = request.data.get('expiry_date')
        
        try:
            # Convert dates from string to datetime
            issue_date = datetime.strptime(issue_date, '%Y-%m-%d')
            expiry_date = datetime.strptime(expiry_date, '%Y-%m-%d') if expiry_date else None
            
            # Validate document
            validation_result = DocumentVerification.validate_document(
                doc_type, issue_date, expiry_date
            )
            
            if validation_result['valid']:
                customer.is_verified = True
                customer.last_verification_date = datetime.now()
                customer.save()
                
                # Create verification document record
                VerificationDocument.objects.create(
                    customer=customer,
                    document_type=doc_type,
                    verification_status='VERIFIED',
                    verification_notes=str(validation_result.get('warnings', []))
                )
            
            return Response({
                'status': 'verified' if validation_result['valid'] else 'failed',
                'warnings': validation_result.get('warnings', []),
                'errors': validation_result.get('errors', [])
            })
            
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def risk_profile(self, request, pk=None):
        customer = self.get_object()
        transactions = Transaction.objects.filter(customer=customer)
        
        # Convert transactions to format needed by risk assessment
        transaction_data = [
            {
                'amount': float(t.amount),
                'timestamp': t.timestamp,
                'is_suspicious': t.is_suspicious
            } for t in transactions
        ]
        
        # Get risk assessment
        risk_factors = RiskAssessmentRules.evaluate_transaction_patterns(transaction_data)
        
        # Update customer risk score
        customer.risk_score = risk_factors['overall_risk']
        customer.save()
        
        # Create risk assessment record
        RiskAssessment.objects.create(
            customer=customer,
            risk_factors=risk_factors,
            overall_score=risk_factors['overall_risk'],
            recommendations=self._generate_recommendations(risk_factors)
        )
        
        return Response(risk_factors)
    
    def _generate_recommendations(self, risk_factors):
        recommendations = []
        
        if risk_factors['velocity'] > 0.7:
            recommendations.append('High transaction velocity detected. Consider implementing cooling-off periods.')
        if risk_factors['amount_variance'] > 0.7:
            recommendations.append('Unusual transaction amount patterns detected. Review for potential structuring.')
        if risk_factors['frequency'] > 0.7:
            recommendations.append('High-frequency trading patterns detected. Enhanced due diligence recommended.')
            
        return '\n'.join(recommendations) if recommendations else 'No specific recommendations at this time.'

class TransactionViewSet(viewsets.ModelViewSet):
    """ViewSet for monitoring and analyzing financial transactions.
    
    Implements ML-based anomaly detection and risk scoring for
    transaction monitoring as required by AML regulations.
    """
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]
    anomaly_detector = TransactionAnomalyDetector()
    
    def perform_create(self, serializer):
        # Validate transaction data
        try:
            transaction_data = TransactionData(
                amount=serializer.validated_data['amount'],
                transaction_type=serializer.validated_data['transaction_type'],
                customer_id=serializer.validated_data['customer'].id,
                description=serializer.validated_data.get('description')
            )
        except ValueError as e:
            raise ValidationError(detail=str(e))
        
        # Save transaction
        transaction = serializer.save()
        
        # Analyze for suspicious activity
        self._analyze_transaction(transaction)
        
        # Update customer risk score
        customer = transaction.customer
        risk_scorer = RiskScorer()
        customer.risk_score = risk_scorer.calculate_risk_score(customer)
        customer.save()
    
    def _analyze_transaction(self, transaction):
        # Check for suspicious activity using ML model
        if self.anomaly_detector.is_suspicious(transaction):
            transaction.is_suspicious = True
            transaction.save()
            
            # Create risk assessment for suspicious transaction
            RiskAssessment.objects.create(
                customer=transaction.customer,
                risk_factors={'suspicious_transaction': True},
                overall_score=min(1.0, transaction.customer.risk_score + 0.2),
                recommendations='Suspicious transaction detected. Enhanced due diligence recommended.'
            )

class DocumentVerificationViewSet(viewsets.ModelViewSet):
    """ViewSet for handling document verification in KYC process.
    
    Manages the verification of identity documents and implements
    document validation rules as per AML guidelines.
    """
    queryset = VerificationDocument.objects.all()
    serializer_class = VerificationDocumentSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=True, methods=['post'])
    def verify(self, request, pk=None):
        document = self.get_object()
        
        try:
            # Validate document details
            validation_result = DocumentVerification.validate_document(
                document.document_type,
                document.upload_date,
                request.data.get('expiry_date')
            )
            
            if validation_result['valid']:
                document.verification_status = 'VERIFIED'
                document.verification_notes = str(validation_result.get('warnings', []))
                document.save()
                
                # Update customer verification status
                customer = document.customer
                customer.is_verified = True
                customer.last_verification_date = datetime.now()
                customer.save()
            
            return Response({
                'status': 'verified' if validation_result['valid'] else 'failed',
                'warnings': validation_result.get('warnings', []),
                'errors': validation_result.get('errors', [])
            })
            
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
