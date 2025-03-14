# Lab Portfolio - Data Privacy and Security

## Exercise 5: Implementing FCA-Compliant Data Privacy

This exercise demonstrates the implementation of data privacy and security measures required for FCA compliance and GDPR requirements in the AML service.

### 1. Data Encryption Service

```python
from cryptography.fernet import Fernet
from django.conf import settings
import base64
from django.core.exceptions import ValidationError

class EncryptionService:
    """
    Encryption service for sensitive data.
    Implements FCA-compliant encryption standards.
    """
    def __init__(self):
        self.key = self._load_encryption_key()
        self.cipher_suite = Fernet(self.key)
        
    def _load_encryption_key(self):
        """Load encryption key from secure environment."""
        try:
            key = settings.ENCRYPTION_KEY
            if not key:
                raise ValueError("Encryption key not found")
            return base64.urlsafe_b64encode(key.encode())
        except Exception as e:
            raise ValidationError(f"Encryption key error: {str(e)}")
            
    def encrypt_sensitive_data(self, data):
        """Encrypt sensitive customer data."""
        try:
            if not data:
                return None
            return self.cipher_suite.encrypt(
                json.dumps(data).encode()
            ).decode()
        except Exception as e:
            raise ValidationError(f"Encryption error: {str(e)}")
            
    def decrypt_sensitive_data(self, encrypted_data):
        """Decrypt sensitive customer data."""
        try:
            if not encrypted_data:
                return None
            decrypted = self.cipher_suite.decrypt(
                encrypted_data.encode()
            )
            return json.loads(decrypted.decode())
        except Exception as e:
            raise ValidationError(f"Decryption error: {str(e)}")
```

### 2. Data Privacy Model

```python
from django.db import models
from django.core.validators import RegexValidator

class PrivacySettings(models.Model):
    """
    Privacy settings and consent management.
    Implements GDPR requirements for data handling.
    """
    customer = models.OneToOneField(
        'Customer',
        on_delete=models.CASCADE,
        related_name='privacy_settings'
    )
    
    # Data retention preferences
    data_retention_period = models.IntegerField(
        default=365,  # days
        help_text="Period to retain customer data in days"
    )
    
    # Marketing preferences
    marketing_consent = models.BooleanField(default=False)
    last_consent_update = models.DateTimeField(auto_now=True)
    
    # Data sharing preferences
    data_sharing_consent = models.BooleanField(default=False)
    third_party_sharing = models.BooleanField(default=False)
    
    # Communication preferences
    class CommunicationChannel(models.TextChoices):
        EMAIL = 'email', 'Email'
        SMS = 'sms', 'SMS'
        PHONE = 'phone', 'Phone'
        NONE = 'none', 'No Communication'
        
    preferred_communication = models.CharField(
        max_length=10,
        choices=CommunicationChannel.choices,
        default=CommunicationChannel.EMAIL
    )
    
    # Data access log
    last_access = models.DateTimeField(null=True, blank=True)
    access_count = models.IntegerField(default=0)
    
    class Meta:
        verbose_name_plural = "Privacy Settings"
        
    def __str__(self):
        return f"Privacy Settings for {self.customer}"
        
    def update_access_log(self):
        """Update data access log."""
        self.last_access = timezone.now()
        self.access_count += 1
        self.save()
```

### 3. Data Access Control

```python
from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import PermissionDenied

class DataAccessControl:
    """
    Implementation of FCA-compliant data access controls.
    """
    def __init__(self, user):
        self.user = user
        self.permissions = self._load_user_permissions()
        
    def _load_user_permissions(self):
        """Load user permissions and roles."""
        return {
            'can_view_sensitive_data': self.user.has_perm('view_sensitive_data'),
            'can_modify_data': self.user.has_perm('modify_customer_data'),
            'is_compliance_officer': self.user.groups.filter(
                name='Compliance_Officers'
            ).exists(),
            'is_data_processor': self.user.groups.filter(
                name='Data_Processors'
            ).exists()
        }
        
    def can_access_customer_data(self, customer):
        """Check if user can access customer data."""
        if not self.permissions['can_view_sensitive_data']:
            return False
            
        # Check for specific access restrictions
        if customer.high_risk and not self.permissions['is_compliance_officer']:
            return False
            
        return True
        
    def can_modify_customer_data(self, customer):
        """Check if user can modify customer data."""
        if not self.permissions['can_modify_data']:
            return False
            
        # Additional checks for high-risk customers
        if customer.high_risk and not self.permissions['is_compliance_officer']:
            return False
            
        return True
        
    def log_access_attempt(self, customer, action_type):
        """Log data access attempts."""
        DataAccessLog.objects.create(
            user=self.user,
            customer=customer,
            action_type=action_type,
            timestamp=timezone.now(),
            was_successful=self.can_access_customer_data(customer)
        )
```

