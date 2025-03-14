# Lab Portfolio - Transaction Monitoring System

## Exercise 3: Implementing Transaction Monitoring

This exercise demonstrates the implementation of a real-time transaction monitoring system that combines rule-based and machine learning approaches for detecting suspicious activities.

### 1. Transaction Model

```python
from django.db import models
from django.utils import timezone

class Transaction(models.Model):
    """
    Transaction model for monitoring financial activities.
    Implements FCA requirements for transaction monitoring.
    """
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(default=timezone.now)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    
    class TransactionType(models.TextChoices):
        DEPOSIT = 'deposit', 'Deposit'
        WITHDRAWAL = 'withdrawal', 'Withdrawal'
        TRANSFER = 'transfer', 'Transfer'
        
    transaction_type = models.CharField(
        max_length=20,
        choices=TransactionType.choices
    )
    
    source_country = models.CharField(max_length=2)
    destination_country = models.CharField(max_length=2)
    
    class ScreeningStatus(models.TextChoices):
        PENDING = 'pending', 'Pending'
        CLEARED = 'cleared', 'Cleared'
        FLAGGED = 'flagged', 'Flagged'
        BLOCKED = 'blocked', 'Blocked'
        
    screening_status = models.CharField(
        max_length=20,
        choices=ScreeningStatus.choices,
        default=ScreeningStatus.PENDING
    )
    
    risk_score = models.FloatField(default=0.0)
    is_suspicious = models.BooleanField(default=False)
```

### 2. Transaction Monitoring Implementation

```python
from sklearn.ensemble import IsolationForest
import numpy as np

class TransactionMonitor:
    """
    Real-time transaction monitoring system implementing FCA guidelines.
    """
    def __init__(self):
        self.rules_engine = ComplianceRulesEngine()
        self.ml_model = self.initialize_ml_model()
        
    def initialize_ml_model(self):
        """Initialize the anomaly detection model."""
        return IsolationForest(
            contamination=0.1,
            random_state=42
        )
        
    def monitor_transaction(self, transaction):
        """
        Monitor a transaction for suspicious activity.
        Returns a tuple of (risk_score, is_suspicious, screening_status)
        """
        # Rule-based screening
        rules_score = self.rules_engine.evaluate_transaction(transaction)
        
        # ML-based anomaly detection
        ml_score = self.detect_anomalies(transaction)
        
        # Combine scores
        risk_score = self.calculate_combined_score(rules_score, ml_score)
        
        # Determine status
        is_suspicious = risk_score > 0.7
        screening_status = self.determine_screening_status(risk_score)
        
        return risk_score, is_suspicious, screening_status
        
    def evaluate_transaction(self, transaction):
        """Evaluate transaction against compliance rules."""
        rules_violations = []
        
        # Check transaction amount
        if transaction.amount > 10000:
            rules_violations.append('large_transaction')
            
        # Check high-risk countries
        if transaction.source_country in HIGH_RISK_COUNTRIES or \
           transaction.destination_country in HIGH_RISK_COUNTRIES:
            rules_violations.append('high_risk_country')
            
        # Check transaction frequency
        recent_transactions = Transaction.objects.filter(
            customer=transaction.customer,
            timestamp__gte=timezone.now() - timedelta(hours=24)
        )
        if recent_transactions.count() > 10:
            rules_violations.append('high_frequency')
            
        return len(rules_violations) / 3  # Normalize score
        
    def detect_anomalies(self, transaction):
        """Detect anomalies using machine learning."""
        # Extract features
        features = self.extract_features(transaction)
        
        # Predict anomaly score
        score = self.ml_model.predict([features])[0]
        
        # Convert to probability-like score
        return (1 - score) / 2  # Convert to [0,1] range
        
    def extract_features(self, transaction):
        """Extract features for ML model."""
        customer = transaction.customer
        
        # Get customer's transaction history
        history = Transaction.objects.filter(
            customer=customer,
            timestamp__gte=timezone.now() - timedelta(days=30)
        )
        
        # Calculate features
        avg_amount = history.aggregate(Avg('amount'))['amount__avg'] or 0
        max_amount = history.aggregate(Max('amount'))['amount__max'] or 0
        transaction_count = history.count()
        
        return [
            float(transaction.amount),
            float(avg_amount),
            float(max_amount),
            transaction_count,
            customer.risk_score
        ]
        
    def calculate_combined_score(self, rules_score, ml_score):
        """Combine rule-based and ML scores."""
        # Weight ML score higher for more established customers
        return 0.4 * rules_score + 0.6 * ml_score
        
    def determine_screening_status(self, risk_score):
        """Determine screening status based on risk score."""
        if risk_score > 0.8:
            return Transaction.ScreeningStatus.BLOCKED
        elif risk_score > 0.7:
            return Transaction.ScreeningStatus.FLAGGED
        elif risk_score > 0.3:
            return Transaction.ScreeningStatus.PENDING
        return Transaction.ScreeningStatus.CLEARED
```

