// AML Service Dashboard JavaScript

// Risk Score Animation
function animateRiskScores() {
    const riskElements = document.querySelectorAll('.risk-score');
    riskElements.forEach(element => {
        const score = parseFloat(element.dataset.score);
        element.style.width = '0%';
        
        // Animate the score fill
        setTimeout(() => {
            element.style.transition = 'width 1s ease-in-out';
            element.style.width = `${score * 100}%`;
        }, 200);
        
        // Update the risk class
        if (score >= 0.7) {
            element.classList.add('risk-score-high');
        } else if (score >= 0.3) {
            element.classList.add('risk-score-medium');
        } else {
            element.classList.add('risk-score-low');
        }
    });
}

// Transaction Volume Chart Updates
function updateTransactionChart(chartId, newData) {
    const chart = Chart.getChart(chartId);
    if (chart) {
        chart.data.datasets[0].data = newData;
        chart.update();
    }
}

// Risk Distribution Updates
function updateRiskDistribution(chartId, distribution) {
    const chart = Chart.getChart(chartId);
    if (chart) {
        chart.data.datasets[0].data = [
            distribution.low,
            distribution.medium,
            distribution.high
        ];
        chart.update();
    }
}

// Activity Feed Updates
function addActivityItem(activity) {
    const activityList = document.querySelector('.activity-list');
    if (!activityList) return;

    const item = document.createElement('div');
    item.className = `activity-item ${activity.type.toLowerCase()}`;
    
    const timestamp = new Date(activity.timestamp).toLocaleString();
    
    item.innerHTML = `
        <div class="activity-time">${timestamp}</div>
        <div class="activity-content">
            <strong>${activity.type}</strong>
            <p>${activity.details}</p>
        </div>
        <div class="activity-status ${activity.status.toLowerCase()}">
            ${activity.status}
        </div>
    `;

    activityList.insertBefore(item, activityList.firstChild);

    // Remove oldest item if more than 10
    if (activityList.children.length > 10) {
        activityList.removeChild(activityList.lastChild);
    }
}

// Document Status Updates
function updateDocumentStatus(documentId, status) {
    const statusElement = document.querySelector(`#doc-${documentId} .document-status`);
    if (statusElement) {
        statusElement.className = `document-status ${status.toLowerCase()}`;
        statusElement.textContent = status;
    }
}

// Customer Risk Profile Updates
function updateCustomerRiskProfile(customerId, riskData) {
    const profileElement = document.querySelector(`#customer-${customerId}`);
    if (!profileElement) return;

    const riskScore = profileElement.querySelector('.risk-score');
    if (riskScore) {
        riskScore.dataset.score = riskData.score;
        riskScore.className = `risk-score risk-score-${riskData.level.toLowerCase()}`;
        riskScore.textContent = `${(riskData.score * 100).toFixed(1)}%`;
    }

    // Update risk factors
    const factorsList = profileElement.querySelector('.risk-factors');
    if (factorsList && riskData.factors) {
        factorsList.innerHTML = riskData.factors.map(factor => `
            <li class="risk-factor ${factor.severity.toLowerCase()}">
                ${factor.description}
            </li>
        `).join('');
    }
}

// Initialize Dashboard
document.addEventListener('DOMContentLoaded', () => {
    // Initialize risk score animations
    animateRiskScores();

    // Setup real-time updates if WebSocket is available
    if ('WebSocket' in window) {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const ws = new WebSocket(`${protocol}//${window.location.host}/ws/dashboard/`);

        ws.onmessage = function(event) {
            const data = JSON.parse(event.data);
            
            switch(data.type) {
                case 'transaction':
                    updateTransactionChart('transactionTrendChart', data.volumes);
                    addActivityItem(data);
                    break;
                case 'risk_distribution':
                    updateRiskDistribution('riskDistributionChart', data.distribution);
                    break;
                case 'document_status':
                    updateDocumentStatus(data.documentId, data.status);
                    addActivityItem(data);
                    break;
                case 'customer_risk':
                    updateCustomerRiskProfile(data.customerId, data.riskData);
                    addActivityItem(data);
                    break;
            }
        };

        ws.onerror = function(error) {
            console.error('WebSocket Error:', error);
        };

        // Heartbeat to keep connection alive
        setInterval(() => {
            if (ws.readyState === WebSocket.OPEN) {
                ws.send(JSON.stringify({ type: 'heartbeat' }));
            }
        }, 30000);
    }

    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});

// Export functions for testing
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        animateRiskScores,
        updateTransactionChart,
        updateRiskDistribution,
        addActivityItem,
        updateDocumentStatus,
        updateCustomerRiskProfile
    };
}
