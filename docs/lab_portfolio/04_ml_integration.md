# Lab Portfolio - Machine Learning Integration

## Exercise 4: Implementing ML-Based Risk Assessment

This exercise demonstrates the integration of machine learning capabilities for risk assessment and anomaly detection in the AML service, focusing on FCA compliance requirements.

### 1. Feature Engineering

```python
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler

class FeatureEngineering:
    """
    Feature engineering for AML risk assessment.
    Extracts and processes features for ML models.
    """
    def __init__(self):
        self.scaler = StandardScaler()
        
    def extract_customer_features(self, customer):
        """Extract features from customer data."""
        # Get customer's transaction history
        transactions = Transaction.objects.filter(customer=customer)
        
        # Transaction patterns
        transaction_features = {
            'avg_transaction_amount': transactions.aggregate(
                Avg('amount')
            )['amount__avg'] or 0,
            'max_transaction_amount': transactions.aggregate(
                Max('amount')
            )['amount__max'] or 0,
            'transaction_frequency': transactions.count(),
            'high_risk_country_ratio': self._calculate_country_risk(transactions)
        }
        
        # Document verification features
        documents = VerificationDocument.objects.filter(customer=customer)
        document_features = {
            'verified_documents': documents.filter(
                status='verified'
            ).count(),
            'expired_documents': documents.filter(
                expiry_date__lt=timezone.now()
            ).count(),
            'document_completeness': self._calculate_doc_completeness(documents)
        }
        
        # Combine features
        features = {
            **transaction_features,
            **document_features,
            'customer_age_days': (timezone.now() - customer.created_at).days,
            'business_type_risk': self._get_business_risk(customer.business_type)
        }
        
        return features
        
    def _calculate_country_risk(self, transactions):
        """Calculate ratio of transactions with high-risk countries."""
        if not transactions:
            return 0.0
            
        high_risk_count = transactions.filter(
            Q(source_country__in=HIGH_RISK_COUNTRIES) |
            Q(destination_country__in=HIGH_RISK_COUNTRIES)
        ).count()
        
        return high_risk_count / transactions.count()
        
    def _calculate_doc_completeness(self, documents):
        """Calculate document verification completeness score."""
        required_docs = set(['id', 'address', 'business_registration'])
        verified_docs = set(
            documents.filter(status='verified').values_list(
                'document_type', flat=True
            )
        )
        return len(required_docs.intersection(verified_docs)) / len(required_docs)
        
    def _get_business_risk(self, business_type):
        """Get risk score for business type."""
        risk_mapping = {
            'gambling': 1.0,
            'cryptocurrency': 0.9,
            'money_services': 0.8,
            'real_estate': 0.6,
            'retail': 0.3,
            'technology': 0.2
        }
        return risk_mapping.get(business_type, 0.5)
```

### 2. ML Model Implementation

```python
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

class RiskAssessmentModel:
    """
    Machine learning model for risk assessment.
    Implements RandomForest classifier for risk prediction.
    """
    def __init__(self):
        self.feature_engineering = FeatureEngineering()
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            class_weight='balanced'
        )
        
    def prepare_training_data(self):
        """Prepare data for model training."""
        customers = Customer.objects.all()
        features = []
        labels = []
        
        for customer in customers:
            customer_features = self.feature_engineering.extract_customer_features(
                customer
            )
            features.append(customer_features)
            
            # Use historical risk assessments as labels
            risk_level = customer.riskassessment_set.latest(
                'assessment_date'
            ).risk_level
            labels.append(1 if risk_level == 'high' else 0)
            
        return pd.DataFrame(features), np.array(labels)
        
    def train(self):
        """Train the risk assessment model."""
        features, labels = self.prepare_training_data()
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            features, labels, test_size=0.2, random_state=42
        )
        
        # Scale features
        X_train_scaled = self.feature_engineering.scaler.fit_transform(X_train)
        X_test_scaled = self.feature_engineering.scaler.transform(X_test)
        
        # Train model
        self.model.fit(X_train_scaled, y_train)
        
        # Evaluate
        y_pred = self.model.predict(X_test_scaled)
        print(classification_report(y_test, y_pred))
        
    def predict_risk(self, customer):
        """Predict risk level for a customer."""
        features = self.feature_engineering.extract_customer_features(customer)
        features_df = pd.DataFrame([features])
        features_scaled = self.feature_engineering.scaler.transform(features_df)
        
        # Get probability of high risk
        risk_prob = self.model.predict_proba(features_scaled)[0][1]
        
        return {
            'risk_probability': risk_prob,
            'risk_level': 'high' if risk_prob > 0.7 else 'medium' if risk_prob > 0.4 else 'low',
            'feature_importance': self._get_feature_importance(features)
        }
        
    def _get_feature_importance(self, features):
        """Get feature importance for risk prediction."""
        importance = dict(zip(
            features.keys(),
            self.model.feature_importances_
        ))
        return dict(sorted(
            importance.items(),
            key=lambda x: x[1],
            reverse=True
        ))
```

