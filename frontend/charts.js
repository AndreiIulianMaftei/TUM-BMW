// Chart rendering and data visualization functions

function renderAllCharts(analysis) {
    // Check if analysis has the necessary data
    if (!analysis) return;
    
    // Render Market Growth Chart (TAM/SAM/SOM)
    renderMarketGrowthChart(analysis);
    
    // Render Revenue & Volume Chart
    renderRevenueChart(analysis);
    
    // Render Cost Breakdown Chart
    renderCostChart(analysis);
    
    // Render Profitability Chart
    renderProfitabilityChart(analysis);
    
    // Render cost details sections
    renderCostDetails(analysis);
}

function renderMarketGrowthChart(analysis) {
    const canvas = document.getElementById('marketGrowthChart');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    const years = ['2024', '2025', '2026', '2027', '2028', '2029', '2030'];
    
    const datasets = [];
    
    // TAM data
    if (analysis.tam && analysis.tam.numbers) {
        datasets.push({
            label: 'TAM (Total Addressable Market)',
            data: years.map(year => analysis.tam.numbers[year] || 0),
            borderColor: '#1C69D4',
            backgroundColor: 'rgba(28, 105, 212, 0.1)',
            borderWidth: 3,
            fill: true,
            tension: 0.4
        });
    }
    
    // SAM data
    if (analysis.sam && analysis.sam.numbers) {
        datasets.push({
            label: 'SAM (Serviceable Available Market)',
            data: years.map(year => analysis.sam.numbers[year] || 0),
            borderColor: '#10B981',
            backgroundColor: 'rgba(16, 185, 129, 0.1)',
            borderWidth: 3,
            fill: true,
            tension: 0.4
        });
    }
    
    // SOM data
    if (analysis.som && analysis.som.numbers) {
        datasets.push({
            label: 'SOM (Serviceable Obtainable Market)',
            data: years.map(year => analysis.som.numbers[year] || 0),
            borderColor: '#F59E0B',
            backgroundColor: 'rgba(245, 158, 11, 0.1)',
            borderWidth: 3,
            fill: true,
            tension: 0.4
        });
    }
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: years,
            datasets: datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                    labels: {
                        usePointStyle: true,
                        padding: 20,
                        font: {
                            size: 12,
                            weight: 600
                        }
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    padding: 12,
                    titleFont: { size: 14, weight: 'bold' },
                    bodyFont: { size: 13 },
                    callbacks: {
                        label: function(context) {
                            return context.dataset.label + ': ' + formatCurrency(context.parsed.y);
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return formatCurrency(value);
                        }
                    },
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            }
        }
    });
}

function renderRevenueChart(analysis) {
    const canvas = document.getElementById('revenueChart');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    const years = ['2024', '2025', '2026', '2027', '2028', '2029', '2030'];
    
    const datasets = [];
    
    // Turnover/Revenue data
    if (analysis.turnover && analysis.turnover.numbers) {
        datasets.push({
            label: 'Revenue',
            data: years.map(year => analysis.turnover.numbers[year] || 0),
            backgroundColor: '#1C69D4',
            borderColor: '#1C69D4',
            borderWidth: 2,
            yAxisID: 'y'
        });
    }
    
    // Volume data
    if (analysis.volume && analysis.volume.numbers) {
        datasets.push({
            label: 'Volume (Units)',
            data: years.map(year => analysis.volume.numbers[year] || 0),
            backgroundColor: '#10B981',
            borderColor: '#10B981',
            borderWidth: 2,
            yAxisID: 'y1',
            type: 'line',
            fill: false,
            tension: 0.4
        });
    }
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: years,
            datasets: datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                    labels: {
                        usePointStyle: true,
                        padding: 20,
                        font: {
                            size: 12,
                            weight: 600
                        }
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    padding: 12,
                    callbacks: {
                        label: function(context) {
                            const label = context.dataset.label || '';
                            if (label.includes('Volume')) {
                                return label + ': ' + formatNumber(context.parsed.y) + ' units';
                            }
                            return label + ': ' + formatCurrency(context.parsed.y);
                        }
                    }
                }
            },
            scales: {
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return formatCurrency(value);
                        }
                    },
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    }
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    beginAtZero: true,
                    grid: {
                        drawOnChartArea: false
                    },
                    ticks: {
                        callback: function(value) {
                            return formatNumber(value);
                        }
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            }
        }
    });
}

