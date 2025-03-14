# Lab Portfolio - Getting Started Guide

## COMP1831 - Technologies for Anti-Money Laundering and Financial Crime

### Exercise 1: Setting Up the AML Service

This guide documents the initial setup and configuration of our Anti-Money Laundering (AML) service, demonstrating the implementation of key FCA compliance requirements.

#### 1. Environment Setup

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Apply database migrations
python manage.py migrate

# Create superuser for admin access
python manage.py createsuperuser
```

#### 2. Key Components Implemented

1. **Customer Due Diligence (CDD)**
   - Risk-based approach implementation
   - Customer categorization system
   - Automated risk scoring
   
   ![Customer Risk Dashboard](screenshots/customer_risk_dashboard.png)

2. **Document Verification System**
   - Multi-document support
   - Expiry tracking
   - Verification workflow
   
   ![Document Verification](screenshots/document_verification.png)

3. **Transaction Monitoring**
   - Real-time screening
   - Risk-based assessment
   - Suspicious activity detection
   
   ![Transaction Monitoring](screenshots/transaction_monitoring.png)

#### 3. FCA Compliance Features

1. **Risk Assessment Framework**
   ```python
   class RiskAssessment(models.Model):
       """Risk Assessment model for customer risk profiling.
       
       Implements comprehensive risk assessment framework including
       initial, periodic, and triggered reviews as required by FCA regulations.
       """
       customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
       assessment_date = models.DateTimeField(auto_now_add=True)
       risk_factors = models.JSONField()
       overall_score = models.FloatField()
       # ... other fields
   ```

2. **Document Verification**
   ```python
   class VerificationDocument(models.Model):
       """Document verification model for KYC process.
       
       Handles various types of identity and business documents
       required for customer verification as per FCA guidelines.
       """
       customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
       document_type = models.CharField(max_length=50, choices=DocumentType.choices)
       # ... other fields
   ```

#### 4. Machine Learning Integration

1. **Risk Scoring Algorithm**
   - Feature engineering for risk factors
   - Weighted scoring system
   - Continuous learning capabilities

2. **Transaction Analysis**
   - Pattern recognition
   - Anomaly detection
   - Behavioral analysis

#### 5. Data Privacy Implementation

1. **Secure Data Handling**
   - Encryption at rest
   - Secure transmission
   - Access control

2. **GDPR Compliance**
   - Data minimization
   - Purpose limitation
   - Storage constraints

#### 6. Testing and Validation

```bash
# Run test suite
python manage.py test

# Coverage report
coverage run manage.py test
coverage report
```

### Next Steps

1. Review the [Risk Assessment Implementation](02_risk_assessment.md)
2. Explore the [Transaction Monitoring System](03_transaction_monitoring.md)
3. Study the [Machine Learning Integration](04_ml_integration.md)

### Learning Outcomes

- Understanding of FCA compliance requirements
- Implementation of secure FinTech solutions
- Application of machine learning in financial crime detection
- Development of scalable financial service architectures

### Notes

This implementation demonstrates:
- Modern Django practices
- FCA compliance integration
- Machine learning application
- Security best practices

For the full implementation details, refer to the source code in the respective modules.
