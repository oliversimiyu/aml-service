"""Validation utilities for AML service."""
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pydantic import BaseModel, Field, validator
import re

class TransactionData(BaseModel):
    amount: float
    transaction_type: str
    customer_id: int
    description: Optional[str] = None
    
    @validator('amount')
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError('Transaction amount must be positive')
        if v >= 1_000_000:
            raise ValueError('Transactions over 1M require enhanced due diligence')
        return v
    
    @validator('transaction_type')
    def validate_transaction_type(cls, v):
        valid_types = {'transfer', 'deposit', 'withdrawal', 'payment'}
        if v.lower() not in valid_types:
            raise ValueError(f'Transaction type must be one of: {valid_types}')
        return v.lower()

class DocumentVerification:
    """Document verification system for KYC/AML compliance."""
    
    VALID_DOC_TYPES = {
        'passport': {'expiry_required': True, 'min_age': 16},
        'driving_license': {'expiry_required': True, 'min_age': 17},
        'national_id': {'expiry_required': True, 'min_age': 16},
        'utility_bill': {'expiry_required': False, 'max_age_months': 3}
    }
    
    @classmethod
    def validate_document(cls, doc_type: str, issue_date: datetime,
                         expiry_date: Optional[datetime] = None) -> Dict[str, bool]:
        """
        Validate a document based on type-specific rules.
        Returns dict with validation results and any warnings/errors.
        """
        if doc_type not in cls.VALID_DOC_TYPES:
            raise ValueError(f'Invalid document type. Must be one of: {cls.VALID_DOC_TYPES.keys()}')
            
        rules = cls.VALID_DOC_TYPES[doc_type]
        results = {'valid': True, 'warnings': [], 'errors': []}
        
        # Check document age
        if 'max_age_months' in rules:
            doc_age = datetime.now() - issue_date
            if doc_age > timedelta(days=rules['max_age_months'] * 30):
                results['valid'] = False
                results['errors'].append(f'Document too old. Must be less than {rules["max_age_months"]} months')
        
        # Check expiry if required
        if rules['expiry_required'] and expiry_date:
            if expiry_date < datetime.now():
                results['valid'] = False
                results['errors'].append('Document has expired')
            elif expiry_date < datetime.now() + timedelta(days=90):
                results['warnings'].append('Document will expire soon')
                
        return results

class RiskAssessmentRules:
    """Rules engine for risk assessment."""
    
    @staticmethod
    def evaluate_transaction_patterns(transactions: List[Dict]) -> Dict[str, float]:
        """
        Evaluate transaction patterns for risk indicators.
        Returns dict of risk factors and their scores.
        """
        if not transactions:
            return {'overall_risk': 0.5}  # Default medium risk
            
        risk_factors = {
            'velocity': 0.0,  # Transaction velocity risk
            'amount_variance': 0.0,  # Unusual amount patterns
            'frequency': 0.0,  # High-frequency trading risk
            'overall_risk': 0.0
        }
        
        # Calculate transaction velocity
        timestamps = [t['timestamp'] for t in transactions]
        if len(timestamps) > 1:
            time_diffs = [(timestamps[i] - timestamps[i-1]).total_seconds() 
                         for i in range(1, len(timestamps))]
            avg_velocity = sum(time_diffs) / len(time_diffs)
            risk_factors['velocity'] = min(1.0, 3600 / max(avg_velocity, 1))
        
        # Calculate amount variance risk
        amounts = [t['amount'] for t in transactions]
        if len(amounts) > 1:
            mean_amount = sum(amounts) / len(amounts)
            variance = sum((x - mean_amount) ** 2 for x in amounts) / len(amounts)
            risk_factors['amount_variance'] = min(1.0, variance / (mean_amount ** 2))
        
        # Calculate frequency risk
        time_window = timedelta(days=7)
        recent_count = sum(1 for t in timestamps 
                         if datetime.now() - t <= time_window)
        risk_factors['frequency'] = min(1.0, recent_count / 50)  # Cap at 50 transactions/week
        
        # Calculate overall risk score
        risk_factors['overall_risk'] = (
            0.4 * risk_factors['velocity'] +
            0.3 * risk_factors['amount_variance'] +
            0.3 * risk_factors['frequency']
        )
        
        return risk_factors
