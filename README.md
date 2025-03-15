# AML Service - Modern Anti-Money Laundering Platform

## Overview

AML Service is a comprehensive anti-money laundering compliance platform designed to help financial institutions meet FCA (Financial Conduct Authority) requirements. Built with modern technologies and best practices, this platform provides robust customer due diligence, transaction monitoring, and risk assessment capabilities.

## Features

### 1. Customer Due Diligence (CDD)
- Customer risk profiling
- Document verification workflow
- PEP (Politically Exposed Person) screening
- Business ownership structure analysis
- Automated risk scoring

### 2. Transaction Monitoring
- Real-time transaction screening
- Suspicious activity detection
- Cross-border transaction monitoring
- Risk-based transaction assessment
- Automated flagging system

### 3. Risk Assessment
- Comprehensive risk scoring framework
- Periodic review scheduling
- Enhanced due diligence triggers
- Risk factor analysis
- Compliance status tracking

### 4. Document Management
- Secure document storage
- Expiry tracking
- Verification workflow
- Multi-document support
- Automated notifications

## Technical Implementation

### Technology Stack
- Python 3.13
- Django 5.1.7
- Django REST Framework 3.15.2
- Bootstrap 5.3.0
- Font Awesome 6.0.0
- SQLite (Development)

### Machine Learning Components
- scikit-learn 1.6.1 for risk scoring
- pandas 2.2.3 for data analysis
- numpy 2.2.3 for numerical computations

### Data Privacy & Security
- python-dotenv 1.0.1 for secure configuration
- pydantic 2.6.1 for data validation
- Django's built-in security features

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd aml-service
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Apply database migrations:
```bash
python manage.py migrate
```

5. Create a superuser:
```bash
python manage.py createsuperuser
```

6. Run the development server:
```bash
python manage.py runserver
```

## Configuration

### Environment Variables
Create a `.env` file in the project root and configure the following variables:
```
DEBUG=True
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1
```

### Security Settings
For production deployment:
1. Set `DEBUG=False`
2. Configure proper `ALLOWED_HOSTS`
3. Use a production-grade database
4. Set up proper SSL/TLS certificates
5. Configure secure session handling

## Usage

### Admin Interface
Access the admin interface at `/admin` to:
- Manage customers and their risk profiles
- Review and process transactions
- Conduct risk assessments
- Verify documents
- Monitor compliance status

### Main Application
The main application provides:
- Dashboard with key metrics
- Customer management interface
- Transaction monitoring tools
- Document verification workflow
- Risk assessment framework

## Compliance

### FCA Requirements
This platform is designed to meet FCA requirements for:
- Customer Due Diligence (CDD)
- Enhanced Due Diligence (EDD)
- Transaction monitoring
- Risk assessment
- Record keeping
- Suspicious activity reporting

### Data Protection
- GDPR compliant data handling
- Secure data storage
- Audit trail maintenance
- Access control implementation

## Development

### Running Tests
```bash
python manage.py test
```

### Code Style
Follow PEP 8 guidelines for Python code. Use the included `.gitignore` for proper version control.

## Production Deployment

Before deploying to production, ensure:
1. Comprehensive security audit is performed
2. FCA compliance requirements are met
3. Data protection measures are properly implemented
4. Infrastructure is properly scaled for production load
5. All sensitive data is properly encrypted
6. Monitoring and alerting systems are in place

### Support
For issues, feature requests, or security concerns, please open an issue in the repository.