### 4. Data Retention Service

```python
class DataRetentionService:
    """
    Service for managing data retention policies.
    Implements FCA and GDPR requirements for data retention.
    """
    def __init__(self):
        self.retention_periods = {
            'customer_data': 365 * 5,  # 5 years
            'transaction_data': 365 * 7,  # 7 years
            'verification_documents': 365 * 10,  # 10 years
            'audit_logs': 365 * 3  # 3 years
        }
        
    def cleanup_expired_data(self):
        """Clean up expired data according to retention policy."""
        now = timezone.now()
        
        # Clean up customer data
        self._cleanup_customers(now)
        
        # Clean up transactions
        self._cleanup_transactions(now)
        
        # Clean up documents
        self._cleanup_documents(now)
        
        # Clean up audit logs
        self._cleanup_audit_logs(now)
        
    def _cleanup_customers(self, now):
        """Clean up expired customer data."""
        expiry_date = now - timedelta(
            days=self.retention_periods['customer_data']
        )
        
        expired_customers = Customer.objects.filter(
            last_activity__lt=expiry_date,
            status='inactive'
        )
        
        for customer in expired_customers:
            # Archive customer data
            self._archive_customer_data(customer)
            # Delete personal information
            customer.anonymize()
            
    def _cleanup_transactions(self, now):
        """Clean up expired transaction data."""
        expiry_date = now - timedelta(
            days=self.retention_periods['transaction_data']
        )
        
        Transaction.objects.filter(
            timestamp__lt=expiry_date
        ).update(
            amount=0,
            description='Redacted',
            is_redacted=True
        )
        
    def _archive_customer_data(self, customer):
        """Archive customer data before deletion."""
        archive_data = {
            'customer_id': customer.id,
            'risk_assessments': list(
                customer.riskassessment_set.values()
            ),
            'archive_date': timezone.now().isoformat()
        }
        
        ArchivedCustomerData.objects.create(
            customer_id=customer.id,
            archived_data=archive_data,
            retention_period=self.retention_periods['customer_data']
        )
```

### 5. Audit Logging

```python
class AuditLogger:
    """
    Comprehensive audit logging system.
    Implements FCA requirements for activity tracking.
    """
    def __init__(self):
        self.log_types = {
            'data_access': self._log_data_access,
            'data_modification': self._log_data_modification,
            'authentication': self._log_authentication,
            'authorization': self._log_authorization
        }
        
    def log_activity(self, log_type, **kwargs):
        """Log an activity."""
        if log_type not in self.log_types:
            raise ValueError(f"Invalid log type: {log_type}")
            
        log_func = self.log_types[log_type]
        return log_func(**kwargs)
        
    def _log_data_access(self, user, resource, action):
        """Log data access activity."""
        return AuditLog.objects.create(
            user=user,
            resource_type=resource.__class__.__name__,
            resource_id=resource.id,
            action=action,
            timestamp=timezone.now(),
            ip_address=get_client_ip(),
            user_agent=get_user_agent()
        )
        
    def _log_data_modification(self, user, resource, changes):
        """Log data modification activity."""
        return AuditLog.objects.create(
            user=user,
            resource_type=resource.__class__.__name__,
            resource_id=resource.id,
            action='modify',
            changes=json.dumps(changes),
            timestamp=timezone.now()
        )
        
    def _log_authentication(self, user, success, failure_reason=None):
        """Log authentication attempts."""
        return AuthenticationLog.objects.create(
            user=user,
            success=success,
            failure_reason=failure_reason,
            timestamp=timezone.now(),
            ip_address=get_client_ip()
        )
```

### Learning Outcomes

1. **Data Privacy Implementation**
   - FCA-compliant data handling
   - GDPR requirements implementation
   - Secure data encryption

2. **Access Control**
   - Role-based access control
   - Permission management
   - Activity logging

3. **Data Retention**
   - Retention policy implementation
   - Data cleanup procedures
   - Archiving mechanisms

### Next Steps

1. Implement additional security measures
2. Enhance audit logging
3. Add data anonymization features
4. Develop privacy compliance reports