### 3. Transaction Monitoring Service

```python
from django.core.exceptions import ValidationError
from django.db import transaction

class TransactionMonitoringService:
    """
    Service class for handling transaction monitoring workflow.
    """
    def __init__(self):
        self.monitor = TransactionMonitor()
        
    @transaction.atomic
    def process_transaction(self, transaction_data):
        """
        Process and monitor a new transaction.
        Implements the full transaction monitoring workflow.
        """
        try:
            # Create transaction
            transaction = Transaction.objects.create(**transaction_data)
            
            # Monitor transaction
            risk_score, is_suspicious, status = self.monitor.monitor_transaction(
                transaction
            )
            
            # Update transaction
            transaction.risk_score = risk_score
            transaction.is_suspicious = is_suspicious
            transaction.screening_status = status
            transaction.save()
            
            # Create alerts if necessary
            if is_suspicious:
                self.create_alert(transaction)
                
            # Update customer risk score
            self.update_customer_risk(transaction.customer)
            
            return transaction
            
        except ValidationError as e:
            raise ValidationError(f"Invalid transaction data: {str(e)}")
            
    def create_alert(self, transaction):
        """Create an alert for suspicious transaction."""
        Alert.objects.create(
            transaction=transaction,
            alert_type='suspicious_transaction',
            severity='high' if transaction.risk_score > 0.8 else 'medium',
            description=f"Suspicious transaction detected: {transaction.id}"
        )
        
    def update_customer_risk(self, customer):
        """Update customer risk score based on transaction history."""
        recent_transactions = Transaction.objects.filter(
            customer=customer,
            timestamp__gte=timezone.now() - timedelta(days=30)
        )
        
        avg_risk = recent_transactions.aggregate(
            Avg('risk_score')
        )['risk_score__avg'] or 0.0
        
        customer.risk_score = avg_risk
        customer.save()
```

### 4. Transaction Monitoring API

```python
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

class TransactionViewSet(viewsets.ModelViewSet):
    """
    API viewset for transaction monitoring.
    """
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    
    def perform_create(self, serializer):
        """Process transaction on creation."""
        service = TransactionMonitoringService()
        transaction_data = serializer.validated_data
        transaction = service.process_transaction(transaction_data)
        serializer.instance = transaction
        
    @action(detail=True, methods=['post'])
    def review(self, request, pk=None):
        """Manual review of flagged transaction."""
        transaction = self.get_object()
        
        if transaction.screening_status != Transaction.ScreeningStatus.FLAGGED:
            return Response(
                {'error': 'Only flagged transactions can be reviewed'},
                status=400
            )
            
        action = request.data.get('action')
        if action not in ['approve', 'reject']:
            return Response(
                {'error': 'Invalid action. Use "approve" or "reject"'},
                status=400
            )
            
        if action == 'approve':
            transaction.screening_status = Transaction.ScreeningStatus.CLEARED
        else:
            transaction.screening_status = Transaction.ScreeningStatus.BLOCKED
            
        transaction.save()
        return Response({'status': 'success'})
```

### Learning Outcomes

1. **Real-time Monitoring**
   - Implementation of FCA-compliant transaction monitoring
   - Integration of rule-based and ML approaches
   - Real-time risk scoring

2. **Machine Learning Integration**
   - Anomaly detection implementation
   - Feature engineering
   - Model integration

3. **Service Architecture**
   - Transaction processing workflow
   - Alert generation
   - Risk score updates

### Next Steps

1. Review the [Machine Learning Integration](04_ml_integration.md)
2. Implement additional monitoring rules
3. Enhance the anomaly detection model