function renderCostChart(analysis) {
    const canvas = document.getElementById('costChart');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    const years = ['2024', '2025', '2026', '2027', '2028', '2029', '2030'];
    
    const datasets = [];
    
    // Check if yearly cost breakdown exists
    if (analysis.yearly_cost_breakdown) {
        const devCosts = years.map(year => 
            analysis.yearly_cost_breakdown[year]?.one_time_development || 0
        );
        const cacCosts = years.map(year => 
            analysis.yearly_cost_breakdown[year]?.customer_acquisition || 0
        );
        const opsCosts = years.map(year => 
            analysis.yearly_cost_breakdown[year]?.distribution_operations || 0
        );
        const afterSalesCosts = years.map(year => 
            analysis.yearly_cost_breakdown[year]?.after_sales || 0
        );
        const cogsCosts = years.map(year => 
            analysis.yearly_cost_breakdown[year]?.total_cogs || 0
        );
        
        datasets.push(
            {
                label: 'Development',
                data: devCosts,
                backgroundColor: '#1C69D4',
                stack: 'costs'
            },
            {
                label: 'Customer Acquisition',
                data: cacCosts,
                backgroundColor: '#10B981',
                stack: 'costs'
            },
            {
                label: 'Operations',
                data: opsCosts,
                backgroundColor: '#F59E0B',
                stack: 'costs'
            },
            {
                label: 'After-Sales',
                data: afterSalesCosts,
                backgroundColor: '#8B5CF6',
                stack: 'costs'
            },
            {
                label: 'COGS',
                data: cogsCosts,
                backgroundColor: '#EF4444',
                stack: 'costs'
            }
        );
    }
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: years,
            datasets: datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                    labels: {
                        usePointStyle: true,
                        padding: 15,
                        font: {
                            size: 11,
                            weight: 600
                        }
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    padding: 12,
                    callbacks: {
                        label: function(context) {
                            return context.dataset.label + ': ' + formatCurrency(context.parsed.y);
                        },
                        footer: function(items) {
                            let sum = 0;
                            items.forEach(item => sum += item.parsed.y);
                            return 'Total: ' + formatCurrency(sum);
                        }
                    }
                }
            },
            scales: {
                x: {
                    stacked: true,
                    grid: {
                        display: false
                    }
                },
                y: {
                    stacked: true,
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return formatCurrency(value);
                        }
                    },
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    }
                }
            }
        }
    });
}

function renderProfitabilityChart(analysis) {
    const canvas = document.getElementById('profitabilityChart');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    const years = ['2024', '2025', '2026', '2027', '2028', '2029', '2030'];
    
    const datasets = [];
    
    // EBIT data
    if (analysis.ebit && analysis.ebit.numbers) {
        datasets.push({
            label: 'EBIT',
            data: years.map(year => analysis.ebit.numbers[year] || 0),
            borderColor: '#1C69D4',
            backgroundColor: 'rgba(28, 105, 212, 0.1)',
            borderWidth: 3,
            fill: true,
            tension: 0.4,
            yAxisID: 'y'
        });
    }
    
    // ROI data
    if (analysis.roi && analysis.roi.numbers) {
        datasets.push({
            label: 'ROI (%)',
            data: years.map(year => analysis.roi.numbers[year] || 0),
            borderColor: '#10B981',
            backgroundColor: 'rgba(16, 185, 129, 0.1)',
            borderWidth: 3,
            fill: false,
            tension: 0.4,
            yAxisID: 'y1'
        });
    }
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: years,
            datasets: datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                    labels: {
                        usePointStyle: true,
                        padding: 20,
                        font: {
                            size: 12,
                            weight: 600
                        }
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    padding: 12,
                    callbacks: {
                        label: function(context) {
                            if (context.dataset.label.includes('%')) {
                                return context.dataset.label + ': ' + context.parsed.y.toFixed(1) + '%';
                            }
                            return context.dataset.label + ': ' + formatCurrency(context.parsed.y);
                        }
                    }
                }
            },
            scales: {
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    ticks: {
                        callback: function(value) {
                            return formatCurrency(value);
                        }
                    },
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    }
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    grid: {
                        drawOnChartArea: false
                    },
                    ticks: {
                        callback: function(value) {
                            return value.toFixed(1) + '%';
                        }
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            }
        }
    });
}

