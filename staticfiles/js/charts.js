/* Chart.js and Custom JavaScript for Stock Analysis */

// Global chart configuration
Chart.defaults.font.family = "'Segoe UI', Tahoma, Geneva, Verdana, sans-serif";
Chart.defaults.font.size = 12;
Chart.defaults.color = '#495057';

// Utility Functions
function formatCurrency(value) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 2
    }).format(value);
}

function formatNumber(value) {
    return new Intl.NumberFormat('en-US').format(value);
}

function formatPercentage(value) {
    return `${value > 0 ? '+' : ''}${value.toFixed(2)}%`;
}

// Stock Chart Creation Functions
function createPriceChart(canvasId, data) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    
    return new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.dates,
            datasets: [{
                label: 'Stock Price',
                data: data.prices,
                borderColor: '#007bff',
                backgroundColor: 'rgba(0, 123, 255, 0.1)',
                borderWidth: 3,
                fill: true,
                tension: 0.4,
                pointBackgroundColor: '#007bff',
                pointBorderColor: '#ffffff',
                pointBorderWidth: 2,
                pointRadius: 5,
                pointHoverRadius: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Stock Price History',
                    font: {
                        size: 16,
                        weight: 'bold'
                    }
                },
                legend: {
                    display: false
                }
            },
            scales: {
                x: {
                    display: true,
                    title: {
                        display: true,
                        text: 'Date'
                    },
                    grid: {
                        display: false
                    }
                },
                y: {
                    display: true,
                    title: {
                        display: true,
                        text: 'Price ($)'
                    },
                    grid: {
                        color: 'rgba(0,0,0,0.05)'
                    }
                }
            },
            interaction: {
                intersect: false,
                mode: 'index'
            },
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `Price: ${formatCurrency(context.parsed.y)}`;
                        }
                    }
                }
            }
        }
    });
}

function createVolumeChart(canvasId, data) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    
    return new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.dates,
            datasets: [{
                label: 'Volume',
                data: data.volumes,
                backgroundColor: 'rgba(40, 167, 69, 0.6)',
                borderColor: '#28a745',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Trading Volume',
                    font: {
                        size: 16,
                        weight: 'bold'
                    }
                },
                legend: {
                    display: false
                }
            },
            scales: {
                x: {
                    display: true,
                    title: {
                        display: true,
                        text: 'Date'
                    },
                    grid: {
                        display: false
                    }
                },
                y: {
                    display: true,
                    title: {
                        display: true,
                        text: 'Volume'
                    },
                    grid: {
                        color: 'rgba(0,0,0,0.05)'
                    }
                }
            },
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `Volume: ${formatNumber(context.parsed.y)}`;
                        }
                    }
                }
            }
        }
    });
}

