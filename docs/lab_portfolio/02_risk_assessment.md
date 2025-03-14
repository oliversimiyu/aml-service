# Lab Portfolio - Risk Assessment Implementation

## Exercise 2: Implementing Risk-Based Approach

This exercise demonstrates the implementation of a risk-based approach to AML compliance, focusing on customer risk assessment and transaction monitoring.

### 1. Risk Assessment Model

```python
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class RiskAssessment(models.Model):
    """
    Risk Assessment model implementing FCA's risk-based approach.
    """
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE)
    assessment_date = models.DateTimeField(auto_now_add=True)
    
    # Risk Factors
    geographic_risk = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)]
    )
    business_type_risk = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)]
    )
    transaction_risk = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)]
    )
    document_risk = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)]
    )
    
    # Overall Risk Score
    overall_risk_score = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)]
    )
    
    class RiskLevel(models.TextChoices):
        LOW = 'low', 'Low Risk'
        MEDIUM = 'medium', 'Medium Risk'
        HIGH = 'high', 'High Risk'
    
    risk_level = models.CharField(
        max_length=10,
        choices=RiskLevel.choices,
        default=RiskLevel.LOW
    )
```

### 2. Risk Scoring Implementation

```python
class RiskScorer:
    def __init__(self, customer):
        self.customer = customer
        self.weights = {
            'geographic_risk': 0.3,
            'business_type_risk': 0.2,
            'transaction_risk': 0.3,
            'document_risk': 0.2
        }
    
    def calculate_geographic_risk(self):
        """Calculate risk based on customer's geographic location."""
        high_risk_countries = ['XX', 'YY', 'ZZ']  # Example country codes
        medium_risk_countries = ['AA', 'BB', 'CC']
        
        if self.customer.country_code in high_risk_countries:
            return 1.0
        elif self.customer.country_code in medium_risk_countries:
            return 0.5
        return 0.1
    
    def calculate_business_risk(self):
        """Calculate risk based on business type."""
        high_risk_businesses = ['gambling', 'cryptocurrency', 'precious_metals']
        medium_risk_businesses = ['money_services', 'real_estate']
        
        if self.customer.business_type in high_risk_businesses:
            return 1.0
        elif self.customer.business_type in medium_risk_businesses:
            return 0.5
        return 0.1
    
    def calculate_transaction_risk(self):
        """Calculate risk based on transaction patterns."""
        recent_transactions = Transaction.objects.filter(
            customer=self.customer,
            timestamp__gte=timezone.now() - timedelta(days=30)
        )
        
        total_amount = sum(t.amount for t in recent_transactions)
        high_value_count = sum(1 for t in recent_transactions if t.amount > 10000)
        
        if high_value_count > 5 or total_amount > 50000:
            return 1.0
        elif high_value_count > 2 or total_amount > 20000:
            return 0.5
        return 0.1
    
    def calculate_document_risk(self):
        """Calculate risk based on document verification status."""
        documents = VerificationDocument.objects.filter(customer=self.customer)
        
        if not documents.exists():
            return 1.0
        
        expired_docs = documents.filter(expiry_date__lt=timezone.now())
        if expired_docs.exists():
            return 0.8
        
        pending_docs = documents.filter(status='pending')
        if pending_docs.exists():
            return 0.5
            
        return 0.1
    
    def calculate_overall_risk(self):
        """Calculate overall risk score."""
        risk_scores = {
            'geographic_risk': self.calculate_geographic_risk(),
            'business_type_risk': self.calculate_business_risk(),
            'transaction_risk': self.calculate_transaction_risk(),
            'document_risk': self.calculate_document_risk()
        }
        
        overall_score = sum(
            score * self.weights[factor] 
            for factor, score in risk_scores.items()
        )
        
        return overall_score, self.determine_risk_level(overall_score)
    
    def determine_risk_level(self, score):
        """Determine risk level based on score."""
        if score >= 0.7:
            return RiskAssessment.RiskLevel.HIGH
        elif score >= 0.4:
            return RiskAssessment.RiskLevel.MEDIUM
        return RiskAssessment.RiskLevel.LOW
```

### 3. Risk Assessment Views

```python
from django.views.generic import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin

class RiskAssessmentView(LoginRequiredMixin, DetailView):
    model = RiskAssessment
    template_name = 'risk_assessments.html'
    context_object_name = 'assessment'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['risk_factors'] = {
            'Geographic Risk': self.object.geographic_risk,
            'Business Type Risk': self.object.business_type_risk,
            'Transaction Risk': self.object.transaction_risk,
            'Document Risk': self.object.document_risk
        }
        return context
```

### 4. Risk Assessment Template

```html
{% extends 'base.html' %}

{% block content %}
<div class="container mt-4">
    <h2>Risk Assessment Details</h2>
    
    <div class="card">
        <div class="card-header">
            <h3>Overall Risk Level: 
                <span class="badge {% if assessment.risk_level == 'high' %}bg-danger
                    {% elif assessment.risk_level == 'medium' %}bg-warning
                    {% else %}bg-success{% endif %}">
                    {{ assessment.get_risk_level_display }}
                </span>
            </h3>
        </div>
        
        <div class="card-body">
            <h4>Risk Factors</h4>
            <div class="row">
                {% for factor, score in risk_factors.items %}
                <div class="col-md-6 mb-3">
                    <div class="card">
                        <div class="card-body">
                            <h5 class="card-title">{{ factor }}</h5>
                            <div class="progress">
                                <div class="progress-bar {% if score >= 0.7 %}bg-danger
                                    {% elif score >= 0.4 %}bg-warning
                                    {% else %}bg-success{% endif %}"
                                    role="progressbar"
                                    style="width: {{ score|multiply:100 }}%"
                                    aria-valuenow="{{ score|multiply:100 }}"
                                    aria-valuemin="0"
                                    aria-valuemax="100">
                                    {{ score|multiply:100 }}%
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

### Learning Outcomes

1. **Risk-Based Approach**
   - Implementation of FCA's risk-based approach to AML compliance
   - Dynamic risk scoring system
   - Multi-factor risk assessment

2. **Data Modeling**
   - Django models for risk assessment
   - Validation constraints
   - Relationship management

3. **User Interface**
   - Risk visualization
   - Interactive risk assessment display
   - Responsive design

### Next Steps

1. Review the [Transaction Monitoring Implementation](03_transaction_monitoring.md)
2. Implement additional risk factors
3. Enhance the risk scoring algorithm