function renderCostDetails(analysis) {
    // Development Costs
    if (analysis.development_costs && analysis.development_costs.length > 0) {
        const container = document.getElementById('developmentCostsContainer');
        if (container) {
            container.innerHTML = '';
            analysis.development_costs.forEach(cost => {
                container.appendChild(createCostItemElement(cost));
            });
            document.getElementById('costDetailsSection').style.display = 'block';
        }
    }
    
    // Customer Acquisition Costs
    if (analysis.customer_acquisition_costs && analysis.customer_acquisition_costs.length > 0) {
        const container = document.getElementById('cacContainer');
        if (container) {
            container.innerHTML = '';
            analysis.customer_acquisition_costs.forEach(cost => {
                container.appendChild(createCostItemElement(cost));
            });
        }
    }
    
    // Distribution & Operations Costs
    if (analysis.distribution_and_operations_costs && analysis.distribution_and_operations_costs.length > 0) {
        const container = document.getElementById('distributionCostsContainer');
        if (container) {
            container.innerHTML = '';
            analysis.distribution_and_operations_costs.forEach(cost => {
                container.appendChild(createCostItemElement(cost));
            });
        }
    }
    
    // After-Sales Costs
    if (analysis.after_sales_costs && analysis.after_sales_costs.length > 0) {
        const container = document.getElementById('afterSalesContainer');
        if (container) {
            container.innerHTML = '';
            analysis.after_sales_costs.forEach(cost => {
                container.appendChild(createCostItemElement(cost));
            });
        }
    }
    
    // COGS Items (Cost of Goods Sold) - handled separately with product_category
    if (analysis.cost_of_goods_sold && analysis.cost_of_goods_sold.length > 0) {
        const cogsSection = document.getElementById('cogsDetailsSection');
        if (!cogsSection) {
            // Create COGS section if it doesn't exist
            const detailsSection = document.getElementById('costDetailsSection');
            if (detailsSection) {
                const cogsCard = document.createElement('div');
                cogsCard.className = 'content-card';
                cogsCard.innerHTML = `
                    <div class="card-header">
                        <h3>Cost of Goods Sold (COGS) Details</h3>
                    </div>
                    <div class="card-body">
                        <div id="cogsItemsContainer"></div>
                    </div>
                `;
                detailsSection.appendChild(cogsCard);
            }
        }
        
        const cogsContainer = document.getElementById('cogsItemsContainer');
        if (cogsContainer) {
            cogsContainer.innerHTML = '';
            analysis.cost_of_goods_sold.forEach(cogsItem => {
                cogsContainer.appendChild(createCOGSItemElement(cogsItem));
            });
        }
    }
}