### 3. Anomaly Detection

```python
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

class TransactionAnomalyDetector:
    """
    Anomaly detection for suspicious transactions.
    Implements Isolation Forest algorithm.
    """
    def __init__(self):
        self.model = IsolationForest(
            contamination=0.1,
            random_state=42
        )
        self.scaler = StandardScaler()
        
    def extract_transaction_features(self, transaction):
        """Extract features for anomaly detection."""
        customer = transaction.customer
        customer_avg = Transaction.objects.filter(
            customer=customer
        ).aggregate(Avg('amount'))['amount__avg'] or 0
        
        features = [
            float(transaction.amount),
            float(customer_avg),
            customer.risk_score,
            self._get_hour_of_day(transaction.timestamp),
            self._get_day_of_week(transaction.timestamp),
            self._calculate_velocity(customer)
        ]
        
        return np.array(features).reshape(1, -1)
        
    def _get_hour_of_day(self, timestamp):
        """Get hour of day as a cyclical feature."""
        hour = timestamp.hour
        return np.sin(2 * np.pi * hour / 24)
        
    def _get_day_of_week(self, timestamp):
        """Get day of week as a cyclical feature."""
        day = timestamp.weekday()
        return np.sin(2 * np.pi * day / 7)
        
    def _calculate_velocity(self, customer):
        """Calculate transaction velocity."""
        recent_transactions = Transaction.objects.filter(
            customer=customer,
            timestamp__gte=timezone.now() - timedelta(hours=24)
        )
        return recent_transactions.count()
        
    def detect_anomalies(self, transactions):
        """Detect anomalies in a batch of transactions."""
        if not transactions:
            return []
            
        features = np.vstack([
            self.extract_transaction_features(t) for t in transactions
        ])
        features_scaled = self.scaler.fit_transform(features)
        
        # -1 for anomalies, 1 for normal
        predictions = self.model.fit_predict(features_scaled)
        
        return [t for t, p in zip(transactions, predictions) if p == -1]
```

### 4. Model Deployment and Monitoring

```python
class ModelDeployment:
    """
    Model deployment and monitoring service.
    Handles model updates and performance monitoring.
    """
    def __init__(self):
        self.risk_model = RiskAssessmentModel()
        self.anomaly_detector = TransactionAnomalyDetector()
        self.metrics = ModelMetricsCollector()
        
    def update_models(self):
        """Periodic model update."""
        try:
            # Train risk assessment model
            self.risk_model.train()
            
            # Update metrics
            self.metrics.collect_model_metrics(self.risk_model)
            
            # Log update
            ModelUpdateLog.objects.create(
                model_type='risk_assessment',
                status='success',
                metrics=self.metrics.get_latest_metrics()
            )
            
        except Exception as e:
            ModelUpdateLog.objects.create(
                model_type='risk_assessment',
                status='failed',
                error_message=str(e)
            )
            raise
            
    def monitor_model_performance(self):
        """Monitor model performance metrics."""
        metrics = self.metrics.get_latest_metrics()
        
        # Check for performance degradation
        if metrics['accuracy'] < 0.8 or metrics['precision'] < 0.7:
            Alert.objects.create(
                alert_type='model_performance',
                severity='high',
                description='Model performance below threshold'
            )
            
        return metrics
```

### Learning Outcomes

1. **Machine Learning Integration**
   - Feature engineering for AML
   - Model training and evaluation
   - Anomaly detection implementation

2. **Risk Assessment**
   - ML-based risk scoring
   - Feature importance analysis
   - Model performance monitoring

3. **Production Deployment**
   - Model deployment workflow
   - Performance monitoring
   - Automated updates

### Next Steps

1. Implement additional ML models
2. Enhance feature engineering
3. Improve model monitoring
4. Develop automated retraining pipeline
