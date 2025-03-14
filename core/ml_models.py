"""Machine learning models for AML detection and risk scoring."""
import numpy as np
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import pandas as pd

class TransactionAnomalyDetector:
    def __init__(self):
        self.isolation_forest = IsolationForest(contamination=0.1, random_state=42)
        self.scaler = StandardScaler()
        
    def extract_features(self, transaction):
        """Extract relevant features for anomaly detection."""
        features = [
            float(transaction.amount),
            transaction.customer.risk_score,
            len(transaction.customer.transaction_set.all())  # Transaction history length
        ]
        return np.array(features).reshape(1, -1)
    
    def is_suspicious(self, transaction):
        """Determine if a transaction is suspicious using isolation forest."""
        features = self.extract_features(transaction)
        features_scaled = self.scaler.fit_transform(features)
        prediction = self.isolation_forest.fit_predict(features_scaled)
        return prediction[0] == -1

class RiskScorer:
    def __init__(self):
        self.rf_classifier = RandomForestClassifier(n_estimators=100, random_state=42)
        
    def calculate_risk_score(self, customer):
        """Calculate customer risk score based on various factors."""
        # Get customer's transaction history
        transactions = customer.transaction_set.all()
        
        if not transactions:
            return 0.5  # Default medium risk for new customers
        
        # Calculate risk factors
        avg_transaction = np.mean([float(t.amount) for t in transactions])
        transaction_frequency = len(transactions) / max(1, (pd.Timestamp.now() - 
            pd.Timestamp(transactions.latest().timestamp)).days)
        suspicious_ratio = len([t for t in transactions if t.is_suspicious]) / len(transactions)
        
        # Combine risk factors
        risk_score = (0.3 * suspicious_ratio + 
                     0.3 * min(1.0, transaction_frequency / 10) +
                     0.4 * min(1.0, avg_transaction / 10000))
        
        return risk_score