// Portfolio Charts
function createPortfolioAllocationChart(canvasId, data) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    
    const colors = [
        '#007bff', '#28a745', '#dc3545', '#ffc107', '#17a2b8',
        '#6f42c1', '#e83e8c', '#fd7e14', '#20c997', '#6c757d'
    ];
    
    return new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: data.symbols,
            datasets: [{
                data: data.values,
                backgroundColor: colors.slice(0, data.symbols.length),
                borderColor: '#ffffff',
                borderWidth: 3,
                hoverOffset: 10
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Portfolio Allocation',
                    font: {
                        size: 16,
                        weight: 'bold'
                    }
                },
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 15,
                        usePointStyle: true
                    }
                }
            },
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((context.parsed / total) * 100).toFixed(1);
                            return `${context.label}: ${formatCurrency(context.parsed)} (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
}

// Real-time Data Functions
function updateStockPrice(symbol, price, change, changePercent) {
    const priceElement = document.querySelector(`[data-symbol="${symbol}"] .price`);
    const changeElement = document.querySelector(`[data-symbol="${symbol}"] .change`);
    
    if (priceElement) {
        priceElement.textContent = formatCurrency(price);
        priceElement.classList.add('pulse');
        setTimeout(() => priceElement.classList.remove('pulse'), 1000);
    }
    
    if (changeElement) {
        changeElement.textContent = `${change > 0 ? '+' : ''}${formatCurrency(change)} (${formatPercentage(changePercent)})`;
        changeElement.className = change >= 0 ? 'text-success' : 'text-danger';
    }
}

// Search Functions
function setupStockSearch() {
    const searchInput = document.getElementById('stockSearch');
    const searchResults = document.getElementById('searchResults');
    
    if (!searchInput || !searchResults) return;
    
    let searchTimeout;
    
    searchInput.addEventListener('input', function() {
        const query = this.value.trim();
        
        clearTimeout(searchTimeout);
        
        if (query.length < 1) {
            searchResults.style.display = 'none';
            return;
        }
        
        searchTimeout = setTimeout(() => {
            fetch(`/api/search-stocks/?q=${encodeURIComponent(query)}`)
                .then(response => response.json())
                .then(data => {
                    displaySearchResults(data.stocks || []);
                })
                .catch(error => {
                    console.error('Search error:', error);
                });
        }, 300);
    });
    
    // Hide results when clicking outside
    document.addEventListener('click', function(e) {
        if (!searchInput.contains(e.target) && !searchResults.contains(e.target)) {
            searchResults.style.display = 'none';
        }
    });
}

function displaySearchResults(stocks) {
    const searchResults = document.getElementById('searchResults');
    
    if (stocks.length === 0) {
        searchResults.innerHTML = '<div class="p-3 text-muted">No stocks found</div>';
        searchResults.style.display = 'block';
        return;
    }
    
    const html = stocks.map(stock => `
        <div class="search-result-item p-3 border-bottom" onclick="selectStock('${stock.symbol}')">
            <div class="d-flex justify-content-between">
                <div>
                    <strong>${stock.symbol}</strong>
                    <div class="text-muted small">${stock.name}</div>
                </div>
                <div class="text-end">
                    <div>${formatCurrency(stock.current_price)}</div>
                    <div class="small ${stock.price_change_percent >= 0 ? 'text-success' : 'text-danger'}">
                        ${formatPercentage(stock.price_change_percent)}
                    </div>
                </div>
            </div>
        </div>
    `).join('');
    
    searchResults.innerHTML = html;
    searchResults.style.display = 'block';
}

function selectStock(symbol) {
    window.location.href = `/stock/${symbol}/`;
}

// Animation Functions
function animateValue(element, start, end, duration = 1000) {
    const startTime = performance.now();
    const startValue = parseFloat(start) || 0;
    const endValue = parseFloat(end) || 0;
    const difference = endValue - startValue;
    
    function updateValue(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        // Easing function (ease-out)
        const easeProgress = 1 - Math.pow(1 - progress, 3);
        
        const currentValue = startValue + (difference * easeProgress);
        
        if (element.dataset.currency === 'true') {
            element.textContent = formatCurrency(currentValue);
        } else if (element.dataset.percentage === 'true') {
            element.textContent = formatPercentage(currentValue);
        } else {
            element.textContent = formatNumber(Math.round(currentValue));
        }
        
        if (progress < 1) {
            requestAnimationFrame(updateValue);
        }
    }
    
    requestAnimationFrame(updateValue);
}

// Loading Functions
function showLoading(element) {
    const originalContent = element.innerHTML;
    element.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Loading...';
    element.disabled = true;
    return originalContent;
}

function hideLoading(element, originalContent) {
    element.innerHTML = originalContent;
    element.disabled = false;
}

// Notification Functions
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.parentNode.removeChild(notification);
        }
    }, 5000);
}

// Initialize Functions
document.addEventListener('DOMContentLoaded', function() {
    // Setup search functionality
    setupStockSearch();
    
    // Animate counters on page load
    document.querySelectorAll('[data-animate="true"]').forEach(element => {
        const endValue = element.textContent;
        animateValue(element, 0, endValue, 1500);
    });
    
    // Add fade-in animation to cards
    document.querySelectorAll('.card').forEach((card, index) => {
        card.style.animationDelay = `${index * 0.1}s`;
        card.classList.add('fade-in');
    });
    
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
});

// Export functions for global use
window.StockAnalytics = {
    createPriceChart,
    createVolumeChart,
    createPortfolioAllocationChart,
    updateStockPrice,
    formatCurrency,
    formatNumber,
    formatPercentage,
    showNotification,
    animateValue
};