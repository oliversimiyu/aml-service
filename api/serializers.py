"""Serializers for the AML service API."""
from rest_framework import serializers
from core.models import Customer, Transaction, RiskAssessment, VerificationDocument
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email')

class CustomerSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Customer
        fields = ('id', 'user', 'risk_score', 'last_verification_date', 'is_verified')
        read_only_fields = ('risk_score', 'last_verification_date', 'is_verified')

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ('id', 'customer', 'amount', 'timestamp', 'transaction_type',
                 'risk_score', 'is_suspicious')
        read_only_fields = ('risk_score', 'is_suspicious')

class RiskAssessmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = RiskAssessment
        fields = ('id', 'customer', 'assessment_date', 'risk_factors',
                 'overall_score', 'recommendations')
        read_only_fields = ('assessment_date', 'risk_factors', 'overall_score',
                          'recommendations')

class VerificationDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = VerificationDocument
        fields = ('id', 'customer', 'document_type', 'upload_date',
                 'verification_status', 'verification_notes')
        read_only_fields = ('upload_date', 'verification_status',
                          'verification_notes')
