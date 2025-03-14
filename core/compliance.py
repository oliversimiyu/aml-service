"""Regulatory compliance and reporting functionality for AML service."""
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json
from dataclasses import dataclass
from enum import Enum

class ReportType(Enum):
    """Types of regulatory reports."""
    SAR = "Suspicious Activity Report"
    CTR = "Currency Transaction Report"
    STR = "Suspicious Transaction Report"

@dataclass
class ComplianceAlert:
    """Structure for compliance alerts."""
    alert_type: str
    severity: str
    description: str
    timestamp: datetime
    related_entities: List[str]
    action_required: bool

class RegulatoryReporting:
    """Handles generation and management of regulatory reports."""
    
    def __init__(self):
        self.threshold_ctr = 10000  # Currency Transaction Report threshold
        self.threshold_sar = 5000   # Suspicious Activity Report threshold
    
    def evaluate_transaction(self, transaction) -> List[ComplianceAlert]:
        """Evaluate a transaction for regulatory reporting requirements."""
        alerts = []
        
        # Check for CTR requirement
        if float(transaction.amount) > self.threshold_ctr:
            alerts.append(ComplianceAlert(
                alert_type=ReportType.CTR.value,
                severity="HIGH",
                description=f"Transaction amount (£{transaction.amount}) exceeds CTR threshold",
                timestamp=datetime.now(),
                related_entities=[str(transaction.customer.id)],
                action_required=True
            ))
        
        # Check for structured transactions
        recent_transactions = transaction.customer.transaction_set.filter(
            timestamp__gte=datetime.now() - timedelta(days=7)
        )
        total_amount = sum(float(t.amount) for t in recent_transactions)
        
        if total_amount > self.threshold_sar:
            alerts.append(ComplianceAlert(
                alert_type=ReportType.SAR.value,
                severity="MEDIUM",
                description="Multiple transactions potentially indicating structuring",
                timestamp=datetime.now(),
                related_entities=[str(transaction.customer.id)],
                action_required=True
            ))
        
        return alerts

class ComplianceRules:
    """Rules engine for regulatory compliance."""
    
    @staticmethod
    def check_high_risk_countries(customer_data: Dict) -> List[str]:
        """Check for transactions involving high-risk countries."""
        high_risk_countries = {
            'XX': 'High-risk jurisdiction',
            'YY': 'Sanctioned country',
            'ZZ': 'Non-cooperative jurisdiction'
        }
        
        warnings = []
        country_code = customer_data.get('country_code')
        if country_code in high_risk_countries:
            warnings.append(f"Customer associated with {high_risk_countries[country_code]}")
        return warnings
    
    @staticmethod
    def evaluate_customer_risk(customer) -> Dict:
        """Evaluate customer risk factors for regulatory compliance."""
        risk_factors = {
            'identity_verification': 0.0,
            'transaction_pattern': 0.0,
            'geographic_risk': 0.0,
            'business_type_risk': 0.0
        }
        
        # Identity verification risk
        if not customer.is_verified:
            risk_factors['identity_verification'] = 1.0
        elif (datetime.now() - customer.last_verification_date).days > 365:
            risk_factors['identity_verification'] = 0.5
            
        # Transaction pattern risk
        suspicious_transactions = customer.transaction_set.filter(is_suspicious=True)
        total_transactions = customer.transaction_set.count()
        if total_transactions > 0:
            risk_factors['transaction_pattern'] = len(suspicious_transactions) / total_transactions
            
        return risk_factors

class PSRCompliance:
    """Payment Systems Regulator (PSR) compliance checks."""
    
    def __init__(self):
        self.required_documents = {
            'business': [
                'certificate_of_incorporation',
                'business_plan',
                'financial_projections',
                'aml_policy'
            ],
            'personal': [
                'proof_of_identity',
                'proof_of_address',
                'source_of_funds'
            ]
        }
    
    def verify_license_requirements(self, customer_type: str, documents: List[str]) -> Dict:
        """Verify if all required documents for PSR license are provided."""
        required = set(self.required_documents[customer_type])
        provided = set(documents)
        
        return {
            'complete': required.issubset(provided),
            'missing_documents': list(required - provided),
            'additional_documents': list(provided - required)
        }
    
    def generate_compliance_report(self, customer) -> Dict:
        """Generate a compliance report for PSR license application."""
        return {
            'customer_id': customer.id,
            'verification_status': customer.is_verified,
            'risk_assessment': ComplianceRules.evaluate_customer_risk(customer),
            'transaction_monitoring': {
                'suspicious_transactions': customer.transaction_set.filter(
                    is_suspicious=True).count(),
                'total_transactions': customer.transaction_set.count(),
                'average_transaction_amount': customer.transaction_set.aggregate(
                    avg_amount=models.Avg('amount'))['avg_amount']
            },
            'compliance_status': 'compliant' if customer.is_verified else 'non_compliant',
            'timestamp': datetime.now().isoformat()
        }