function createCOGSItemElement(cogsItem) {
    const div = document.createElement('div');
    div.className = 'cost-item';
    
    let html = `
        <div class="cost-item-header">
            <div class="cost-item-category">${cogsItem.product_category}</div>
            <div class="cost-item-pricing">
                <span class="cogs-price">Price: ${formatCurrency(cogsItem.price_per_item)}</span>
                <span class="cogs-cost">COGS: ${formatCurrency(cogsItem.cogs_per_item)}</span>
                <span class="cogs-margin">Margin: ${cogsItem.gross_margin_percentage.toFixed(1)}%</span>
            </div>
        </div>
        <div class="cost-item-reasoning">${cogsItem.reasoning}</div>
    `;
    
    if (cogsItem.market_comparison) {
        html += `
            <div class="cost-comparison">
                <div class="cost-comparison-title">Market Comparison</div>
                <div class="cost-comparison-details"><strong>${cogsItem.market_comparison.similar_case}</strong></div>
                <div class="cost-comparison-details">${cogsItem.market_comparison.comparison_details}</div>
        `;
        
        if (cogsItem.market_comparison.cost_figures && cogsItem.market_comparison.cost_figures.length > 0) {
            html += '<div class="cost-figures">';
            cogsItem.market_comparison.cost_figures.forEach(figure => {
                html += `
                    <div class="cost-figure-card">
                        <div class="cost-figure-company">${figure.company}</div>
                        <div class="cost-figure-product">${figure.product || figure.project}</div>
                        <div class="cost-figure-pricing">
                            Price: ${formatCurrency(figure.retail_price || figure.amount)} | 
                            COGS: ${formatCurrency(figure.cogs)} | 
                            Margin: ${figure.margin ? figure.margin.toFixed(1) + '%' : 'N/A'}
                        </div>
                        <div class="cost-figure-year">(${figure.year})</div>
                    </div>
                `;
            });
            html += '</div>';
        }
        
        if (cogsItem.market_comparison.reference_links && cogsItem.market_comparison.reference_links.length > 0) {
            html += `
                <div class="cost-sources">
                    <div class="cost-sources-label">Sources</div>
            `;
            cogsItem.market_comparison.reference_links.forEach((link, idx) => {
                html += `<a href="${link}" target="_blank" rel="noopener noreferrer" title="${link}">${link}</a>`;
            });
            html += '</div>';
        }
        
        html += '</div>';
    }
    
    div.innerHTML = html;
    return div;
}

function createCostItemElement(cost) {
    const div = document.createElement('div');
    div.className = 'cost-item-modern';
    
    let html = `
        <div class="cost-item-main">
            <div class="cost-item-info">
                <h4 class="cost-item-title">${cost.category}</h4>
                <p class="cost-item-description">${cost.reasoning}</p>
            </div>
            <div class="cost-item-value">${formatCurrency(cost.estimated_amount || cost.estimated_annual_budget)}</div>
        </div>
    `;
    
    if (cost.market_comparison) {
        html += `
            <div class="cost-comparison-modern">
                <div class="comparison-header">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                    </svg>
                    <span>Market Benchmark: ${cost.market_comparison.similar_case}</span>
                </div>
                <p class="comparison-note">${cost.market_comparison.comparison_details}</p>
        `;
        
        if (cost.market_comparison.cost_figures && cost.market_comparison.cost_figures.length > 0) {
            html += '<div class="comparison-table">';
            html += '<table><thead><tr><th>Company</th><th>Project</th><th>Cost</th><th>Year</th></tr></thead><tbody>';
            cost.market_comparison.cost_figures.forEach(figure => {
                html += `
                    <tr>
                        <td><strong>${figure.company}</strong></td>
                        <td>${figure.project}</td>
                        <td class="amount-cell">${formatCurrency(figure.amount)} ${figure.currency}</td>
                        <td>${figure.year}</td>
                    </tr>
                `;
            });
            html += '</tbody></table></div>';
        }
        
        if (cost.market_comparison.reference_links && cost.market_comparison.reference_links.length > 0) {
            html += '<div class="comparison-sources">';
            cost.market_comparison.reference_links.forEach((link, idx) => {
                const displayUrl = link.length > 50 ? link.substring(0, 47) + '...' : link;
                html += `<a href="${link}" target="_blank" rel="noopener noreferrer" title="${link}">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                    </svg>
                    ${displayUrl}
                </a>`;
            });
            html += '</div>';
        }
        
        html += '</div>';
    }
    
    div.innerHTML = html;
    return div;
}

// Helper function to format currency (defined in main.js but re-declared here for charts.js)
function formatCurrency(value) {
    if (!value && value !== 0) return 'N/A';
    return new Intl.NumberFormat('en-US', { 
        style: 'currency', 
        currency: 'EUR',
        notation: 'compact',
        maximumFractionDigits: 1
    }).format(value);
}

function formatNumber(value) {
    if (!value && value !== 0) return 'N/A';
    return new Intl.NumberFormat('en-US', { 
        notation: 'compact',
        maximumFractionDigits: 1
    }).format(value);
}
